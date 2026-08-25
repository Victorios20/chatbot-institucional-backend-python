INSERT INTO curriculum_rules (
    id, course_id, total_semesters, required_optional_hours, required_complementary_hours, requires_internship, notes
) VALUES
('11111111-1111-4111-8111-000000000001', 'b57cf5a4-bb33-4b37-9306-1c95b2ca1001', 8, 252, 120, FALSE, 'Curso de referencia do projeto. Exige horas optativas e atividades complementares.'),
('11111111-1111-4111-8111-000000000002', 'b57cf5a4-bb33-4b37-9306-1c95b2ca1002', 10, 300, 160, TRUE, 'Curso com maior carga pratica e estagio supervisionado.'),
('11111111-1111-4111-8111-000000000003', 'b57cf5a4-bb33-4b37-9306-1c95b2ca1003', 8, 200, 100, TRUE, 'Curso com trilhas optativas e atividades complementares.'),
('11111111-1111-4111-8111-000000000004', 'b57cf5a4-bb33-4b37-9306-1c95b2ca1004', 10, 160, 120, TRUE, 'Curso com pratica juridica e atividades complementares.'),
('11111111-1111-4111-8111-000000000005', 'b57cf5a4-bb33-4b37-9306-1c95b2ca1005', 10, 200, 180, TRUE, 'Curso com estagio e atividades praticas supervisionadas.'),
('11111111-1111-4111-8111-000000000006', 'b57cf5a4-bb33-4b37-9306-1c95b2ca1006', 12, 320, 200, TRUE, 'Curso com carga horaria extensa e atividades praticas obrigatorias.')
ON CONFLICT DO NOTHING;

INSERT INTO assessment_models (
    id, subject_id, model_type, minimum_average, formula_description, av3_has_greater_weight
) VALUES
('22222222-2222-4222-8222-000000000001', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000001', 'AV_SERIES', 5.00, 'Media composta por AV1, AV2 e AV3. A AV3 pode ter peso maior conforme plano de ensino.', TRUE),
('22222222-2222-4222-8222-000000000002', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000002', 'AV_SERIES', 5.00, 'Media composta por avaliacoes parciais e avaliacao final.', TRUE),
('22222222-2222-4222-8222-000000000003', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000003', 'SINGLE_GRADE', 6.00, 'Disciplina de nota unica com media minima 6.', FALSE),
('22222222-2222-4222-8222-000000000004', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000004', 'AV_SERIES', 5.00, 'Media composta por AV1, AV2 e AV3.', TRUE),
('22222222-2222-4222-8222-000000000005', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000005', 'SINGLE_GRADE', 6.00, 'Disciplina de nota unica com media minima 6.', FALSE),
('22222222-2222-4222-8222-000000000006', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000006', 'AV_SERIES', 5.00, 'Media composta por avaliacoes parciais e avaliacao final.', TRUE),
('22222222-2222-4222-8222-000000000007', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000011', 'AV_SERIES', 5.00, 'Media composta por AV1, AV2 e AV3.', TRUE),
('22222222-2222-4222-8222-000000000008', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000015', 'SINGLE_GRADE', 6.00, 'Disciplina de nota unica com media minima 6.', FALSE),
('22222222-2222-4222-8222-000000000009', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000019', 'AV_SERIES', 5.00, 'Media composta por avaliacoes parciais e avaliacao final.', TRUE),
('22222222-2222-4222-8222-000000000010', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000023', 'AV_SERIES', 5.00, 'Media composta por avaliacoes teoricas e praticas.', TRUE),
('22222222-2222-4222-8222-000000000011', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000029', 'SINGLE_GRADE', 6.00, 'Disciplina de nota unica com media minima 6.', FALSE),
('22222222-2222-4222-8222-000000000012', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000030', 'SINGLE_GRADE', 6.00, 'Disciplina de nota unica com media minima 6.', FALSE)
ON CONFLICT DO NOTHING;

INSERT INTO student_grades (
    id, student_id, subject_id, assessment_name, grade_value, weight, recorded_at
) VALUES
('33333333-3333-4333-8333-000000000001', '68580c37-69ca-4e35-b91f-3f010fbf9f01', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000001', 'AV1', 7.20, 1.00, '2026-03-20 10:00:00'),
('33333333-3333-4333-8333-000000000002', '68580c37-69ca-4e35-b91f-3f010fbf9f01', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000001', 'AV2', 6.80, 1.00, '2026-05-10 10:00:00'),
('33333333-3333-4333-8333-000000000003', '68580c37-69ca-4e35-b91f-3f010fbf9f01', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000002', 'AV1', 8.10, 1.00, '2026-03-21 10:00:00'),
('33333333-3333-4333-8333-000000000004', '68580c37-69ca-4e35-b91f-3f010fbf9f01', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000003', 'NOTA_UNICA', 6.40, 1.00, '2026-05-30 10:00:00'),
('33333333-3333-4333-8333-000000000005', '68580c37-69ca-4e35-b91f-3f010fbf9f02', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000004', 'AV1', 5.50, 1.00, '2026-03-22 10:00:00'),
('33333333-3333-4333-8333-000000000006', '68580c37-69ca-4e35-b91f-3f010fbf9f02', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000004', 'AV2', 6.00, 1.00, '2026-05-11 10:00:00'),
('33333333-3333-4333-8333-000000000007', '68580c37-69ca-4e35-b91f-3f010fbf9f03', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000028', 'NOTA_UNICA', 7.00, 1.00, '2026-05-28 10:00:00'),
('33333333-3333-4333-8333-000000000008', '68580c37-69ca-4e35-b91f-3f010fbf9f05', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000011', 'AV1', 6.30, 1.00, '2026-03-25 10:00:00'),
('33333333-3333-4333-8333-000000000009', '68580c37-69ca-4e35-b91f-3f010fbf9f07', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000015', 'NOTA_UNICA', 8.40, 1.00, '2026-05-29 10:00:00'),
('33333333-3333-4333-8333-000000000010', '68580c37-69ca-4e35-b91f-3f010fbf9f09', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000019', 'AV1', 7.80, 1.00, '2026-03-26 10:00:00'),
('33333333-3333-4333-8333-000000000011', '68580c37-69ca-4e35-b91f-3f010fbf9f11', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000023', 'AV1', 6.90, 1.00, '2026-03-27 10:00:00'),
('33333333-3333-4333-8333-000000000012', '68580c37-69ca-4e35-b91f-3f010fbf9f11', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000024', 'AV1', 7.10, 1.00, '2026-03-28 10:00:00')
ON CONFLICT DO NOTHING;

INSERT INTO academic_events (
    id, title, event_type, starts_on, ends_on, audience, description
) VALUES
('44444444-4444-4444-8444-000000000001', 'Inicio do primeiro semestre', 'SEMESTER_START', '2026-02-02', '2026-02-02', 'Todos os alunos', 'Inicio aproximado do primeiro semestre letivo.'),
('44444444-4444-4444-8444-000000000002', 'Periodo de AV1', 'EXAM_PERIOD', '2026-03-16', '2026-03-28', 'Alunos de graduacao', 'Periodo previsto para avaliacoes AV1.'),
('44444444-4444-4444-8444-000000000003', 'Periodo de AV2', 'EXAM_PERIOD', '2026-05-04', '2026-05-16', 'Alunos de graduacao', 'Periodo previsto para avaliacoes AV2.'),
('44444444-4444-4444-8444-000000000004', 'Periodo de AV3', 'EXAM_PERIOD', '2026-06-08', '2026-06-20', 'Alunos de graduacao', 'Periodo previsto para avaliacoes AV3.'),
('44444444-4444-4444-8444-000000000005', 'Fim do primeiro semestre', 'SEMESTER_END', '2026-06-26', '2026-06-26', 'Todos os alunos', 'Encerramento aproximado do primeiro semestre letivo.'),
('44444444-4444-4444-8444-000000000006', 'Inicio do segundo semestre', 'SEMESTER_START', '2026-08-03', '2026-08-03', 'Todos os alunos', 'Inicio aproximado do segundo semestre letivo.'),
('44444444-4444-4444-8444-000000000007', 'Periodo de rematricula', 'ENROLLMENT', '2026-07-10', '2026-07-25', 'Alunos veteranos', 'Periodo previsto para rematricula do segundo semestre.'),
('44444444-4444-4444-8444-000000000008', 'Fim do segundo semestre', 'SEMESTER_END', '2026-12-04', '2026-12-04', 'Todos os alunos', 'Encerramento aproximado do segundo semestre letivo.')
ON CONFLICT DO NOTHING;

INSERT INTO financial_records (
    id, student_id, reference_month, amount, due_date, status, paid_at, payment_method, description
) VALUES
('55555555-5555-4555-8555-000000000001', '68580c37-69ca-4e35-b91f-3f010fbf9f01', '2026-08-01', 1490.00, '2026-08-10', 'PAID', '2026-08-08 14:20:00', 'BOLETO', 'Mensalidade de agosto.'),
('55555555-5555-4555-8555-000000000002', '68580c37-69ca-4e35-b91f-3f010fbf9f01', '2026-09-01', 1490.00, '2026-09-10', 'OPEN', NULL, NULL, 'Mensalidade de setembro.'),
('55555555-5555-4555-8555-000000000003', '68580c37-69ca-4e35-b91f-3f010fbf9f02', '2026-08-01', 1490.00, '2026-08-10', 'OVERDUE', NULL, NULL, 'Mensalidade de agosto em atraso.'),
('55555555-5555-4555-8555-000000000004', '68580c37-69ca-4e35-b91f-3f010fbf9f03', '2026-08-01', 1720.00, '2026-08-10', 'PAID', '2026-08-09 09:10:00', 'PIX', 'Mensalidade de agosto.'),
('55555555-5555-4555-8555-000000000005', '68580c37-69ca-4e35-b91f-3f010fbf9f05', '2026-08-01', 1320.00, '2026-08-10', 'NEGOTIATION', NULL, NULL, 'Mensalidade em negociacao.'),
('55555555-5555-4555-8555-000000000006', '68580c37-69ca-4e35-b91f-3f010fbf9f11', '2026-08-01', 3950.00, '2026-08-10', 'OPEN', NULL, NULL, 'Mensalidade de agosto.')
ON CONFLICT DO NOTHING;

INSERT INTO student_benefits (
    id, student_id, benefit_type, percentage, status, valid_from, valid_until, loss_reason
) VALUES
('66666666-6666-4666-8666-000000000001', '68580c37-69ca-4e35-b91f-3f010fbf9f01', 'DESCONTO_PONTUALIDADE', 10.00, 'ACTIVE', '2026-02-01', NULL, NULL),
('66666666-6666-4666-8666-000000000002', '68580c37-69ca-4e35-b91f-3f010fbf9f02', 'BOLSA_INSTITUCIONAL', 35.00, 'SUSPENDED', '2026-02-01', NULL, 'Mensalidade em atraso.'),
('66666666-6666-4666-8666-000000000003', '68580c37-69ca-4e35-b91f-3f010fbf9f05', 'DESCONTO_CONVENIO', 15.00, 'ACTIVE', '2026-02-01', '2026-12-31', NULL),
('66666666-6666-4666-8666-000000000004', '68580c37-69ca-4e35-b91f-3f010fbf9f09', 'BOLSA_MERITO', 25.00, 'ACTIVE', '2026-02-01', '2026-12-31', NULL)
ON CONFLICT DO NOTHING;

INSERT INTO complementary_activities (
    id, student_id, activity_type, description, hours, status, approved_by, approved_at
) VALUES
('77777777-7777-4777-8777-000000000001', '68580c37-69ca-4e35-b91f-3f010fbf9f01', 'CURSO_ONLINE', 'Curso introdutorio de Python para analise de dados.', 20, 'APPROVED', 'Coordenacao do curso', '2026-04-10 15:00:00'),
('77777777-7777-4777-8777-000000000002', '68580c37-69ca-4e35-b91f-3f010fbf9f01', 'EVENTO_ACADEMICO', 'Semana academica de tecnologia.', 12, 'APPROVED', 'Coordenacao do curso', '2026-05-05 15:00:00'),
('77777777-7777-4777-8777-000000000003', '68580c37-69ca-4e35-b91f-3f010fbf9f02', 'PALESTRA', 'Palestra sobre carreira em dados.', 4, 'PENDING', NULL, NULL),
('77777777-7777-4777-8777-000000000004', '68580c37-69ca-4e35-b91f-3f010fbf9f05', 'PROJETO_EXTENSAO', 'Projeto de consultoria para pequenos negocios.', 30, 'APPROVED', 'Coordenacao do curso', '2026-05-20 15:00:00'),
('77777777-7777-4777-8777-000000000005', '68580c37-69ca-4e35-b91f-3f010fbf9f09', 'EVENTO_ACADEMICO', 'Jornada de psicologia aplicada.', 16, 'APPROVED', 'Coordenacao do curso', '2026-05-22 15:00:00')
ON CONFLICT DO NOTHING;

INSERT INTO internships (
    id, student_id, company_name, internship_type, status, starts_on, ends_on, weekly_hours, approved_hours, supervisor
) VALUES
('88888888-8888-4888-8888-000000000001', '68580c37-69ca-4e35-b91f-3f010fbf9f05', 'Empresa Junior Administracao', 'NON_MANDATORY', 'ACTIVE', '2026-03-01', NULL, 20, 80, 'Carla Menezes'),
('88888888-8888-4888-8888-000000000002', '68580c37-69ca-4e35-b91f-3f010fbf9f09', 'Clinica Escola', 'MANDATORY', 'PLANNED', '2026-09-01', '2026-12-01', 16, 0, 'Marcio Salles'),
('88888888-8888-4888-8888-000000000003', '68580c37-69ca-4e35-b91f-3f010fbf9f03', 'Construtora Modelo', 'MANDATORY', 'ACTIVE', '2026-04-01', NULL, 20, 60, 'Helena Duarte')
ON CONFLICT DO NOTHING;

INSERT INTO class_slots (
    id, subject_id, weekday, shift, slot_code, starts_at, ends_at, duration_minutes
) VALUES
('99999999-9999-4999-8999-000000000001', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000001', 2, 'MANHA', 'AB', '07:30:00', '09:10:00', 100),
('99999999-9999-4999-8999-000000000002', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000002', 3, 'MANHA', 'CD', '09:20:00', '11:00:00', 100),
('99999999-9999-4999-8999-000000000003', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000003', 4, 'NOITE', 'AB', '18:30:00', '20:10:00', 100),
('99999999-9999-4999-8999-000000000004', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000004', 5, 'NOITE', 'CD', '20:20:00', '22:00:00', 100)
ON CONFLICT DO NOTHING;

INSERT INTO classes (
    id, subject_id, slot_id, class_date, topic, is_required_for_all, notes
) VALUES
('aaaaaaaa-aaaa-4aaa-8aaa-000000000001', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000001', '99999999-9999-4999-8999-000000000001', '2026-08-04', 'Modelagem relacional', TRUE, 'Aula regular.'),
('aaaaaaaa-aaaa-4aaa-8aaa-000000000002', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000001', '99999999-9999-4999-8999-000000000001', '2026-08-11', 'Normalizacao', TRUE, 'Aula regular.'),
('aaaaaaaa-aaaa-4aaa-8aaa-000000000003', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000001', '99999999-9999-4999-8999-000000000001', '2026-08-18', 'Acompanhamento de grupo', FALSE, 'Atendimento especifico para grupo selecionado.'),
('aaaaaaaa-aaaa-4aaa-8aaa-000000000004', '8f5c7eb3-e2b4-4eff-a1b0-0e9f10000002', '99999999-9999-4999-8999-000000000002', '2026-08-05', 'Listas encadeadas', TRUE, 'Aula regular.')
ON CONFLICT DO NOTHING;

INSERT INTO attendance_records (
    id, class_id, student_id, attended_slot_code, minutes_attended, status, created_at
) VALUES
('bbbbbbbb-bbbb-4bbb-8bbb-000000000001', 'aaaaaaaa-aaaa-4aaa-8aaa-000000000001', '68580c37-69ca-4e35-b91f-3f010fbf9f01', 'AB', 100, 'PRESENT', '2026-08-04 09:15:00'),
('bbbbbbbb-bbbb-4bbb-8bbb-000000000002', 'aaaaaaaa-aaaa-4aaa-8aaa-000000000002', '68580c37-69ca-4e35-b91f-3f010fbf9f01', 'A', 50, 'PARTIAL', '2026-08-11 09:15:00'),
('bbbbbbbb-bbbb-4bbb-8bbb-000000000003', 'aaaaaaaa-aaaa-4aaa-8aaa-000000000003', '68580c37-69ca-4e35-b91f-3f010fbf9f01', NULL, 0, 'EXCUSED', '2026-08-18 09:15:00'),
('bbbbbbbb-bbbb-4bbb-8bbb-000000000004', 'aaaaaaaa-aaaa-4aaa-8aaa-000000000001', '68580c37-69ca-4e35-b91f-3f010fbf9f02', NULL, 0, 'ABSENT', '2026-08-04 09:15:00'),
('bbbbbbbb-bbbb-4bbb-8bbb-000000000005', 'aaaaaaaa-aaaa-4aaa-8aaa-000000000004', '68580c37-69ca-4e35-b91f-3f010fbf9f01', 'CD', 100, 'PRESENT', '2026-08-05 11:05:00')
ON CONFLICT DO NOTHING;

INSERT INTO excused_absences (
    id, attendance_record_id, reason, approved_by, approved_at, counts_against_attendance
) VALUES
('cccccccc-cccc-4ccc-8ccc-000000000001', 'bbbbbbbb-bbbb-4bbb-8bbb-000000000003', 'Aula de acompanhamento destinada apenas a grupo especifico.', 'Professor da disciplina', '2026-08-18 10:00:00', FALSE)
ON CONFLICT DO NOTHING;
