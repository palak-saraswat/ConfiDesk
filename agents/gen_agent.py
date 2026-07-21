import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from services.retriever import retrieve_context

load_dotenv()

client = genai.Client()


class SupportAgentResponse(BaseModel):
    confidence_score: int = Field(
        ...,
        description="Confidence score from 1 to 10 based strictly on whether the answer is found in the provided company brochure context."
    )

    draft_reply: str = Field(
        ...,
        description="Professional email reply."
    )

    status: str = Field(
        ...,
        description="approved if confidence_score >= 7 else pending_review"
    )


def run_gen_ai_agent(email_text: str):
    """
    Generate a customer support reply using Retrieval-Augmented Generation (RAG).
    """

    # Step 1: Retrieve relevant context
    retrieved_context = retrieve_context(email_text)

    # Step 2: Build prompt
    prompt = f"""
You are ConfiDesk AI Customer Support Agent.

You are part of a Retrieval-Augmented Generation (RAG) system.

Answer ONLY using the Retrieved Context.

If the answer cannot be found in the context, politely state that the information is unavailable.

Rules:
1. Never invent information.
2. Use only the Retrieved Context.
3. If the context fully answers the customer's email, assign confidence_score between 7 and 10.
4. If the context partially answers the email, assign confidence_score between 4 and 6.
5. If the context cannot answer the email, assign confidence_score between 1 and 3.
6. If confidence_score >= 7, status must be "approved".
7. Otherwise, status must be "pending_review".
8. Return ONLY valid JSON matching the provided schema.

Retrieved Context:
{retrieved_context}

Customer Email:
{email_text}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash-lite", 
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=SupportAgentResponse,
            ),
        )

        result = json.loads(response.text)
        score = int(result["confidence_score"])
        raw_status = result["status"].strip()

        # Safety mapping
        if raw_status not in ("approved", "pending_review"):
            raw_status = "approved" if score >= 7 else "pending_review"

        return {
            "confidence_score": score,
            "draft_reply": result["draft_reply"],
            "status": raw_status,
            "retrieved_context": retrieved_context,
        }

    except Exception as e:
        print(f"Gemini Error: {e}")

        return {
            "confidence_score": 0,
            "draft_reply": "Unable to generate a response.",
            "status": "pending_review",
            "retrieved_context": retrieved_context,
        }