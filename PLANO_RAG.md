# Plano de Implementacao do RAG Hibrido

Este arquivo registra o plano da implementacao do RAG no backend Python.

A ideia e manter a branch `main` estavel e desenvolver tudo na branch:

```text
feature/rag-hibrido
```

O merge para `main` so deve acontecer quando o fluxo estiver funcionando e testado.

## Objetivo

Implementar um RAG hibrido que consiga usar duas fontes:

```text
1. Banco de dados
2. Documentos Markdown em app/knowledge
```

O backend deve identificar varias intencoes dentro da mesma pergunta e buscar apenas os dados relevantes para cada uma.

## Fluxo Desejado

```text
1. Aluno envia pergunta
2. Backend identifica palavras-chave
3. Backend gera uma ou mais intencoes
4. Cada intencao aponta para:
   - uma ou mais consultas no banco
   - um ou mais documentos Markdown
5. Backend executa as consultas
6. Backend recupera trechos dos documentos
7. Backend junta:
   - pergunta original
   - dados relevantes do banco
   - trechos relevantes dos documentos
8. Gemini recebe o contexto filtrado
9. Gemini responde ao aluno
```

## Exemplo

Pergunta:

```text
Tenho faltas em Banco de Dados e isso afeta minha matricula ou financeiro?
```

Intencoes detectadas:

```text
attendance
subjects
enrollment
financial
```

Fontes:

```text
Banco:
- dados da disciplina Banco de Dados
- frequencia atual
- faltas registradas
- minimo exigido

Markdown:
- frequencia.md
- matricula.md
- financeiro.md
```

## Intencoes Iniciais

```text
attendance
subjects
credits
course
financial
enrollment
secretariat
documents
calendar
library
internship
support
out_of_scope
```

## Documentos Iniciais

```text
app/knowledge/frequencia.md
app/knowledge/disciplinas.md
app/knowledge/creditos.md
app/knowledge/curso.md
app/knowledge/financeiro.md
app/knowledge/matricula.md
app/knowledge/secretaria.md
app/knowledge/documentos.md
app/knowledge/calendario.md
app/knowledge/biblioteca.md
app/knowledge/estagio.md
app/knowledge/suporte.md
app/knowledge/fallback.md
```

Status atual:

```text
criado: app/knowledge/matricula.md
criado: app/knowledge/frequencia.md
criado: app/knowledge/financeiro.md
criado: app/knowledge/secretaria.md
criado: app/knowledge/documentos.md
criado: app/knowledge/calendario.md
criado: app/knowledge/notas.md
criado: app/knowledge/disciplinas.md
criado: app/knowledge/curso.md
criado: app/knowledge/creditos.md
criado: app/knowledge/biblioteca.md
criado: app/knowledge/estagio.md
criado: app/knowledge/suporte.md
criado: app/knowledge/fallback.md
pendente: nenhum documento inicial
```

Proximo documento sugerido:

```text
nenhum documento inicial pendente
```

## Arquivos Python Planejados

```text
app/rag/intent_classifier.py
app/rag/query_planner.py
app/rag/document_retriever.py
app/rag/context_builder.py
app/rag/rag_service.py
```

## Melhorias Futuras No Banco De Dados

Estas melhorias nao precisam entrar na primeira versao do RAG, mas devem ficar anotadas para evolucao do projeto.

## Migrations Criadas Para Suporte Ao RAG

As novas alteracoes de banco devem ser feitas por migrations novas, sem editar as migrations antigas herdadas do Java.

Arquivos criados:

```text
migrations/V5__add_rag_support_schema.sql
migrations/V6__seed_rag_support_data.sql
```

A migration `V5` cria uma estrutura mais preparada para consultas padrao do RAG:

```text
curriculum_rules
assessment_models
student_grades
academic_events
financial_records
student_benefits
complementary_activities
internships
class_slots
classes
attendance_records
excused_absences
```

A migration `V6` insere dados leves de exemplo para:

```text
regras curriculares por curso
modelos de avaliacao
notas de alunos
eventos do calendario academico
mensalidades
bolsas/descontos
atividades complementares
estagios
horarios de aula
aulas realizadas
presencas parciais e faltas abonadas
```

### Frequencia Por Aula

Hoje o banco guarda um resumo da frequencia:

```text
current_attendance_percentage
absences_in_hours
minimum_attendance_percentage
workload_hours
class_duration_minutes
```

Isso permite responder com base no resumo atual, mas nao representa chamada aula por aula.

Melhoria futura:

```text
classes
attendances
excused_absences
```

### Horarios A/B/C/D/E/F

A universidade organiza horarios por letras, como A, B, C, D, E e F, nos turnos manha, tarde e noite.

Cada letra equivale a 50 minutos.

Exemplo:

```text
A = 50 minutos
B = 50 minutos
AB = 1 hora e 40 minutos
```

Melhoria futura:

```text
class_slots
```

Possiveis campos:

```text
id
subject_id
weekday
shift
slot_code
starts_at
ends_at
duration_minutes
```

### Presenca Parcial

Em uma aula AB, o aluno pode receber:

```text
AB = presenca completa
A = meia presenca
B = meia presenca
nenhum = falta completa
```

Melhoria futura:

```text
attendance_records
```

Possiveis campos:

```text
id
student_id
class_id
slot_code_attended
minutes_attended
status
```

### Faltas Abonadas Ou Desconsideradas

Algumas ausencias podem nao contar negativamente na frequencia.

Exemplos:

```text
erro no lancamento da chamada
aula para grupo especifico
segunda chamada
atividade nao obrigatoria para todos
ajuste autorizado pelo professor
```

Melhoria futura:

```text
excused_absences
```

Possiveis campos:

```text
id
attendance_record_id
reason
approved_by
approved_at
counts_against_attendance
```

### Calculo Real Da Frequencia

Com essas tabelas, o sistema poderia calcular a frequencia real assim:

```text
minutos presentes / minutos obrigatorios considerados
```

Isso seria mais preciso do que depender apenas do resumo salvo atualmente.

### Dados Financeiros Do Aluno

Hoje o banco nao guarda mensalidades, boletos, pagamentos, bolsas ou descontos.

O RAG pode responder orientacoes financeiras gerais usando `financeiro.md`, mas nao consegue confirmar valores ou pendencias reais sem novas tabelas.

Melhoria futura:

```text
financial_records
invoices
scholarships
discounts
payments
```

Possiveis campos para mensalidades/boletos:

```text
id
student_id
reference_month
amount
due_date
status
payment_date
payment_method
```

Possiveis campos para bolsas/descontos:

```text
id
student_id
benefit_type
percentage
status
valid_from
valid_until
loss_reason
```

Regras futuras possiveis:

```text
atraso de mensalidade pode afetar desconto/bolsa
reprovacao pode afetar desconto/bolsa
regularidade financeira pode impactar rematricula
```

### Notas E Avaliacoes

Hoje o banco nao guarda notas detalhadas como nota unica, AV1, AV2 ou AV3.

O RAG pode responder regras gerais usando `notas.md`, mas nao consegue confirmar a nota real do aluno sem novas tabelas.

Melhoria futura:

```text
assessment_models
assessments
student_grades
```

Possiveis campos para modelos de avaliacao:

```text
id
subject_id
model_type
minimum_average
formula_description
```

Possiveis campos para notas:

```text
id
student_id
subject_id
assessment_name
grade_value
weight
recorded_at
```

Regras futuras possiveis:

```text
nota unica costuma exigir media 6
modelo com AV1, AV2 e AV3 costuma exigir media final 5
AV3 pode ter peso maior
aprovacao depende de nota e frequencia
```

### Matriz Curricular, Optativas E Atividades Complementares

Hoje o banco guarda o curso do aluno e uma quantidade resumida de creditos optativos exigidos/concluidos.

Para responder melhor sobre matriz curricular, horas optativas e atividades complementares, o banco poderia evoluir para guardar regras por curso.

Melhoria futura:

```text
curriculum_rules
optional_requirements
complementary_activities
student_complementary_hours
```

Possiveis campos para regras do curso:

```text
id
course_id
total_semesters
required_optional_hours
required_complementary_hours
requires_internship
```

Possiveis campos para atividades complementares:

```text
id
student_id
activity_type
description
hours
status
approved_by
approved_at
```

Regras futuras possiveis:

```text
cada curso pode ter quantidade diferente de semestres
cada curso pode exigir horas optativas diferentes
cada curso pode exigir atividades complementares diferentes
estagio pode contar ou nao como requisito dependendo do curso
```

## Decisao Atual

Na primeira versao do RAG, vamos manter o schema atual.

O RAG deve usar os dados resumidos que ja existem no banco e os documentos Markdown.

As melhorias de banco ficam registradas para uma etapa futura.
