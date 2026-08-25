from app.rag.context_builder import build_context_payload
from app.rag.database_retriever import retrieve_database_context
from app.rag.document_retriever import retrieve_document_context
from app.rag.intent_classifier import classify_intents, detect_subjects
from app.rag.query_planner import build_query_plan


def build_rag_context(message: str, student_context: dict) -> dict:
    intents = classify_intents(message)
    detected_subjects = detect_subjects(message, student_context)
    plan = build_query_plan(intents, detected_subjects)
    intent_names = [intent.name for intent in intents]

    database_context = retrieve_database_context(
        registration=student_context["registration"],
        query_names=plan.database_queries,
        detected_subjects=detected_subjects,
    )
    document_context = retrieve_document_context(plan.documents, message, intent_names)

    return build_context_payload(
        message=message,
        student_context=student_context,
        plan=plan,
        database_context=database_context,
        document_context=document_context,
    )
