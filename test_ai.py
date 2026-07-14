from services.ai_agent import graph

result = graph.invoke(
    {
        "customer_email": """
Hello,

I am interested in your AI development services.
Do you also build web applications and mobile apps?

Regards,
John
""",
        "brochure": "",
        "draft_reply": "",
        "confidence": 0.0,
    }
)

print("\nGenerated Reply:\n")
print(result["draft_reply"])

print("\nConfidence:")
print(result["confidence"])