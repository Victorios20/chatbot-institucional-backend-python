-- Two additional fictitious profiles: beginning and near the end of the reduced matrix.
INSERT INTO students(id,registration,full_name,password_hash,course_id)
 SELECT md5('profile:'||x.registration)::uuid,x.registration,x.name,s.password_hash,s.course_id
 FROM students s CROSS JOIN (VALUES ('2610090','Aluno Iniciante — Demonstração'),('1910091','Aluna Concluinte — Demonstração')) x(registration,name)
 WHERE s.registration='2310000' ON CONFLICT DO NOTHING;
INSERT INTO enrollments(id,student_id,current_semester,completed_optional_credits)
 SELECT md5('enrollment:'||registration)::uuid,id,CASE WHEN registration='2610090' THEN 1 ELSE 8 END,
 CASE WHEN registration='2610090' THEN 0 ELSE 8 END FROM students WHERE registration IN ('2610090','1910091') ON CONFLICT DO NOTHING;
INSERT INTO academic_attempts(id,student_id,subject_id,term_id,assessment_model,attendance_percentage,closed)
 SELECT md5('profile-attempt:'||s.id::text||cc.subject_id::text)::uuid,s.id,cc.subject_id,'2026.1','AV_SERIES',95,TRUE
 FROM students s JOIN course_curriculum cc ON cc.course_id=s.course_id JOIN subjects sub ON sub.id=cc.subject_id
 WHERE s.registration='1910091' AND sub.name<>'Inteligência Artificial' ON CONFLICT DO NOTHING;
INSERT INTO academic_attempts(id,student_id,subject_id,term_id,assessment_model,attendance_percentage,closed)
 SELECT md5('profile-current:'||s.id::text||cc.subject_id::text)::uuid,s.id,cc.subject_id,'2026.2','AV_SERIES',90,FALSE
 FROM students s JOIN course_curriculum cc ON cc.course_id=s.course_id JOIN subjects sub ON sub.id=cc.subject_id
 WHERE (s.registration='2610090' AND sub.name IN ('Introdução à Programação','Lógica Computacional'))
 OR (s.registration='1910091' AND sub.name='Inteligência Artificial') ON CONFLICT DO NOTHING;
INSERT INTO student_grades(id,student_id,subject_id,attempt_id,assessment_name,grade_value)
 SELECT md5(a.id::text||n.name)::uuid,a.student_id,a.subject_id,a.id,n.name,
 CASE WHEN a.closed THEN 8 WHEN n.name='AV1' THEN 7 WHEN n.name='AV2' THEN 8 ELSE NULL END
 FROM academic_attempts a JOIN students s ON s.id=a.student_id CROSS JOIN (VALUES ('AV1'),('AV2'),('AV3')) n(name)
 WHERE s.registration IN ('2610090','1910091') ON CONFLICT DO NOTHING;
INSERT INTO student_subjects(id,student_id,subject_id,current_attendance_percentage,absences_in_hours)
 SELECT md5('profile-subject:'||a.id::text)::uuid,a.student_id,a.subject_id,90,2 FROM academic_attempts a JOIN students s ON s.id=a.student_id
 WHERE s.registration IN ('2610090','1910091') AND NOT a.closed ON CONFLICT DO NOTHING;
INSERT INTO student_offerings(student_id,offering_id)
 SELECT a.student_id,o.id FROM academic_attempts a JOIN students s ON s.id=a.student_id
 JOIN subject_offerings o ON o.subject_id=a.subject_id AND o.course_id=s.course_id AND o.term_id=a.term_id
 WHERE s.registration IN ('2610090','1910091') AND NOT a.closed ON CONFLICT DO NOTHING;
