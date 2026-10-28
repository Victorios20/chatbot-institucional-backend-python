"""Fast, grounded answers for structured academic questions; Gemini handles open questions."""
import re
from datetime import datetime, timedelta
from app.rag.intent_classifier import normalize_text

DAYS=['segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira','sábado','domingo']
LABELS={'APROVADO':'notas e frequência suficientes','PENDENTE':'aguardando lançamento das avaliações','REPROVADO_MEDIA_INICIAL':'reprovação pela média inicial',
 'REPROVADO_REGRESSAO':'reprovação por regressão','REPROVADO_MEDIA_FINAL':'reprovação pela média final',
 'REPROVADO_NOTA':'reprovação pela nota','REPROVADO_FREQUENCIA':'frequência abaixo do mínimo',
 'NOTAS_SUFICIENTES_FREQUENCIA_PENDENTE':'notas suficientes, frequência não informada'}

def clean_label(value):
    value = re.sub(r"(?i)\s*[—–-]\s*(?:calendário\s+)?fict[ií]ci[oa]s?", "", value)
    return re.sub(r"(?i)\b(?:fict[ií]ci[oa]s?|demonstrativ[oa]s?)\b", "", value).strip()


def fmt(v):
    return 'pendente' if v is None else f'{v:.2f}'.rstrip('0').rstrip('.').replace('.',',')


def structured_answer(message,rag,student):
    data=rag.get('databaseQueries',{}).get('academic',{}).get('data',{})
    names={i['name'] for i in rag.get('intents',[])}
    detected=rag.get('detectedSubjects',[])
    text=normalize_text(message)
    # Invitations to explain concepts are answered using the knowledge documents by Gemini.
    conceptual=any(x in text for x in ('como funciona','explique','o que e','qual a regra','como e calculad'))
    simulation=data.get('simulation')
    if simulation:
        if simulation.get('error'):return simulation['error']
        r=simulation['result']
        return (f"Na simulação: média inicial {fmt(r['initialAverage'])}; média final {fmt(r['finalAverage'])}. "
                f"Resultado pelas notas: {LABELS[r['status']]}. "
                +(f"AV3 necessária: {fmt(r['requiredAv3'])}. " if r['status']=='PENDENTE' and r['requiredAv3'] is not None else '')
                +"A frequência também precisa ser suficiente. Nenhuma nota cadastrada foi alterada.")
    prefix=''
    if 'calendar' in names and 'offerings' not in names and any(x in text for x in ('quando','calendario','data','prazo')):
        return grounded_fallback(message,rag)
    if 'complementar' in text and any(x in text for x in ('quantas', 'quantos', 'quanto', 'faltam')) and not conceptual:
        p=data.get('progress',{})
        if p.get('complementaryHoursRequired') is None:
            return prefix+'não há requisito de horas complementares cadastrado para confirmar o saldo.'
        return (prefix+f"você tem {p['complementaryHoursApproved']} horas complementares aprovadas de {p['complementaryHoursRequired']} exigidas. "
                f"Faltam {p['complementaryHoursRemaining']} horas. Atividades pendentes ou rejeitadas não entram nessa soma.")
    if 'optativ' in text and any(x in text for x in ('quantos', 'quantas', 'quanto')) and not conceptual:
        course=student.get('course',{})
        required,completed=course.get('requiredOptionalCredits'),course.get('completedOptionalCredits')
        if required is not None and completed is not None:
            return prefix+f"seu perfil registra {completed} créditos optativos concluídos de {required} exigidos; faltam {max(0,required-completed)} créditos optativos. Esse saldo considera os requisitos de créditos optativos cadastrados no seu curso."
    if 'pmg' in names and not conceptual:
        p=data['pmg']
        if p['value'] is None:return prefix+'você ainda não possui PMG: nenhuma disciplina finalizada possui média final registrada.'
        result=prefix+f"sua PMG é {fmt(p['value'])}: soma {fmt(p['sum'])} ÷ {p['count']} disciplinas finalizadas, com aprovação ou reprovação. Se você cursou uma matéria novamente, cada resultado final entra no cálculo. Disciplinas em andamento ou sem média final ficam fora."
        if any(x in text for x in ('evolucao','semestre','melhor','periodo')):
            periods=[p for p in data['pmgByTerm'] if p['value'] is not None]
            result+='\nMédias por período: '+ '; '.join(f"{p['term']}: {fmt(p['value'])}" for p in periods)+'.'
            if len(periods)>1:
                change=periods[-1]['value']-periods[-2]['value']
                result+=f" Variação entre os dois últimos: {fmt(change)} ponto(s)."
        return result
    if 'grades' in names and 'history' not in names and not ('calendar' in names and any(x in text for x in ('quando','data','prazo'))) and not conceptual and not any(x in text for x in ('regra','formula','significa')):
        attempts=data.get('attempts',[])
        if not attempts:return prefix+'não há avaliações cadastradas para essa disciplina.'
        current=[a for a in attempts if not a['closed']]
        attempts=current or attempts
        if any(x in text for x in ('preciso','necessari','tirar','tirasse')):
            if not detected:return 'De qual disciplina você quer saber a nota necessária na AV3?'
            a=attempts[-1];r=a['requiredAv3']
            if a['status']=='REPROVADO_MEDIA_INICIAL':return prefix+f"a média inicial em {a['name']} é {fmt(a['initialAverage'])}, abaixo de 4. A regra prevê reprovação direta; a AV3 não recupera esse resultado."
            if a['assessment_model']=='SINGLE_GRADE':return prefix+f"{a['name']} é de nota única, com mínimo 6 e frequência mínima; não tem AV3."
            if r is None:return prefix+f"ainda faltam AV1 ou AV2 de {a['name']}; não é possível calcular a AV3 necessária."
            return prefix+f"você precisa de pelo menos {fmt(r)} na AV3 de {a['name']} (média inicial {fmt(a['initialAverage'])}). A AV3 precisa ser pelo menos 4, a média final pelo menos 5 e a frequência mínima deve ser cumprida."
        lines=[]
        for a in attempts:
            g=' · '.join(f"{'Nota única' if k=='NOTA_UNICA' else k}: {fmt(v) if v is not None else 'ainda não lançada'}" for k,v in a['grades'].items())
            suffix=f"\n  Média inicial: {fmt(a['initialAverage'])}" if a['assessment_model']=='AV_SERIES' else ''
            suffix+=f". Média final: {fmt(a['finalAverage'])}." if a['finalAverage'] is not None else "\n  A média final será calculada quando todas as notas necessárias forem lançadas."
            if a['status'] != 'PENDENTE': suffix+=f" Situação: {LABELS[a['status']]}."
            lines.append(f"• {a['name']} ({a['term_id']}, {'finalizada' if a['closed'] else 'em andamento'}): {g}{suffix}")
        return 'Suas notas:\n'+'\n'.join(lines)
    if 'prerequisites' in names and not conceptual:
        subjects=[s for s in data.get('curriculum',[]) if s['name'] in detected]
        if not subjects:return 'De qual disciplina você quer consultar os pré-requisitos?'
        lines=[]
        completed={s['name'] for s in data['curriculum'] if s['completed']}
        for s in subjects:
            req=s['prerequisites']
            pending=[name for name in req if name not in completed]
            lines.append(s['name']+': '+(', '.join(req) if req else 'nenhum pré-requisito cadastrado')+'.'+(' Pendentes: '+', '.join(pending)+'.' if pending else ' Requisitos cadastrados atendidos.'))
        return 'Pré-requisitos:\n'+'\n'.join(lines)
    if 'offerings' in names and not conceptual:
        term_match=re.search(r'\b(20\d{2})[./]([12])\b',text)
        term='.'.join(term_match.groups()) if term_match else data.get('currentTerm')
        if not term_match and term and any(x in text for x in ('proximo semestre','proximo periodo')):
            year,part=term.split('.')
            term=f'{int(year)+(part=="2")}.{1 if part=="2" else 2}'
        offers=[o for o in data.get('offerings',[]) if o['term_id']==term]
        if detected:offers=[o for o in offers if o['name'] in detected]
        if not offers:return f'Não há oferta cadastrada para {term or "o período solicitado"}.'
        eligible=any(x in text for x in ('posso','apto','elegiv','liberad'))
        if eligible:
            available=[o for o in offers if o['canEnrollInPrototype']]
            if not available:
                reasons=sorted({reason for o in offers for reason in o['restrictions']} | {'Choque de horários' for o in offers if o['scheduleConflicts']})
                return f'Em {term}, nenhuma das turmas consultadas atende a todos os critérios de matrícula cadastrados. Motivos: '+', '.join(reasons)+'.'
            return f'Turmas que você pode cursar em {term}:\n'+'\n'.join(f"• {o['name']} — turma {o['class_code']}, {o['seats_available']} vagas." for o in available)+'\nPré-requisitos, vagas, conclusão anterior e conflitos cadastrados foram verificados. Isso não efetua nem garante matrícula oficial.'
        return f'Disciplinas disponíveis em {term}:\n'+'\n'.join(f"• {o['name']} — turma {o['class_code']}, {o['seats_available']} vagas, {o['teacher']}, {o['room']}." for o in offers)+'\nUma disciplina ofertada pode ter restrições de matrícula.'
    if 'schedule' in names and not conceptual:
        if 'proxima' in text:
            c=data.get('nextClass')
            if not c:return prefix+'não há próxima aula cadastrada no período atual.'
            date=datetime.fromisoformat(c['startsOn'])
            return prefix+f"sua próxima aula é {c['name']}, {DAYS[c['weekday']-1]} ({date:%d/%m}), das {c['starts_at'][:5]} às {c['ends_at'][:5]}, com {c['teacher']}, na sala {c['room']} — bloco {c['room'][0]}."
        schedule=data.get('schedule',[])
        if detected:schedule=[s for s in schedule if s['name'] in detected]
        day=None
        now=datetime.fromisoformat(data['currentDate'])
        if 'hoje' in text:day=now.isoweekday()
        elif 'amanha' in text:day=(now+timedelta(days=1)).isoweekday()
        else:
            for i,name in enumerate(DAYS,1):
                if normalize_text(name).split()[0] in text:day=i;break
        if day:schedule=[s for s in schedule if s['weekday']==day]
        if not schedule:return prefix+'não há aula cadastrada para esse dia ou disciplina no período atual.'
        return 'Seu horário no período atual:\n'+'\n'.join(f"• {s['name']}: {DAYS[s['weekday']-1]}, {s['starts_at'][:5]}–{s['ends_at'][:5]}, {s['room']}, {s['teacher']}." for s in sorted(schedule,key=lambda s:(s['weekday'],s['starts_at'])))
    if 'history' in names and not conceptual and not ('progress' in names and 'quanto' in text):
        attempts=data.get('attempts',[])
        if detected:attempts=[a for a in attempts if a['name'] in detected]
        closed=[a for a in attempts if a['closed']]
        if not closed:
            return prefix+('a disciplina está em curso e ainda não consta como concluída.' if attempts else 'não há disciplinas finalizadas para essa consulta.')
        if any(x in text for x in ('conclu','aprovad')):closed=[a for a in closed if a['status']=='APROVADO']
        if 'reprov' in text:closed=[a for a in closed if a['status'].startswith('REPROVADO')]
        if not closed:return prefix+'não há disciplinas finalizadas com essa situação.'
        return 'Seu histórico acadêmico:\n'+'\n'.join(f"• {a['term_id']} — {a['name']}: média {fmt(a['finalAverage'])}, {LABELS[a['status']]} (finalizada)." for a in closed)
    if 'curriculum' in names and not conceptual:
        subjects=data.get('curriculum',[])
        if 'optativ' in text:subjects=[s for s in subjects if s['category']=='OPTIONAL']
        if any(x in text for x in ('faltam','restam','falta cursar','pendentes')):subjects=[s for s in subjects if not s['completed']]
        return 'Matriz curricular cadastrada:\n'+'\n'.join(f"• {s['name']}: {'optativa' if s['category']=='OPTIONAL' else 'obrigatória'}, {s['credits']} créditos, {s['workload_hours']}h, {'concluída' if s['completed'] else 'em curso' if s['inProgress'] else 'não concluída'}." for s in subjects)
    if 'progress' in names and not conceptual and not any(x in text for x in ('complementar','optativ')):
        p=data['progress']
        return (f"Na matriz curricular cadastrada, você concluiu {fmt(p['percentage'])}%: "
                f"{p['completedHours']} de {p['totalHours']} horas e {p['completedCredits']} de {p['totalCredits']} créditos. "
                f"Faltam {p['remainingHours']} horas e {p['remainingCredits']} créditos de disciplinas nessa matriz. "
                "A conclusão do curso também depende dos demais requisitos acadêmicos.")
    return None


def grounded_fallback(message, rag):
    """Only retrieved facts and verbatim institutional guidance; never invent a replacement answer."""
    rag=rag or {}
    data=rag.get('databaseQueries',{}).get('academic',{}).get('data',{})
    names={i['name'] for i in rag.get('intents',[])}
    text=normalize_text(message)
    if 'grades' in names and data.get('gradeRules') and not ('calendar' in names and any(x in text for x in ('quando','data','prazo'))):
        return ('A média inicial é (AV1 + AV2) ÷ 2. Abaixo de 4, há reprovação direta. '
                'Com média inicial de pelo menos 4, a AV3 é obrigatória e precisa ser pelo menos 4. '
                'A média final (média inicial + AV3) ÷ 2 deve ser pelo menos 5, além da frequência mínima da disciplina. '
                'Disciplinas cadastradas como nota única exigem 6 e frequência mínima.')
    queries=rag.get('databaseQueries',{})
    if 'calendar' in names and queries.get('academic_events',{}).get('available'):
        events=queries['academic_events']['data']
        if 'av3' in text:events=[e for e in events if 'av3' in normalize_text(e['title'])]
        elif any(x in text for x in ('matricula','rematricula')):events=[e for e in events if e['event_type']=='ENROLLMENT']
        current=data.get('currentDate','')[:10]
        upcoming=[e for e in events if str(e['ends_on'])>=current]
        events=upcoming or events
        if events:
            return 'Calendário acadêmico:\n'+'\n'.join(f"• {clean_label(e['title'])}: {datetime.fromisoformat(str(e['starts_on'])):%d/%m/%Y} a {datetime.fromisoformat(str(e['ends_on'])):%d/%m/%Y}." for e in events[:4])
    if 'financial' in names:
        records=queries.get('financial_records',{}).get('data',[])
        benefits=queries.get('student_benefits',{}).get('data',[])
        statuses={'PAID':'paga','OPEN':'em aberto','OVERDUE':'em atraso','NEGOTIATION':'em negociação'}
        lines=[f"• {str(r['reference_month'])[:7]}: R$ {r['amount']:.2f}, {statuses.get(r['status'],r['status'])}; vencimento {r['due_date']}." for r in records]
        lines.extend(f"• Benefício {clean_label(b['benefit_type'].replace('_',' ').lower())}: {fmt(b['percentage'])}%, situação {dict(ACTIVE='ativo',SUSPENDED='suspenso',ENDED='encerrado').get(b['status'],b['status'])}." for b in benefits)
        if lines:return 'Seus registros financeiros:\n'+'\n'.join(lines)+'\nO assistente não emite boletos nem altera pagamentos.'
    docs=[d for d in rag.get('knowledgeDocuments',[]) if d.get('available') and d.get('sections')]
    if docs:
        sections=docs[0]['sections']
        excerpt=clean_label('\n\n'.join(sections))
        if len(excerpt)>1500:excerpt=excerpt[:1500].rsplit(' ',1)[0]+'…'
        return 'Não consegui elaborar uma explicação personalizada agora. Nas orientações cadastradas consta:\n\n'+excerpt
    return 'Não há informação suficiente nas orientações recuperadas para confirmar essa resposta. Reformule sua dúvida acadêmica ou consulte o setor responsável.'


def attendance_answer(message, student, detected=None):
    """Answer factual attendance questions without generating an LLM response."""
    text = normalize_text(message)
    if any(word in text for word in ('abonar', 'abonada', 'corrigir', 'divergencia', 'como funciona', 'explique', 'o que e')):
        return None
    if not any(word in text for word in ('quantas', 'quantos', 'quanto', 'posso', 'minha', 'minhas', 'tenho', 'frequencia atual', 'limite')):
        return None
    subjects = student.get('subjects', [])
    if detected:
        subjects = [s for s in subjects if s['name'] in detected]
    if not subjects:
        return 'Não há dados de frequência cadastrados para essa disciplina.'
    lines = []
    for s in subjects:
        remaining = s['remainingAbsencesHours']
        limit = s['maximumAbsencesHours']
        used = s['absencesInHours']
        detail = f"ainda pode faltar {fmt(remaining)} h" if used <= limit else f"o limite foi ultrapassado em {fmt(used-limit)} h"
        lines.append(f"• {s['name']}: {fmt(used)} h de faltas registradas; limite de {fmt(limit)} h. Você {detail}. Frequência atual: {fmt(s['currentAttendancePercentage'])}% (mínimo {fmt(s['minimumAttendancePercentage'])}%).")
    return 'Sua frequência por disciplina:\n' + '\n'.join(lines) + '\nOs limites estão em horas de falta, não em dias de aula.'
