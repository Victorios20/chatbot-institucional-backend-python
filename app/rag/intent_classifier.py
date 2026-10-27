from dataclasses import dataclass
from unicodedata import category, normalize as unicode_normalize


@dataclass(frozen=True)
class IntentMatch:
    name: str
    score: int
    matched_keywords: list[str]


INTENT_KEYWORDS: dict[str, list[str]] = {
    "attendance": [
        "falta",
        "faltas",
        "frequencia",
        "presenca",
        "presenca parcial",
        "ausencia",
        "reprovar por falta",
        "abonar",
        "abonada",
        "chamada",
    ],
    "subjects": [
        "disciplina",
        "disciplinas",
        "materia",
        "materias",
        "cadeira",
        "professor",
        "professora",
        "carga horaria",
        "turma",
        "horario",
    ],
    "grades": [
        "nota",
        "notas",
        "media",
        "av1",
        "av2",
        "av3",
        "avaliacao",
        "prova",
        "nota unica",
        "aprovado",
        "reprovado",
    ],
    "credits": [
        "credito",
        "creditos",
        "optativa",
        "optativas",
        "horas optativas",
        "horas complementares",
        "atividade complementar",
        "atividades complementares",
    ],
    "course": [
        "curso",
        "semestre",
        "periodo",
        "matriz",
        "matriz curricular",
        "grade curricular",
        "coordenacao",
    ],
    "financial": [
        "financeiro",
        "boleto",
        "mensalidade",
        "pagamento",
        "pagar",
        "atraso",
        "divida",
        "desconto",
        "bolsa",
        "uol",
        "unifor online",
    ],
    "enrollment": [
        "matricula",
        "rematricula",
        "trancar",
        "trancamento",
        "cancelar disciplina",
        "trocar turma",
        "transferencia",
        "reitoria",
    ],
    "secretariat": [
        "secretaria",
        "reitoria",
        "protocolo",
        "servicos",
        "declaracao",
        "historico",
        "comprovante",
        "documento",
        "documentos",
        "atendimento",
        "coordenacao",
    ],
    "documents": [
        "documento",
        "documentos",
        "declaracao",
        "historico",
        "comprovante",
        "comprovante de matricula",
    ],
    "calendar": [
        "calendario",
        "data",
        "prazo",
        "quando",
        "inicio das aulas",
        "fim do semestre",
        "feriado",
        "recesso",
        "segunda chamada",
    ],
    "library": [
        "biblioteca",
        "livro",
        "emprestimo",
        "renovar livro",
        "renovacao",
        "devolucao",
        "multa biblioteca",
        "acervo",
    ],
    "internship": [
        "estagio",
        "termo de compromisso",
        "empresa",
        "supervisor",
        "horas de estagio",
        "estagio obrigatorio",
        "estagio nao obrigatorio",
    ],
    "support": [
        "suporte",
        "senha",
        "login",
        "portal",
        "acesso",
        "erro",
        "sistema",
        "email institucional",
    ],
}


INTENT_KEYWORDS.update({
    "pmg": ["pmg", "media geral", "media acumulada", "desempenho", "evolucao", "melhorou", "rendimento"],
    "history": ["historico", "conclui", "concluidas", "concluidos", "ja cursei", "reprovacoes", "repeti", "aprovadas"],
    "curriculum": ["matriz", "grade curricular", "obrigatorias", "optativas", "faltam", "falta cursar", "restam"],
    "prerequisites": ["pre requisito", "pre requisitos", "prerequisito", "prerequisitos", "antes de cursar", "liberar"],
    "offerings": ["disponiveis", "disponivel", "ofertadas", "oferta", "posso cursar", "posso me matricular", "vagas", "turmas"],
    "schedule": ["horario", "horarios", "proxima aula", "hoje", "amanha", "segunda", "terca", "quarta", "quinta", "sexta", "sala"],
    "progress": ["progresso", "quanto do curso", "quanto ja conclui", "concluir", "formar", "formatura", "creditos", "quanto falta", "porcentagem", "percentual"],
})


def normalize_text(text: str) -> str:
    decomposed = unicode_normalize("NFD", text.lower())
    without_accents = "".join(char for char in decomposed if category(char) != "Mn")
    return " ".join(without_accents.replace("-", " ").replace("_", " ").split())


def classify_intents(message: str, minimum_score: int = 1) -> list[IntentMatch]:
    normalized_message = normalize_text(message)
    matches: list[IntentMatch] = []

    for intent, keywords in INTENT_KEYWORDS.items():
        matched = []
        for keyword in keywords:
            normalized_keyword = normalize_text(keyword)
            import re
            if re.search(r"(?<!\w)" + re.escape(normalized_keyword) + r"(?!\w)", normalized_message):
                matched.append(keyword)
        if len(matched) >= minimum_score:
            matches.append(IntentMatch(name=intent, score=len(matched), matched_keywords=matched))

    if not matches:
        return [IntentMatch(name="out_of_scope", score=1, matched_keywords=[])]

    matches.sort(key=lambda item: item.score, reverse=True)
    return matches


def detect_subjects(message: str, student_context: dict) -> list[str]:
    normalized_message = normalize_text(message)
    detected: list[str] = []

    for subject in student_context.get("subjects", []):
        subject_name = subject.get("name")
        if not subject_name:
            continue
        normalized_subject = normalize_text(subject_name)
        important_tokens = [token for token in normalized_subject.split() if len(token) > 2]
        if normalized_subject in normalized_message or (important_tokens and all(token in normalized_message for token in important_tokens)):
            detected.append(subject_name)

    return detected
