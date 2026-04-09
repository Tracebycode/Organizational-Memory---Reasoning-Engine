class AnswerAgent:

    def build(self, reasoning, metadata):

        return {
            "answer": reasoning,
            "sources": metadata
        }