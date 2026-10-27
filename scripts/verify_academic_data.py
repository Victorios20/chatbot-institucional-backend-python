"""Read-only integration validation. Run with DATABASE_URL pointing to QA first."""
from app.database import get_connection
from app.academic_repository import get_academic_context
from app.rag.rag_service import build_rag_context
from app.student_repository import get_student_context_by_registration
from app.session_store import ChatMessage
from datetime import datetime, UTC

QUESTIONS = ['Quais minhas notas AV1 AV2 AV3?', 'Qual minha PMG e evolução?',
 'Quais disciplinas já concluí?', 'Quais matérias faltam na matriz?',
 'Quais pré-requisitos de Inteligência Artificial?', 'Quais matérias estão disponíveis?',
 'Qual minha próxima aula?', 'Qual meu progresso e créditos?', 'Quando é a AV3?',
 'Tenho bolsa e boletos?', 'Quantas horas complementares tenho?', 'Como funciona o estágio?']


def verify():
    with get_connection() as conn:
        registrations=[r['registration'] for r in conn.execute('SELECT registration FROM students ORDER BY registration').fetchall()]
    for registration in registrations:
        c=get_academic_context(registration)
        assert c['curriculum'] and c['offerings'],registration
        assert c['progress']['completedHours']<=c['progress']['totalHours']
        context=get_student_context_by_registration(registration)
        for question in QUESTIONS if registration == '2310000' else []:
            rag=build_rag_context(question,context)
            unavailable=[k for k,v in rag['databaseQueries'].items() if not v['available']]
            assert not unavailable,(registration,question,unavailable)
            assert all(d['available'] for d in rag['knowledgeDocuments'])
        print(registration, 'PMG', c['pmg']['value'], 'attempts',len(c['attempts']),'OK',flush=True)
    context=get_student_context_by_registration('2310000')
    history=[ChatMessage('STUDENT','Quais minhas notas em Banco de Dados?',datetime.now(UTC))]
    follow=build_rag_context('E quanto preciso tirar na AV3 nela?',context,history)
    assert follow['detectedSubjects']==['Banco de Dados']
    attempts=follow['databaseQueries']['academic']['data']['attempts']
    assert all(a['name']=='Banco de Dados' for a in attempts)
    assert attempts[0]['requiredAv3']==4
    print('Follow-up, scope, documents and all queries OK',flush=True)

if __name__=='__main__': verify()
