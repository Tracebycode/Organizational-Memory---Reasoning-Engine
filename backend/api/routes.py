from fastapi import APIRouter
from brain.orchestrator import BrainOrchestrator

router = APIRouter()

def get_brain():
    return BrainOrchestrator()

brain = get_brain()

@router.post("/store-decision")
def store(data: dict):
    return brain.store_decision(data)


@router.post("/ask")
def ask(data: dict):

    question = data.get("question")

    if not question:
        return {"error": "question is required"}

    return brain.ask_question(question)