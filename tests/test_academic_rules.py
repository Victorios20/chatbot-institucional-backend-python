import unittest
from app.academic_rules import evaluate_grades, pmg
from app.rag.intent_classifier import classify_intents


class AcademicRulesTest(unittest.TestCase):
    def test_boundaries(self):
        scenarios=[
          ({'AV1':3,'AV2':4},'REPROVADO_MEDIA_INICIAL',3.5),
          ({'AV1':4,'AV2':4},'PENDENTE',None),
          ({'AV1':4,'AV2':4,'AV3':6},'APROVADO',5),
          ({'AV1':6,'AV2':6,'AV3':4},'APROVADO',5),
          ({'AV1':4,'AV2':4,'AV3':4},'REPROVADO_MEDIA_FINAL',4),
          ({'AV1':10,'AV2':10,'AV3':3.99},'REPROVADO_REGRESSAO',7),
          ({'AV1':0,'AV2':0,'AV3':10},'REPROVADO_MEDIA_INICIAL',0),
          ({'AV1':None,'AV2':8,'AV3':8},'PENDENTE',None),
          ({'AV1':3.99,'AV2':4},'REPROVADO_MEDIA_INICIAL',4),
          ({'AV1':5.99,'AV2':6,'AV3':4},'REPROVADO_MEDIA_FINAL',5),
        ]
        for grades,status,final in scenarios:
            with self.subTest(grades=grades):
                result=evaluate_grades(grades,attendance=75)
                self.assertEqual(result['status'],status)
                self.assertEqual(result['finalAverage'],final)
    def test_required_av3(self):
        for initial,needed in [(4,6),(5,5),(6,4),(10,4)]:
            self.assertEqual(evaluate_grades({'AV1':initial,'AV2':initial})['requiredAv3'],needed)
    def test_av3_always_required(self):
        self.assertEqual(evaluate_grades({'AV1':10,'AV2':10},attendance=100)['status'],'PENDENTE')
    def test_attendance(self):
        self.assertEqual(evaluate_grades({'AV1':10,'AV2':10,'AV3':10},attendance=74.99)['status'],'REPROVADO_FREQUENCIA')
        self.assertEqual(evaluate_grades({'AV1':10,'AV2':10,'AV3':10})['status'],'NOTAS_SUFICIENTES_FREQUENCIA_PENDENTE')
    def test_single(self):
        self.assertEqual(evaluate_grades({'NOTA_UNICA':6},'SINGLE_GRADE',75)['status'],'APROVADO')
        self.assertEqual(evaluate_grades({'NOTA_UNICA':5.99},'SINGLE_GRADE',75)['status'],'REPROVADO_NOTA')
    def test_invalid(self):
        for value in [-1,10.01]:
            with self.assertRaises(ValueError):evaluate_grades({'AV1':value})
    def test_pmg_includes_zero_failures_repeats(self):
        result=pmg([{'closed':True,'finalAverage':0},{'closed':True,'finalAverage':4},
                    {'closed':True,'finalAverage':8},{'closed':False,'finalAverage':10},
                    {'closed':True,'finalAverage':None}])
        self.assertEqual(result['value'],4)
        self.assertEqual(result['count'],3)
        self.assertIsNone(pmg([])['value'])
    def test_simulation(self):
        from app.grade_simulation import simulate
        self.assertEqual(simulate('Se eu tirar AV1 4, AV2 4 e AV3 4, passo?')['result']['status'],'REPROVADO_MEDIA_FINAL')
        self.assertEqual(simulate('Se eu tirar AV1 6, AV2 6 e AV3 4')['result']['status'],'NOTAS_SUFICIENTES_FREQUENCIA_PENDENTE')
        self.assertIsNone(simulate('Quais minhas notas AV1, AV2 e AV3?'))
    def test_pmg_precision(self):
        self.assertEqual(pmg([{'closed':True,'finalAverage':5,'finalAverageExact':'4.995'},{'closed':True,'finalAverage':4.99,'finalAverageExact':'4.9925'}])['value'],4.99)
    def test_complementary_hours_routing(self):
        from app.academic_answers import structured_answer
        rag={'intents':[{'name':'credits'},{'name':'curriculum'}], 'databaseQueries':{'academic':{'data':{'progress':{'complementaryHoursApproved':32,'complementaryHoursRequired':120,'complementaryHoursRemaining':88}}}}}
        answer=structured_answer('Quantas horas complementares ainda faltam?',rag,{})
        self.assertIn('Faltam 88 horas',answer)
        self.assertNotIn('Matriz reduzida',answer)
    def test_optional_credits_routing(self):
        from app.academic_answers import structured_answer
        rag={'intents':[{'name':'credits'},{'name':'curriculum'}], 'databaseQueries':{'academic':{'data':{}}}}
        answer=structured_answer('Quantos créditos optativos faltam?',rag,{'course':{'requiredOptionalCredits':12,'completedOptionalCredits':8}})
        self.assertIn('faltam 4 créditos optativos',answer)
    def test_model_quota_failover(self):
        from app import gemini_service as service
        from unittest.mock import patch, MagicMock
        from types import SimpleNamespace
        error=RuntimeError('quota');error.code=429
        client=MagicMock()
        client.models.generate_content.side_effect=[error,SimpleNamespace(text='Resposta fundamentada')]
        settings=SimpleNamespace(gemini_api_key='fake-test-key',gemini_model='primary',gemini_fallback_models=('reserve',))
        with patch.object(service,'settings',settings), patch.object(service.genai,'Client',return_value=client), patch.dict(service._model_cooldowns,{},clear=True):
            self.assertEqual(service.generate_chat_answer('Explique',{}),'Resposta fundamentada')
            self.assertEqual(client.models.generate_content.call_count,2)
            self.assertEqual(client.models.generate_content.call_args.kwargs['model'],'reserve')
            self.assertIn('primary',service._model_cooldowns)
    def test_all_models_unavailable_uses_retrieved_rules(self):
        from app import gemini_service as service
        from unittest.mock import patch, MagicMock
        from types import SimpleNamespace
        client=MagicMock();client.models.generate_content.side_effect=RuntimeError('unavailable')
        settings=SimpleNamespace(gemini_api_key='fake-test-key',gemini_model='primary',gemini_fallback_models=('reserve',))
        rag={'intents':[{'name':'grades'}],'databaseQueries':{'academic':{'data':{'gradeRules':{'initialMinimum':4}}}}}
        with patch.object(service,'settings',settings), patch.object(service.genai,'Client',return_value=client), patch.dict(service._model_cooldowns,{},clear=True):
            answer=service.generate_chat_answer('Como funciona AV3?',{},rag)
            self.assertIn('AV3 é obrigatória',answer)
            self.assertIn('pelo menos 4',answer)
    def test_calendar_fallback_is_not_grade_rule(self):
        from app.academic_answers import grounded_fallback
        rag={'intents':[{'name':'calendar'},{'name':'grades'}], 'databaseQueries':{'academic':{'data':{'gradeRules':{'initialMinimum':4},'currentDate':'2026-10-26'}}, 'academic_events':{'available':True,'data':[{'title':'AV3 — calendário fictício','event_type':'EXAM_PERIOD','starts_on':'2026-11-23','ends_on':'2026-12-02'}]}}}
        answer=grounded_fallback('Quando é a AV3?',rag)
        self.assertIn('23/11/2026',answer)
        self.assertNotIn('MI =',answer)
        from app.academic_answers import structured_answer
        self.assertIn('23/11/2026',structured_answer('Quando é a AV3?',rag,{}))
    def test_attendance_bypasses_model_and_full_rag(self):
        from app import chatbot_service as service
        from unittest.mock import patch
        from types import SimpleNamespace
        student={'registration':'test','subjects':[{'name':'Banco de Dados','remainingAbsencesHours':4,'maximumAbsencesHours':18,'absencesInHours':14,'currentAttendancePercentage':80,'minimumAttendancePercentage':75}]}
        session=SimpleNamespace(student_context=student,history=[])
        with patch.object(service.session_store,'get',return_value=session), patch.object(service.session_store,'add_message'), patch.object(service,'find_chat_response',return_value=None), patch.object(service,'save_chat_response',side_effect=lambda registration, request_id, question, answer, presentation, suggestions: ({'response':answer},True)), patch.object(service,'get_student_context_by_registration',return_value=student), patch.object(service,'build_rag_context') as rag, patch.object(service,'generate_chat_answer') as model:
            answer=service.send_message(SimpleNamespace(sessionId='test',message='Quantas faltas ainda posso ter em Banco de Dados?'))['response']
            self.assertIn('ainda pode faltar 4 h',answer)
            self.assertIn('limite de 18 h',answer)
            rag.assert_not_called()
            model.assert_not_called()
    def test_attendance_over_limit_and_abono(self):
        from app.academic_answers import attendance_answer
        student={'subjects':[{'name':'Banco de Dados','remainingAbsencesHours':0,'maximumAbsencesHours':18,'absencesInHours':20,'currentAttendancePercentage':70,'minimumAttendancePercentage':75}]}
        self.assertIn('ultrapassado em 2 h',attendance_answer('Quantas faltas tenho?',student))
        self.assertIsNone(attendance_answer('Como abonar minhas faltas?',student))
    def test_intents(self):
        for text,intent in [('Qual minha PMG?','pmg'),('Quais matérias estão disponíveis?','offerings'),
                            ('Quais pré-requisitos faltam?','prerequisites'),('Qual minha próxima aula?','schedule'),
                            ('Qual meu histórico?','history'),('Quanto falta para concluir?','progress')]:
            self.assertIn(intent,[i.name for i in classify_intents(text)])

if __name__=='__main__':unittest.main()
