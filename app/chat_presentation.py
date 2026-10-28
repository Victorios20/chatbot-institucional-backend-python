"""Presentation contracts built from computed academic records, never inferred by the UI."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AcademicAnswer:
    text: str
    presentation: dict | None = None


def grade_presentation(attempts, number):
    cards = []
    statuses = {
        'APROVADO': 'Notas e frequência suficientes',
        'PENDENTE': 'Aguardando avaliações',
        'REPROVADO_MEDIA_INICIAL': 'Média inicial abaixo do mínimo',
        'REPROVADO_REGRESSAO': 'AV3 abaixo do mínimo',
        'REPROVADO_MEDIA_FINAL': 'Média final abaixo do mínimo',
        'REPROVADO_NOTA': 'Nota abaixo do mínimo',
        'REPROVADO_FREQUENCIA': 'Frequência abaixo do mínimo',
        'NOTAS_SUFICIENTES_FREQUENCIA_PENDENTE': 'Frequência ainda não informada',
    }
    for a in attempts:
        series = a['assessment_model'] == 'AV_SERIES'
        fields = [{'label': k if k != 'NOTA_UNICA' else 'Nota única',
                   'value': number(a['grades'].get(k)) if a['grades'].get(k) is not None else 'Não lançada',
                   'pending': a['grades'].get(k) is None, 'emphasis': False}
                  for k in (('AV1', 'AV2', 'AV3') if series else ('NOTA_UNICA',))]
        if series:
            fields.append({'label': 'Média inicial', 'value': number(a['initialAverage']) if a['initialAverage'] is not None else 'A calcular',
                           'pending': a['initialAverage'] is None, 'emphasis': True})
        fields.append({'label': 'Média final', 'value': number(a['finalAverage']) if a['finalAverage'] is not None else 'A calcular',
                       'pending': a['finalAverage'] is None, 'emphasis': True})
        status = a['status']
        label = 'Aprovada' if a['closed'] and status == 'APROVADO' else statuses[status]
        tone = 'success' if status == 'APROVADO' else 'danger' if status.startswith('REPROVADO') else 'neutral'
        pending = [f['label'] for f in fields if f['pending'] and not f['emphasis']]
        note = 'Aguardando ' + ', '.join(pending) + ' para finalizar as notas.' if pending and a['finalAverage'] is None else None
        cards.append({'title': a['name'], 'subtitle': f"{a['term_id']} · {'Finalizada' if a['closed'] else 'Em andamento'}",
                      'fields': fields, 'status': {'label': label, 'tone': tone}, 'note': note})
    return {'kind': 'subject-cards', 'title': 'Suas notas', 'cards': cards}


def follow_up_suggestions(intents, detected, academic=None):
    names = set(intents)
    academic = academic or {}
    if names & {'grades', 'pmg'}:
        subjects = [a for a in academic.get('attempts', []) if not a['closed'] and a['assessment_model'] == 'AV_SERIES'
                    and a['requiredAv3'] is not None and a['grades'].get('AV3') is None]
        if detected: subjects = [a for a in subjects if a['name'] in detected]
        return ([f"Quanto preciso na AV3 de {subjects[0]['name']}?"] if subjects else []) + ['Ver meu histórico acadêmico', 'Qual é minha PMG?']
    if 'attendance' in names:
        return ['Ver minhas notas', 'Qual é minha próxima aula?']
    if 'schedule' in names:
        return ['Quais são meus horários da semana?', 'Quantas faltas ainda posso ter?']
    if names & {'offerings', 'curriculum', 'prerequisites', 'progress', 'history'}:
        return ['Quais matérias ainda faltam cursar?', 'Quais matérias posso cursar?', 'Quanto do curso já concluí?']
    return ['Ver minhas notas', 'Qual é minha próxima aula?', 'Qual é minha PMG?']
