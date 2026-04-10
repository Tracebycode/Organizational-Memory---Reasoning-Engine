import ollama
from opentelemetry import context


class ReasoningAgent:

    def __init__(self):
        self.model = "phi3:mini"

    def reason(self, question, context):

        prompt = f"""
You are an AI that explains engineering decisions in natural language.

Context:
{context}

User question:
{question}

Write a clear natural explanation.
Do NOT return bullet points.
Do NOT list fields.
Explain like a human explaining to a teammate.
"""

        try:
            response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 120, "temperature": 0.3}
        )

            return response["message"]["content"]

        except:
            return context