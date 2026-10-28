"""Queries scoped to the authenticated student, never a registration supplied in chat."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.database import get_connection
from app.academic_rules import evaluate_grades, pmg
from app.rag.database_retriever import serialize_rows


def get_academic_context(registration):
    with get_connection() as conn:
        profile = conn.execute('''SELECT s.id, s.course_id, c.name FROM students s JOIN courses c ON c.id=s.course_id
                                  WHERE s.registration=%s''', (registration,)).fetchone()
        if not profile:
            return {}
        student_id, course_id = profile['id'], profile['course_id']
        curriculum = serialize_rows(conn.execute('''SELECT cc.subject_id,sub.name,cc.category,cc.credits,
             cc.recommended_semester,sub.workload_hours,sub.minimum_attendance_percentage
             FROM course_curriculum cc JOIN subjects sub ON sub.id=cc.subject_id
             WHERE cc.course_id=%s ORDER BY cc.recommended_semester,sub.name''', (course_id,)).fetchall())
        prerequisites = serialize_rows(conn.execute('''SELECT p.subject_id,p.prerequisite_id,s.name AS prerequisite_name
             FROM subject_prerequisites p JOIN subjects s ON s.id=p.prerequisite_id WHERE p.course_id=%s''',(course_id,)).fetchall())
        attempts = serialize_rows(conn.execute('''SELECT a.id,a.subject_id,s.name,a.term_id,a.closed,a.assessment_model,
             a.attendance_percentage,s.minimum_attendance_percentage,s.workload_hours
             FROM academic_attempts a JOIN subjects s ON s.id=a.subject_id
             WHERE a.student_id=%s ORDER BY a.term_id,s.name''',(student_id,)).fetchall())
        grades = serialize_rows(conn.execute('''SELECT g.attempt_id,g.assessment_name,g.grade_value,g.recorded_at
             FROM student_grades g JOIN academic_attempts a ON a.id=g.attempt_id
             WHERE a.student_id=%s ORDER BY a.term_id,g.assessment_name''',(student_id,)).fetchall())
        offerings = serialize_rows(conn.execute('''SELECT o.id,o.subject_id,s.name,o.term_id,o.class_code,o.teacher,o.room,
             o.seats_available,EXISTS(SELECT 1 FROM student_offerings so WHERE so.offering_id=o.id AND so.student_id=%s) AS enrolled
             FROM subject_offerings o JOIN subjects s ON s.id=o.subject_id WHERE o.course_id=%s ORDER BY o.term_id,s.name''',(student_id,course_id)).fetchall())
        schedules = serialize_rows(conn.execute('''SELECT os.offering_id,os.weekday,os.starts_at,os.ends_at
             FROM offering_schedules os JOIN subject_offerings o ON o.id=os.offering_id WHERE o.course_id=%s''',(course_id,)).fetchall())
        activities = serialize_rows(conn.execute('SELECT hours,status FROM complementary_activities WHERE student_id=%s',(student_id,)).fetchall())
        rules = conn.execute('SELECT required_complementary_hours,requires_internship FROM curriculum_rules WHERE course_id=%s',(course_id,)).fetchone() or {}
    now = datetime.now(ZoneInfo('America/Fortaleza'))
    # The term is resolved by dates; future terms are available for planning.
    current = next((o['term_id'] for o in offerings if o['term_id'] == f'{now.year}.{1 if now.month<=6 else 2}'), None)
    grades_by_attempt = {}
    for grade in grades:
        grades_by_attempt.setdefault(grade['attempt_id'],{})[grade['assessment_name']] = grade['grade_value']
    for a in attempts:
        a['grades'] = grades_by_attempt.get(a['id'],{})
        a.update(evaluate_grades(a['grades'],a['assessment_model'],a['attendance_percentage'],a['minimum_attendance_percentage']))
        a['scope'] = 'ENCERRADA' if a['closed'] else 'EM_CURSO'
    completed = {a['subject_id'] for a in attempts if a['closed'] and a['status']=='APROVADO'}
    enrolled_subjects = {o['subject_id'] for o in offerings if o['enrolled'] and o['term_id']==current}
    for sub in curriculum:
        sub['completed'] = sub['subject_id'] in completed
        sub['inProgress'] = sub['subject_id'] in enrolled_subjects
        sub['prerequisites'] = [p['prerequisite_name'] for p in prerequisites if p['subject_id']==sub['subject_id']]
    for o in offerings:
        missing = [p['prerequisite_name'] for p in prerequisites if p['subject_id']==o['subject_id'] and p['prerequisite_id'] not in completed]
        o['schedules'] = [s for s in schedules if s['offering_id']==o['id']]
        o['missingPrerequisites'] = missing
        reasons=[]
        if o['subject_id'] in completed: reasons.append('Disciplina já concluída')
        if o['enrolled']: reasons.append('Já matriculado nesta turma')
        if missing: reasons.append('Pré-requisitos pendentes')
        if o['seats_available']==0: reasons.append('Sem vagas')
        o['eligibleByAcademicRules'] = not reasons
        o['restrictions'] = reasons
    schedule = []
    for o in offerings:
        if o['enrolled'] and o['term_id']==current:
            for s in o['schedules']:
                schedule.append({'name':o['name'],'teacher':o['teacher'],'room':o['room'],**s})
    for o in offerings:
        conflicts=[]
        for candidate in o['schedules']:
            for enrolled in schedule if o['term_id']==current and not o['enrolled'] else []:
                if candidate['weekday']==enrolled['weekday'] and candidate['starts_at']<enrolled['ends_at'] and enrolled['starts_at']<candidate['ends_at']:
                    conflicts.append(enrolled['name'])
        o['scheduleConflicts'] = sorted(set(conflicts))
        o['canEnrollInPrototype'] = o['eligibleByAcademicRules'] and not conflicts
    upcoming=[]
    for s in schedule:
        day=now.date()+timedelta(days=(s['weekday']-now.isoweekday())%7)
        start=datetime.fromisoformat(str(day)+'T'+s['starts_at']).replace(tzinfo=now.tzinfo)
        end=datetime.fromisoformat(str(day)+'T'+s['ends_at']).replace(tzinfo=now.tzinfo)
        if end<=now: start+=timedelta(days=7);end+=timedelta(days=7)
        upcoming.append({**s,'startsOn':start.isoformat(),'endsOn':end.isoformat()})
    total_hours=sum(s['workload_hours'] for s in curriculum)
    done_hours=sum(s['workload_hours'] for s in curriculum if s['completed'])
    total_credits=sum(s['credits'] for s in curriculum)
    done_credits=sum(s['credits'] for s in curriculum if s['completed'])
    required=[s for s in curriculum if s['category']=='REQUIRED']
    optional=[s for s in curriculum if s['category']=='OPTIONAL']
    approved_hours=sum(a['hours'] for a in activities if a['status']=='APPROVED')
    return {'dataSource':'Registros acadêmicos cadastrados. O progresso considera somente a matriz disponível e não confirma autorização para formatura.',
            'currentDate':now.isoformat(),'currentTerm':current,
            'gradeRules':{'initialMinimum':4,'av3Minimum':4,'finalMinimum':5,'singleGradeMinimum':6,
              'av3Mandatory':True,'formula':'MI=(AV1+AV2)/2; MF=(MI+AV3)/2'},
            'attempts':attempts,'pmg':pmg(attempts),
            'pmgByTerm':[{'term':t,**pmg([a for a in attempts if a['term_id']==t])} for t in sorted({a['term_id'] for a in attempts})],
            'curriculum':curriculum,'offerings':offerings,'schedule':schedule,
            'nextClass':min(upcoming,key=lambda x:x['startsOn']) if upcoming else None,
            'progress':{'scope':'Matriz curricular cadastrada; conclusão depende dos demais requisitos acadêmicos',
              'totalHours':total_hours,'completedHours':done_hours,'remainingHours':total_hours-done_hours,
              'totalCredits':total_credits,'completedCredits':done_credits,'remainingCredits':total_credits-done_credits,
              'percentage':round(100*done_hours/total_hours,2) if total_hours else 0,
              'requiredSubjectsRemaining':[s['name'] for s in required if not s['completed']],
              'optionalCreditsOffered':sum(s['credits'] for s in optional),
              'optionalCreditsCompleted':sum(s['credits'] for s in optional if s['completed']),
              'complementaryHoursApproved':approved_hours,
              'complementaryHoursRequired':rules.get('required_complementary_hours'),
              'complementaryHoursRemaining':max(0,rules.get('required_complementary_hours',0)-approved_hours),
              'requiresInternship':rules.get('requires_internship')}}
