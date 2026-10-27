CREATE TABLE courses (
    id UUID PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    required_optional_credits INTEGER NOT NULL
);

CREATE TABLE students (
    id UUID PRIMARY KEY,
    registration VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(140) NOT NULL,
    password_hash VARCHAR(120) NOT NULL,
    account_non_locked BOOLEAN NOT NULL DEFAULT TRUE,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    lock_time TIMESTAMP,
    course_id UUID NOT NULL,
    CONSTRAINT fk_students_course FOREIGN KEY (course_id) REFERENCES courses (id)
);

CREATE INDEX idx_students_course_id ON students (course_id);

CREATE TABLE enrollments (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL UNIQUE,
    current_semester INTEGER NOT NULL,
    completed_optional_credits INTEGER NOT NULL,
    CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id) REFERENCES students (id)
);

CREATE TABLE subjects (
    id UUID PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    teacher VARCHAR(120) NOT NULL,
    workload_hours INTEGER NOT NULL,
    minimum_attendance_percentage DOUBLE PRECISION NOT NULL,
    class_duration_minutes INTEGER NOT NULL
);

CREATE TABLE student_subjects (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL,
    subject_id UUID NOT NULL,
    current_attendance_percentage DOUBLE PRECISION NOT NULL,
    absences_in_hours INTEGER NOT NULL,
    CONSTRAINT fk_student_subjects_student FOREIGN KEY (student_id) REFERENCES students (id),
    CONSTRAINT fk_student_subjects_subject FOREIGN KEY (subject_id) REFERENCES subjects (id)
);

CREATE INDEX idx_student_subjects_student_id ON student_subjects (student_id);
CREATE INDEX idx_student_subjects_subject_id ON student_subjects (subject_id);

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY,
    token_hash VARCHAR(200) NOT NULL UNIQUE,
    student_id UUID NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_refresh_tokens_student FOREIGN KEY (student_id) REFERENCES students (id)
);

CREATE INDEX idx_refresh_tokens_student_id ON refresh_tokens (student_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens (expires_at);
