"""Extract explicitly supplied AV scores for a simulation without changing records."""
import re
from app.academic_rules import evaluate_grades


def simulate(message):
    normalized=message.lower().replace(',', '.')
    if not any(word in normalized for word in ('se ', 'simul', 'tirar', 'tirasse', 'tirei')):
        return None
    matches=re.findall(r'\bav\s*([123])\s*(?:=|:|de|for)?\s*(\d+(?:\.\d+)?)',normalized)
    if not matches:
        return None
    grades={'AV'+n:float(v) for n,v in matches}
    if any(v>10 for v in grades.values()):
        return {'error':'Use notas entre 0 e 10 na simulação.'}
    return {'scope':'Simulação com notas fornecidas na pergunta, sem alterar as notas cadastradas.',
            'grades':grades,'result':evaluate_grades(grades),
            'attendance':'Não informada nesta simulação. Suficiência das notas não confirma aprovação por frequência.'}
