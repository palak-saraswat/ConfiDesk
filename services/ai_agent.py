from typing import TypedDict
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

load_dotenv()


class AgentState(TypedDict):
    customer_email: str
    brochure: str
    draft_reply: str
    confidence: float


BASE_DIR = Path(__file__).resolve().parent.parent
BROCHURE_PATH = BASE_DIR / "data" / "company_brochure.txt"

with open(BROCHURE_PATH, "r", encoding="utf-8") as file:
    COMPANY_BROCHURE = file.read()


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",  # or your teammate's preferred model
    temperature=0.3,
)


def generate_reply(state: AgentState):
    prompt = f"""
You are an AI customer support assistant.

Use ONLY the information in the company brochure below.

Company Brochure:
{COMPANY_BROCHURE}

Customer Email:
{state["customer_email"]}

Write a professional email reply.
"""

    try:
        response = llm.invoke(prompt)
        return {
            "draft_reply": response.content
        }

    except Exception as e:
        print(f"Gemini Error: {e}")
        return {
            "draft_reply": "",
            "confidence": 0.0
        }


def calculate_confidence(state: AgentState):
    confidence = 0.95

    return {
        "confidence": round(confidence * 10)
    }


def route_email(state: AgentState):
    if state["confidence"] >= 7:
        return "email"
    return "human_review"


builder = StateGraph(AgentState)

builder.add_node("generate_reply", generate_reply)
builder.add_node("calculate_confidence", calculate_confidence)

builder.set_entry_point("generate_reply")

builder.add_edge("generate_reply", "calculate_confidence")

builder.add_conditional_edges(
    "calculate_confidence",
    route_email,
    {
        "email": END,
        "human_review": END,
    },
)

graph = builder.compile()