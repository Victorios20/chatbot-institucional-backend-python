import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4
from pydantic import ValidationError
from app.academic_answers import structured_result
from app.academic_rules import evaluate_grades
from app.chat_presentation import follow_up_suggestions
from app.schemas import ChatRequest, ChatResponse, ChatFeedbackRequest
from app import chatbot_service as service


class ChatExperienceTest(unittest.TestCase):
    def rag(self, grades=None, closed=False):
        grades = grades or {'AV1': 6, 'AV2': 7, 'AV3': None}
        attempt = {'name':'Banco de Dados', 'term_id':'2026.2', 'closed':closed,
                   'assessment_model':'AV_SERIES', 'grades':grades, **evaluate_grades(grades, attendance=80)}
        return {'intents':[{'name':'grades'}], 'detectedSubjects':[], 'databaseQueries':{'academic':{'data':{'attempts':[attempt]}}}}

    def test_pending_grades_are_cards_not_zero(self):
        result=structured_result('Quais são minhas notas?', self.rag(), {})
        card=result.presentation['cards'][0]
        self.assertEqual(card['fields'][2]['label'],'AV3')
        self.assertEqual(card['fields'][2]['value'],'Não lançada')
        self.assertTrue(card['fields'][2]['pending'])
        self.assertEqual(card['fields'][3]['value'],'6,5')
        self.assertEqual(card['fields'][4]['value'],'A calcular')
        ChatResponse(response=result.text,messageId=uuid4(),presentation=result.presentation)

    def test_closed_approved_card_is_distinct_from_in_progress(self):
        result=structured_result('Minhas notas',self.rag({'AV1':8,'AV2':8,'AV3':8},closed=True),{})
        self.assertEqual(result.presentation['cards'][0]['status']['label'],'Aprovada')
        result=structured_result('Minhas notas',self.rag({'AV1':8,'AV2':8,'AV3':8}),{})
        self.assertNotEqual(result.presentation['cards'][0]['status']['label'],'Aprovada')

    def test_failure_does_not_get_success_color(self):
        result=structured_result('Minhas notas',self.rag({'AV1':3,'AV2':3,'AV3':None}),{})
        self.assertEqual(result.presentation['cards'][0]['status']['tone'],'danger')

    def test_follow_up_names_actual_subject(self):
        data=self.rag()['databaseQueries']['academic']['data']
        self.assertIn('Quanto preciso na AV3 de Banco de Dados?',follow_up_suggestions({'grades'},[],data))
        self.assertFalse(any('AV3' in q for q in follow_up_suggestions({'grades'},[],{'attempts':[]})))

    def test_simulation_and_concepts_do_not_become_grade_cards(self):
        rag=self.rag()
        self.assertIsNone(structured_result('Explique como funciona a média',rag,{}))
        result=structured_result('Quanto preciso na AV3?',rag,{})
        self.assertIsNone(result.presentation)

    def test_cached_answer_does_not_call_model_or_duplicate_history(self):
        request=ChatRequest(sessionId='session',message='Minhas notas',requestId=uuid4())
        reply={'response':'Resposta salva','messageId':str(uuid4())}
        session=SimpleNamespace(student_context={'registration':'2310000'},history=[])
        with patch.object(service.session_store,'get',return_value=session), patch.object(service,'find_chat_response',return_value=reply), patch.object(service,'build_rag_context') as rag, patch.object(service,'generate_chat_answer') as model, patch.object(service.session_store,'add_message') as history:
            self.assertEqual(service.send_message(request),reply)
            rag.assert_not_called(); model.assert_not_called(); history.assert_not_called()

    def test_profile_exposes_only_identity(self):
        session=SimpleNamespace(student_context={'registration':'2310000','fullName':'Aluno','course':{'name':'Computação','currentSemester':4},'subjects':[{'grades':'private'}]})
        with patch.object(service.session_store,'get',return_value=session):
            result=service.get_chat_session('session')
        self.assertEqual(result,{'student':{'fullName':'Aluno','courseName':'Computação','semester':4}})

    def test_feedback_uses_session_identity(self):
        request=ChatFeedbackRequest(sessionId='session',messageId=uuid4(),rating='helpful')
        session=SimpleNamespace(student_context={'registration':'2310000'})
        with patch.object(service.session_store,'get',return_value=session), patch.object(service,'save_feedback',return_value={'rating':'helpful'}) as save:
            service.submit_feedback(request)
            save.assert_called_once_with('2310000',request.messageId,'helpful')

    def test_invalid_rating_id_and_message_are_rejected(self):
        for value in ['', 'bad', 1]:
            with self.assertRaises(ValidationError): ChatFeedbackRequest(sessionId='session',messageId=uuid4(),rating=value)
        with self.assertRaises(ValidationError): ChatFeedbackRequest(sessionId='session',messageId='wrong',rating='helpful')
        for message in ['   ', 'a'*4001]:
            with self.assertRaises(ValidationError): ChatRequest(sessionId='session',message=message)
        self.assertEqual(ChatRequest(sessionId='session',message='  Olá  ').message,'Olá')

class ChatApiContractTest(unittest.TestCase):
    def test_session_requires_authorization(self):
        from fastapi.testclient import TestClient
        from app.main import app
        response=TestClient(app).get('/chat/session')
        self.assertEqual(response.status_code,401)
        self.assertEqual(response.json()['code'],'SESSION_NOT_FOUND')

    def test_invalid_feedback_is_rejected_before_database(self):
        from fastapi.testclient import TestClient
        from app.main import app
        response=TestClient(app).post('/chat/feedback',json={'sessionId':'test','messageId':str(uuid4()),'rating':'unknown'})
        self.assertEqual(response.status_code,400)

    def test_message_contract_preserves_presentation_and_actions(self):
        from fastapi.testclient import TestClient
        from app import main
        reply={'messageId':str(uuid4()),'response':'Suas notas','presentation':{'kind':'subject-cards','title':'Suas notas','cards':[]},'suggestions':['Qual é minha PMG?']}
        with patch.object(main,'send_message',return_value=reply):
            response=TestClient(main.app).post('/chat/message',json={'sessionId':'test','message':'Minhas notas','requestId':str(uuid4())})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json(),reply)

if __name__=='__main__': unittest.main()
