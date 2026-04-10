import ollama


class ImpactAgent:

  def analyze(self, question, context):

    prompt = f"""
You are an AI system architect.

Context:
{context}

User question:
{question}

Explain in natural language what will happen if this decision is changed.
Describe system impact clearly.
Do not use bullet points.
"""

    response = ollama.chat(
        model="phi3:mini",
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": 120, "temperature": 0.3}
    )

    return response["message"]["content"]