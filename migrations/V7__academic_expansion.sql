-- Demonstrative academic data. Existing enrollments and credentials are preserved.
CREATE TABLE academic_terms (
 id TEXT PRIMARY KEY, starts_on DATE NOT NULL, ends_on DATE NOT NULL,
 CHECK (ends_on >= starts_on)
);
CREATE TABLE course_curriculum (
 course_id UUID REFERENCES courses(id), subject_id UUID REFERENCES subjects(id),
 recommended_semester INTEGER NOT NULL CHECK(recommended_semester > 0),
 category TEXT NOT NULL CHECK(category IN ('REQUIRED','OPTIONAL')),
 credits INTEGER NOT NULL CHECK(credits > 0),
 PRIMARY KEY(course_id,subject_id)
);
CREATE TABLE subject_prerequisites (
 course_id UUID NOT NULL, subject_id UUID NOT NULL, prerequisite_id UUID NOT NULL,
 PRIMARY KEY(course_id,subject_id,prerequisite_id),
 FOREIGN KEY(course_id,subject_id) REFERENCES course_curriculum(course_id,subject_id),
 FOREIGN KEY(course_id,prerequisite_id) REFERENCES course_curriculum(course_id,subject_id),
 CHECK(subject_id <> prerequisite_id)
);
CREATE TABLE academic_attempts (
 id UUID PRIMARY KEY, student_id UUID NOT NULL REFERENCES students(id),
 subject_id UUID NOT NULL REFERENCES subjects(id), term_id TEXT NOT NULL REFERENCES academic_terms(id),
 assessment_model TEXT NOT NULL DEFAULT 'AV_SERIES' CHECK(assessment_model IN ('AV_SERIES','SINGLE_GRADE')),
 attendance_percentage NUMERIC(5,2) CHECK(attendance_percentage BETWEEN 0 AND 100),
 closed BOOLEAN NOT NULL DEFAULT FALSE,
 UNIQUE(student_id,subject_id,term_id), UNIQUE(id,student_id,subject_id)
);
CREATE INDEX academic_attempts_student_idx ON academic_attempts(student_id);
ALTER TABLE student_grades ADD COLUMN attempt_id UUID;
ALTER TABLE student_grades ADD CONSTRAINT grades_attempt_fk FOREIGN KEY(attempt_id,student_id,subject_id) REFERENCES academic_attempts(id,student_id,subject_id);
ALTER TABLE student_grades DROP CONSTRAINT uq_student_grades_assessment;
ALTER TABLE student_grades ALTER COLUMN grade_value DROP NOT NULL;
ALTER TABLE student_grades ADD CONSTRAINT grades_attempt_assessment_unique UNIQUE(attempt_id,assessment_name);
ALTER TABLE student_grades ADD CONSTRAINT grades_assessment_name CHECK(assessment_name IN ('AV1','AV2','AV3','NOTA_UNICA'));
CREATE INDEX grades_attempt_idx ON student_grades(attempt_id);
CREATE TABLE subject_offerings (
 id UUID PRIMARY KEY, course_id UUID NOT NULL, subject_id UUID NOT NULL,
 term_id TEXT NOT NULL REFERENCES academic_terms(id), class_code TEXT NOT NULL,
 teacher TEXT NOT NULL, room TEXT NOT NULL, seats_available INTEGER NOT NULL CHECK(seats_available>=0),
 FOREIGN KEY(course_id,subject_id) REFERENCES course_curriculum(course_id,subject_id),
 UNIQUE(course_id,subject_id,term_id,class_code)
);
CREATE TABLE offering_schedules (
 id UUID PRIMARY KEY, offering_id UUID NOT NULL REFERENCES subject_offerings(id),
 weekday INTEGER NOT NULL CHECK(weekday BETWEEN 1 AND 7),
 starts_at TIME NOT NULL, ends_at TIME NOT NULL, CHECK(ends_at>starts_at),
 UNIQUE(offering_id,weekday,starts_at)
);
CREATE TABLE student_offerings (
 student_id UUID REFERENCES students(id), offering_id UUID REFERENCES subject_offerings(id),
 PRIMARY KEY(student_id,offering_id)
);
