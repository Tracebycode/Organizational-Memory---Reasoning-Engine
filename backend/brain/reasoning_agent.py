import ollama


class ReasoningAgent:

    def __init__(self):
        self.model = "phi3:mini"

    def reason(self, question, context):

        prompt = f"""
Question: {question}

Context:
{context}

Explain briefly why the decision was made.
"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"num_predict": 80}
            )

            return response["message"]["content"]

        except Exception as e:
            return f"Decision reasoning:\n{context}"