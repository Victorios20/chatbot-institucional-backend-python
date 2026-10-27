from app.rag.query_planner import QueryPlan


def build_context_payload(
    message: str,
    student_context: dict,
    plan: QueryPlan,
    database_context: dict,
    document_context: list[dict],
) -> dict:
    return {
        "strategy": "RAG_HIBRIDO",
        "question": message,
        "student": {
            "registration": student_context.get("registration"),
            "fullName": student_context.get("fullName"),
            "course": student_context.get("course", {}),
        },
        "intents": [
            {
                "name": intent.name,
                "score": intent.score,
                "matchedKeywords": intent.matched_keywords,
            }
            for intent in plan.intents
        ],
        "detectedSubjects": plan.detected_subjects,
        "databaseQueries": database_context,
        "knowledgeDocuments": document_context,
        "responseRules": [
            "Use apenas os dados recuperados do banco e dos documentos.",
            "Se uma informacao nao estiver no contexto, diga que nao ha dados suficientes.",
            "Nao invente valores, datas, notas, pagamentos ou situacoes oficiais.",
            "Quando necessario, oriente o aluno a procurar o setor oficial adequado.",
        ],
    }
