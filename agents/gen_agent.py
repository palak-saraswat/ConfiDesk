import os
import json
from google import genai
from dotenv import load_dotenv

# 1. Load the environment variable configuration mapping
load_dotenv()

def run_gen_ai_agent(email_text: str):
    """
    Analyzes an incoming customer support email using Gemini, matches it against
    trusted brochure contexts, and updates the application workflow state.
    """
    # Initialize the Gemini client 
    # (It automatically reads GEMINI_API_KEY from your .env file)
    client = genai.Client()
    
    # 2. Read the trusted local brochure knowledge base document
    try:
        with open("data/company_brochure.txt", "r") as f:
            brochure_context = f.read()
    except FileNotFoundError:
        brochure_context = "Default Brand Context: Serve customers politely and efficiently."
        
    # 3. Formulate the operational prompt structure
    prompt = f"""
    You are an advanced Generative AI Customer Support Agent. Your job is to analyze the incoming customer email and dynamically draft a reply.
    
    Evaluate the request carefully based ONLY on the provided Company Context text. 
    If the answer cannot be confidently found in the context, assign a confidence score lower than 7.
    If the context fully satisfies the inquiry, assign a score of 7 or higher.
    
    Company Context:
    {brochure_context}
    
    Incoming Customer Email:
    {email_text}
    
    Return your response strictly in the following JSON format:
    {{
        "confidence_score": 7,
        "draft_reply": "your response text here",
        "status": "approved"
    }}
    """
    
    print("\n⚡ [EXECUTING GEMINI GENERATIVE AI AGENT NODE] ⚡")
    
    try:
        # 4. Generate structured JSON output directly from Gemini 2.5 Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        # Convert the raw JSON string text to a clean Python dictionary for LangGraph
        return json.loads(response.text)
        
    except Exception as e:
        print(f"❌ Gemini API Call Failed: {e}")
        return {
            "confidence_score": 0,
            "draft_reply": "System Error: Unable to process request at this moment.",
            "status": "needs_review"
        }