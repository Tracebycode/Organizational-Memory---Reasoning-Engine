from brain.vector_store import VectorStore
from brain.reasoning_agent import ReasoningAgent
from brain.retrieval_agent import RetrievalAgent
from brain.answer_agent import AnswerAgent


class BrainOrchestrator:

    def __init__(self):
        self.memory = VectorStore()
        self.reasoner = ReasoningAgent()
        self.retriever = RetrievalAgent()
        self.answer_agent = AnswerAgent()

    def store_decision(self, data):

        decision = data.get("decision")
        reason = data.get("reason")
        source = data.get("source", "manual")

        text = f"""
Decision: {decision}
Reason: {reason}
Source: {source}
"""

        metadata = {
            "decision": decision,
            "reason": reason,
            "source": source
        }

        self.memory.store(text, metadata)

        return {"status": "stored"}

    def ask_question(self, question):

        context, metadata = self.retriever.retrieve(
            self.memory,
            question
        )

        if not context:
            return {
                "answer": "No decision found.",
                "sources": []
            }

        reasoning = self.reasoner.reason(
            question,
            context
        )

        return self.answer_agent.build(
            reasoning,
            metadata
        )