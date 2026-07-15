import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def run_gen_ai_agent(email_text: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Read the trusted context/brochure document
    try:
        with open("data/company_brochure.txt", "r") as f:
            brochure_context = f.read()
    except FileNotFoundError:
        brochure_context = "Default Brand Context: Serve customers politely and efficiently."

    # Using Generative AI to understand intent and draft replies dynamically
    prompt = f"""
    You are an advanced Generative AI Customer Support Agent. Your job is to analyze the incoming customer email and dynamically synthesize an accurate draft reply using the provided company context.
    
    Evaluate the request carefully. If the generation requires information outside the provided text, assign a low confidence score (< 7).
    
    Company Context:
    {brochure_context}
    
    Customer Email:
    {email_text}
    
    Respond STRICTLY in this layout format:
    CONFIDENCE_SCORE: [Provide an integer score from 1 to 10]
    DRAFT_REPLY: [Your generative response here, or state "Escalation required" if score is low]
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7 # Slight temperature allowed for creative generative synthesis
    )
    
    output = response.choices[0].message.content
    
    try:
        lines = output.strip().split("\n")
        score = int(lines[0].replace("CONFIDENCE_SCORE:", "").strip())
        draft = lines[1].replace("DRAFT_REPLY:", "").strip()
    except Exception:
        score = 5
        draft = "Escalation required due to output formatting variations."
        
    return {"confidence_score": score, "draft_reply": draft}