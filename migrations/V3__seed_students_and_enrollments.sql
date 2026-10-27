INSERT INTO students (id, registration, full_name, password_hash, account_non_locked, failed_attempts, lock_time, course_id) VALUES
('68580c37-69ca-4e35-b91f-3f010fbf9f01', '2310000', 'João Silva', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1001'),
('68580c37-69ca-4e35-b91f-3f010fbf9f02', '2310001', 'Mariana Souza', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1001'),
('68580c37-69ca-4e35-b91f-3f010fbf9f03', '2410002', 'Lucas Almeida', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1002'),
('68580c37-69ca-4e35-b91f-3f010fbf9f04', '2410003', 'Fernanda Martins', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1002'),
('68580c37-69ca-4e35-b91f-3f010fbf9f05', '2210004', 'Rafael Nascimento', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1003'),
('68580c37-69ca-4e35-b91f-3f010fbf9f06', '2210005', 'Patrícia Lima', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1003'),
('68580c37-69ca-4e35-b91f-3f010fbf9f07', '2110006', 'Eduardo Falcão', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1004'),
('68580c37-69ca-4e35-b91f-3f010fbf9f08', '2110007', 'Camila Rezende', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1004'),
('68580c37-69ca-4e35-b91f-3f010fbf9f09', '2510008', 'Bianca Menezes', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1005'),
('68580c37-69ca-4e35-b91f-3f010fbf9f10', '2510009', 'Thiago Barros', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1005'),
('68580c37-69ca-4e35-b91f-3f010fbf9f11', '2010010', 'Gabriela Rocha', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1006'),
('68580c37-69ca-4e35-b91f-3f010fbf9f12', '2010011', 'Henrique Dantas', '$2a$12$RAI69Wp8Ls9r5YC8U8z.POVBZBKu4XQFNY5T5lXXnFoxlebPxjjPy', TRUE, 0, NULL, 'b57cf5a4-bb33-4b37-9306-1c95b2ca1006');

INSERT INTO enrollments (id, student_id, current_semester, completed_optional_credits) VALUES
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb01', '68580c37-69ca-4e35-b91f-3f010fbf9f01', 3, 4),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb02', '68580c37-69ca-4e35-b91f-3f010fbf9f02', 6, 10),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb03', '68580c37-69ca-4e35-b91f-3f010fbf9f03', 2, 2),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb04', '68580c37-69ca-4e35-b91f-3f010fbf9f04', 8, 12),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb05', '68580c37-69ca-4e35-b91f-3f010fbf9f05', 5, 6),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb06', '68580c37-69ca-4e35-b91f-3f010fbf9f06', 7, 10),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb07', '68580c37-69ca-4e35-b91f-3f010fbf9f07', 4, 2),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb08', '68580c37-69ca-4e35-b91f-3f010fbf9f08', 9, 8),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb09', '68580c37-69ca-4e35-b91f-3f010fbf9f09', 1, 0),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb10', '68580c37-69ca-4e35-b91f-3f010fbf9f10', 5, 4),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb11', '68580c37-69ca-4e35-b91f-3f010fbf9f11', 10, 14),
('de9d45f2-0df7-40ab-8d9d-3e7a08dfeb12', '68580c37-69ca-4e35-b91f-3f010fbf9f12', 7, 9);
