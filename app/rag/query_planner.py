from dataclasses import dataclass

from app.rag.intent_classifier import IntentMatch


@dataclass(frozen=True)
class QueryPlan:
    intents: list[IntentMatch]
    detected_subjects: list[str]
    database_queries: list[str]
    documents: list[str]


QUERY_BY_INTENT: dict[str, list[str]] = {
    "attendance": ["student_profile", "subject_attendance", "detailed_attendance"],
    "subjects": ["student_profile", "student_subjects"],
    "grades": ["student_profile"],
    "credits": ["student_profile", "curriculum_rules", "complementary_activities"],
    "course": ["student_profile", "curriculum_rules"],
    "financial": ["student_profile", "financial_records", "student_benefits"],
    "enrollment": ["student_profile", "curriculum_rules"],
    "secretariat": ["student_profile"],
    "documents": ["student_profile"],
    "calendar": ["academic_events"],
    "library": [],
    "internship": ["student_profile", "internships", "complementary_activities"],
    "support": ["student_profile"],
    "out_of_scope": [],
}


DOCUMENTS_BY_INTENT: dict[str, list[str]] = {
    "attendance": ["frequencia.md"],
    "subjects": ["disciplinas.md"],
    "grades": ["notas.md"],
    "credits": ["creditos.md", "curso.md"],
    "course": ["curso.md"],
    "financial": ["financeiro.md"],
    "enrollment": ["matricula.md"],
    "secretariat": ["secretaria.md"],
    "documents": ["documentos.md", "secretaria.md"],
    "calendar": ["calendario.md"],
    "library": ["biblioteca.md"],
    "internship": ["estagio.md", "curso.md"],
    "support": ["suporte.md"],
    "out_of_scope": ["fallback.md"],
}

for intent in ("pmg", "history", "curriculum", "prerequisites", "offerings", "schedule", "progress"):
    QUERY_BY_INTENT[intent] = ["student_profile"]
    DOCUMENTS_BY_INTENT[intent] = [{"pmg":"pmg.md", "history":"historico.md", "curriculum":"matriz.md", "prerequisites":"prerequisitos.md", "offerings":"oferta.md", "schedule":"horarios.md", "progress":"progresso.md"}[intent]]


def _unique(items: list[str]) -> list[str]:
    seen = set()
    unique_items = []
    for item in items:
        if item not in seen:
            unique_items.append(item)
            seen.add(item)
    return unique_items


def build_query_plan(intents: list[IntentMatch], detected_subjects: list[str]) -> QueryPlan:
    query_names: list[str] = []
    document_names: list[str] = []

    for intent in intents:
        query_names.extend(QUERY_BY_INTENT.get(intent.name, []))
        document_names.extend(DOCUMENTS_BY_INTENT.get(intent.name, []))

    return QueryPlan(
        intents=intents,
        detected_subjects=detected_subjects,
        database_queries=_unique(query_names),
        documents=_unique(document_names),
    )
