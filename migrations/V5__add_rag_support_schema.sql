CREATE TABLE curriculum_rules (
    id UUID PRIMARY KEY,
    course_id UUID NOT NULL UNIQUE,
    total_semesters INTEGER NOT NULL,
    required_optional_hours INTEGER NOT NULL,
    required_complementary_hours INTEGER NOT NULL,
    requires_internship BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    CONSTRAINT fk_curriculum_rules_course FOREIGN KEY (course_id) REFERENCES courses (id)
);

CREATE TABLE assessment_models (
    id UUID PRIMARY KEY,
    subject_id UUID NOT NULL UNIQUE,
    model_type VARCHAR(30) NOT NULL,
    minimum_average NUMERIC(4, 2) NOT NULL,
    formula_description TEXT NOT NULL,
    av3_has_greater_weight BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_assessment_models_subject FOREIGN KEY (subject_id) REFERENCES subjects (id),
    CONSTRAINT chk_assessment_models_type CHECK (model_type IN ('SINGLE_GRADE', 'AV_SERIES'))
);

CREATE TABLE student_grades (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL,
    subject_id UUID NOT NULL,
    assessment_name VARCHAR(30) NOT NULL,
    grade_value NUMERIC(4, 2) NOT NULL,
    weight NUMERIC(4, 2) NOT NULL DEFAULT 1,
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_student_grades_student FOREIGN KEY (student_id) REFERENCES students (id),
    CONSTRAINT fk_student_grades_subject FOREIGN KEY (subject_id) REFERENCES subjects (id),
    CONSTRAINT uq_student_grades_assessment UNIQUE (student_id, subject_id, assessment_name),
    CONSTRAINT chk_student_grades_value CHECK (grade_value >= 0 AND grade_value <= 10),
    CONSTRAINT chk_student_grades_weight CHECK (weight > 0)
);

CREATE INDEX idx_student_grades_student_id ON student_grades (student_id);
CREATE INDEX idx_student_grades_subject_id ON student_grades (subject_id);

CREATE TABLE academic_events (
    id UUID PRIMARY KEY,
    title VARCHAR(160) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    starts_on DATE NOT NULL,
    ends_on DATE NOT NULL,
    audience VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    CONSTRAINT chk_academic_events_dates CHECK (ends_on >= starts_on)
);

CREATE INDEX idx_academic_events_type ON academic_events (event_type);
CREATE INDEX idx_academic_events_dates ON academic_events (starts_on, ends_on);

CREATE TABLE financial_records (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL,
    reference_month DATE NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL,
    paid_at TIMESTAMP,
    payment_method VARCHAR(40),
    description TEXT NOT NULL,
    CONSTRAINT fk_financial_records_student FOREIGN KEY (student_id) REFERENCES students (id),
    CONSTRAINT uq_financial_records_month UNIQUE (student_id, reference_month),
    CONSTRAINT chk_financial_records_status CHECK (status IN ('OPEN', 'PAID', 'OVERDUE', 'NEGOTIATION')),
    CONSTRAINT chk_financial_records_amount CHECK (amount >= 0)
);

CREATE INDEX idx_financial_records_student_id ON financial_records (student_id);
CREATE INDEX idx_financial_records_status ON financial_records (status);

CREATE TABLE student_benefits (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL,
    benefit_type VARCHAR(60) NOT NULL,
    percentage NUMERIC(5, 2) NOT NULL,
    status VARCHAR(30) NOT NULL,
    valid_from DATE NOT NULL,
    valid_until DATE,
    loss_reason TEXT,
    CONSTRAINT fk_student_benefits_student FOREIGN KEY (student_id) REFERENCES students (id),
    CONSTRAINT chk_student_benefits_status CHECK (status IN ('ACTIVE', 'SUSPENDED', 'ENDED')),
    CONSTRAINT chk_student_benefits_percentage CHECK (percentage >= 0 AND percentage <= 100),
    CONSTRAINT chk_student_benefits_dates CHECK (valid_until IS NULL OR valid_until >= valid_from)
);

CREATE INDEX idx_student_benefits_student_id ON student_benefits (student_id);
CREATE INDEX idx_student_benefits_status ON student_benefits (status);

CREATE TABLE complementary_activities (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL,
    activity_type VARCHAR(60) NOT NULL,
    description TEXT NOT NULL,
    hours INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL,
    approved_by VARCHAR(120),
    approved_at TIMESTAMP,
    CONSTRAINT fk_complementary_activities_student FOREIGN KEY (student_id) REFERENCES students (id),
    CONSTRAINT chk_complementary_activities_status CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    CONSTRAINT chk_complementary_activities_hours CHECK (hours > 0)
);

CREATE INDEX idx_complementary_activities_student_id ON complementary_activities (student_id);
CREATE INDEX idx_complementary_activities_status ON complementary_activities (status);

CREATE TABLE internships (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL,
    company_name VARCHAR(160) NOT NULL,
    internship_type VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL,
    starts_on DATE NOT NULL,
    ends_on DATE,
    weekly_hours INTEGER NOT NULL,
    approved_hours INTEGER NOT NULL DEFAULT 0,
    supervisor VARCHAR(120),
    CONSTRAINT fk_internships_student FOREIGN KEY (student_id) REFERENCES students (id),
    CONSTRAINT chk_internships_type CHECK (internship_type IN ('MANDATORY', 'NON_MANDATORY')),
    CONSTRAINT chk_internships_status CHECK (status IN ('PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT chk_internships_dates CHECK (ends_on IS NULL OR ends_on >= starts_on),
    CONSTRAINT chk_internships_weekly_hours CHECK (weekly_hours > 0),
    CONSTRAINT chk_internships_approved_hours CHECK (approved_hours >= 0)
);

CREATE INDEX idx_internships_student_id ON internships (student_id);
CREATE INDEX idx_internships_status ON internships (status);

CREATE TABLE class_slots (
    id UUID PRIMARY KEY,
    subject_id UUID NOT NULL,
    weekday INTEGER NOT NULL,
    shift VARCHAR(20) NOT NULL,
    slot_code VARCHAR(6) NOT NULL,
    starts_at TIME NOT NULL,
    ends_at TIME NOT NULL,
    duration_minutes INTEGER NOT NULL,
    CONSTRAINT fk_class_slots_subject FOREIGN KEY (subject_id) REFERENCES subjects (id),
    CONSTRAINT uq_class_slots_subject_slot UNIQUE (subject_id, weekday, shift, slot_code),
    CONSTRAINT chk_class_slots_weekday CHECK (weekday BETWEEN 1 AND 7),
    CONSTRAINT chk_class_slots_shift CHECK (shift IN ('MANHA', 'TARDE', 'NOITE')),
    CONSTRAINT chk_class_slots_duration CHECK (duration_minutes > 0),
    CONSTRAINT chk_class_slots_time CHECK (ends_at > starts_at)
);

CREATE INDEX idx_class_slots_subject_id ON class_slots (subject_id);

CREATE TABLE classes (
    id UUID PRIMARY KEY,
    subject_id UUID NOT NULL,
    slot_id UUID,
    class_date DATE NOT NULL,
    topic VARCHAR(200) NOT NULL,
    is_required_for_all BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    CONSTRAINT fk_classes_subject FOREIGN KEY (subject_id) REFERENCES subjects (id),
    CONSTRAINT fk_classes_slot FOREIGN KEY (slot_id) REFERENCES class_slots (id)
);

CREATE INDEX idx_classes_subject_id ON classes (subject_id);
CREATE INDEX idx_classes_date ON classes (class_date);

CREATE TABLE attendance_records (
    id UUID PRIMARY KEY,
    class_id UUID NOT NULL,
    student_id UUID NOT NULL,
    attended_slot_code VARCHAR(6),
    minutes_attended INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_attendance_records_class FOREIGN KEY (class_id) REFERENCES classes (id),
    CONSTRAINT fk_attendance_records_student FOREIGN KEY (student_id) REFERENCES students (id),
    CONSTRAINT uq_attendance_records_class_student UNIQUE (class_id, student_id),
    CONSTRAINT chk_attendance_records_status CHECK (status IN ('PRESENT', 'PARTIAL', 'ABSENT', 'EXCUSED')),
    CONSTRAINT chk_attendance_records_minutes CHECK (minutes_attended >= 0)
);

CREATE INDEX idx_attendance_records_student_id ON attendance_records (student_id);
CREATE INDEX idx_attendance_records_status ON attendance_records (status);

CREATE TABLE excused_absences (
    id UUID PRIMARY KEY,
    attendance_record_id UUID NOT NULL UNIQUE,
    reason TEXT NOT NULL,
    approved_by VARCHAR(120) NOT NULL,
    approved_at TIMESTAMP NOT NULL,
    counts_against_attendance BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_excused_absences_record FOREIGN KEY (attendance_record_id) REFERENCES attendance_records (id)
);
