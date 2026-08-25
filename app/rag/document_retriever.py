from pathlib import Path

from app.rag.intent_classifier import INTENT_KEYWORDS, normalize_text


KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"


def split_sections(content: str) -> list[str]:
    sections: list[str] = []
    current: list[str] = []

    for line in content.splitlines():
        if line.startswith("#") and current:
            sections.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)

    if current:
        sections.append("\n".join(current).strip())
    return [section for section in sections if section]


def score_section(section: str, message: str, intent_names: list[str]) -> int:
    normalized_section = normalize_text(section)
    normalized_message = normalize_text(message)
    message_terms = [term for term in normalized_message.split() if len(term) > 3]

    score = sum(1 for term in message_terms if term in normalized_section)
    for intent in intent_names:
        for keyword in INTENT_KEYWORDS.get(intent, []):
            if normalize_text(keyword) in normalized_section:
                score += 1
    return score


def retrieve_document_context(document_names: list[str], message: str, intent_names: list[str]) -> list[dict]:
    retrieved = []

    for document_name in document_names:
        path = KNOWLEDGE_DIR / document_name
        if not path.exists():
            retrieved.append(
                {
                    "document": document_name,
                    "available": False,
                    "sections": [],
                    "note": "Documento de conhecimento nao encontrado.",
                }
            )
            continue

        content = path.read_text(encoding="utf-8")
        sections = split_sections(content)
        ranked_sections = sorted(
            sections,
            key=lambda section: score_section(section, message, intent_names),
            reverse=True,
        )
        selected_sections = ranked_sections[:2] if ranked_sections else [content[:1200]]

        retrieved.append(
            {
                "document": document_name,
                "available": True,
                "sections": selected_sections,
            }
        )

    return retrieved
