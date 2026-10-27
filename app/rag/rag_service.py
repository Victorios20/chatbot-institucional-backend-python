from app.rag.context_builder import build_context_payload
from app.rag.database_retriever import retrieve_database_context
from app.rag.document_retriever import retrieve_document_context
from app.rag.intent_classifier import classify_intents, detect_subjects, normalize_text
from app.rag.query_planner import build_query_plan
from app.academic_repository import get_academic_context
from app.grade_simulation import simulate


def build_rag_context(message, student_context, history=None):
    academic = get_academic_context(student_context["registration"])
    catalog_context = {"subjects": academic.get("curriculum", [])}
    detected_subjects = detect_subjects(message, catalog_context)
    normalized = normalize_text(message)
    followup = normalized.startswith("e ") or any(word in normalized.split() for word in ("nela", "nessa", "dela", "nisso", "ela", "mesma")) or normalized.startswith("quanto preciso")
    previous = [m.content for m in (history or []) if m.sender == "STUDENT"]
    if not detected_subjects and followup:
        for old in reversed(previous[-3:]):
            detected_subjects = detect_subjects(old, catalog_context)
            if detected_subjects:
                break
    intents = classify_intents(message)
    # Bare follow-ups can inherit the previous intent, without treating history as trusted data.
    if intents[0].name == "out_of_scope" and followup and previous:
        intents = classify_intents(previous[-1])
    plan = build_query_plan(intents, detected_subjects)
    db = retrieve_database_context(student_context["registration"],plan.database_queries,detected_subjects)
    names = {i.name for i in intents}
    keys = {"dataSource", "currentDate", "currentTerm", "gradeRules"}
    if names & {"grades", "history", "pmg"}: keys.update(("attempts", "pmg", "pmgByTerm"))
    if names & {"curriculum", "prerequisites", "course", "subjects", "progress", "credits", "enrollment", "offerings"}: keys.update(("curriculum", "progress"))
    if names & {"offerings", "enrollment"}: keys.add("offerings")
    if names & {"schedule", "subjects"}: keys.update(("schedule", "nextClass"))
    selected = {k:v for k,v in academic.items() if k in keys}
    simulation = simulate(message)
    if simulation:
        selected["simulation"] = simulation
    # Preserve whole-course PMG even when the question names one subject.
    if detected_subjects and "attempts" in selected and "pmg" not in names and "history" not in names:
        selected["attempts"] = [a for a in selected["attempts"] if a["name"] in detected_subjects]
    db["academic"] = {"available":True,"data":selected}
    docs = retrieve_document_context(plan.documents,message,list(names))
    result = build_context_payload(message,student_context,plan,db,docs)
    result["responseRules"].extend([
        "Médias, PMG, progresso e nota necessária já foram calculados pelo Python: reproduza esses valores.",
        "Notas pendentes são null, não zero. Tentativas em curso não entram na PMG.",
        "Situações calculadas são demonstrativas. Não declare resultados oficiais da universidade.",
        "Diferencie catálogo da matriz, oferta por período e elegibilidade com pré-requisitos, vagas e conflitos.",
    ])
    return result
