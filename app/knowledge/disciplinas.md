# Disciplinas

As disciplinas representam as materias em que o aluno esta matriculado ou que fazem parte do seu curso.

O chatbot pode usar os dados do banco para consultar informacoes das disciplinas do aluno, como nome, professor, carga horaria, frequencia minima, frequencia atual e faltas registradas.

## Informacoes Que Podem Ser Consultadas

Quando estiverem disponiveis no banco, o chatbot pode informar:

- disciplinas em que o aluno esta matriculado;
- nome da disciplina;
- professor responsavel;
- carga horaria;
- frequencia minima exigida;
- frequencia atual;
- faltas registradas;
- duracao da aula;
- relacao da disciplina com o curso do aluno.

## Perguntas Comuns

O aluno pode perguntar:

- quais disciplinas esta cursando;
- quem e o professor de uma disciplina;
- qual a carga horaria de uma disciplina;
- se possui faltas em uma disciplina;
- qual disciplina tem maior risco por frequencia;
- quais materias aparecem no contexto academico atual.

## Disciplina Especifica

Quando o aluno mencionar uma disciplina especifica, o chatbot deve tentar localizar essa disciplina nos dados recuperados do banco.

Exemplo:

```text
Como esta minha frequencia em Banco de Dados?
```

Nesse caso, o backend deve buscar os dados da disciplina Banco de Dados, em vez de enviar todas as disciplinas sem necessidade.

Se a disciplina nao aparecer nos dados do aluno, o chatbot deve informar que nao encontrou essa disciplina entre as informacoes disponiveis.

## Turmas E Horarios

Informacoes de turma e horario devem ser confirmadas nos canais oficiais da universidade, como portal do aluno, coordenacao ou secretaria academica.

Caso o banco nao tenha horario ou turma da disciplina, o chatbot nao deve inventar essa informacao.

## Limites Do Chatbot

O chatbot nao deve:

- matricular aluno em disciplina;
- remover disciplina da matricula;
- trocar turma;
- garantir vaga;
- alterar professor;
- alterar carga horaria;
- inventar horario, sala ou turma;
- confirmar informacao oficial que nao esteja no contexto.

Para mudanca de turma, ajuste de disciplinas, problemas de matricula ou confirmacao oficial de horarios, o aluno deve procurar a coordenacao do curso, secretaria academica, Reitoria ou Unifor Online.
