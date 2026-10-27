"""Deterministic prototype rules; comparisons use unrounded Decimal values."""
from decimal import Decimal, ROUND_HALF_UP


def number(value):
    return None if value is None else Decimal(str(value))


def display(value):
    return None if value is None else float(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def evaluate_grades(grades, model='AV_SERIES', attendance=None, minimum_attendance=75):
    values = {key: number(value) for key, value in grades.items()}
    if any(v is not None and not 0 <= v <= 10 for v in values.values()):
        raise ValueError('Nota deve estar entre 0 e 10')
    initial = final = needed = None
    status = 'PENDENTE'
    if model == 'SINGLE_GRADE':
        final = values.get('NOTA_UNICA')
        if final is not None:
            status = 'APROVADO' if final >= 6 else 'REPROVADO_NOTA'
    else:
        av1, av2, av3 = (values.get(k) for k in ('AV1','AV2','AV3'))
        if av1 is not None and av2 is not None:
            initial = (av1 + av2) / 2
            if initial < 4:
                status, final = 'REPROVADO_MEDIA_INICIAL', initial
            else:
                needed = max(Decimal(4), Decimal(10) - initial)
                if av3 is not None:
                    final = (initial + av3) / 2
                    status = ('REPROVADO_REGRESSAO' if av3 < 4 else
                              'APROVADO' if final >= 5 else 'REPROVADO_MEDIA_FINAL')
    if attendance is not None and number(attendance) < number(minimum_attendance):
        status = 'REPROVADO_FREQUENCIA'
    elif status == 'APROVADO' and attendance is None:
        status = 'NOTAS_SUFICIENTES_FREQUENCIA_PENDENTE'
    return {'initialAverage': display(initial), 'finalAverage': display(final),
            'requiredAv3': display(needed), 'status': status,
            'finalAverageExact': str(final) if final is not None else None,
            'ruleSource': 'Regras demonstrativas do protótipo, não oficiais'}


def pmg(attempts):
    values = [number(a.get('finalAverageExact') or a['finalAverage']) for a in attempts if a.get('closed') and a.get('finalAverage') is not None]
    return {'value': display(sum(values) / len(values)) if values else None,
            'count': len(values), 'sum': display(sum(values)) if values else 0,
            'method': 'Média simples das médias finais de tentativas encerradas, incluindo reprovações e repetições; pendências excluídas.'}
