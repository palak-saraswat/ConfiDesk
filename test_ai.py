from agents.gen_agent import run_gen_ai_agent

email = """
Hello,

Can you tell me about your pricing plans?
"""

result = run_gen_ai_agent(email)

print(result)