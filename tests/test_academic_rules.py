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
    def test_intents(self):
        for text,intent in [('Qual minha PMG?','pmg'),('Quais matérias estão disponíveis?','offerings'),
                            ('Quais pré-requisitos faltam?','prerequisites'),('Qual minha próxima aula?','schedule'),
                            ('Qual meu histórico?','history'),('Quanto falta para concluir?','progress')]:
            self.assertIn(intent,[i.name for i in classify_intents(text)])

if __name__=='__main__':unittest.main()
