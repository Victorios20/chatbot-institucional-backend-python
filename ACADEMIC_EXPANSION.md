# Ampliação acadêmica do protótipo

Esta versão usa dados fictícios e regras confirmadas pela equipe do TCC; não integra registros oficiais da UNIFOR. Mantém FastAPI/Python, PostgreSQL/Neon, Gemini e Next.js/Vercel, com backend no Render gratuito.

## Regras confirmadas

- Escala: 0 a 10. Nota pendente é NULL; zero registrado entra nos cálculos.
- MI = (AV1 + AV2) / 2. MI < 4: reprovação direta. A nota demonstrativa de encerramento é MI nesse caso.
- MI >= 4: AV3 obrigatória, inclusive quando MI é alta.
- AV3 < 4: reprovação por regressão, independentemente da média final.
- MF = (MI + AV3) / 2. MF deve ser >= 5, além de frequência mínima da disciplina.
- AV3 necessária = max(4, 10 - MI), somente com MI >= 4 e AV1/AV2 disponíveis.
- Disciplinas explicitamente de nota única: nota mínima 6 e frequência mínima, conforme documento recebido. Não se aplica AV3.
- PMG: média simples de médias finais de tentativas encerradas. Inclui reprovações, zeros e repetições; exclui notas pendentes e tentativas em curso. Cálculo com Decimal antes do arredondamento de exibição.
- Uma aprovação em tentativa ainda aberta não significa disciplina concluída. Progresso e pré-requisitos exigem tentativa encerrada aprovada.

## Dados e migrações

V1–V4 preservam os dados existentes. V5/V6 incorporam as tabelas e documentos de suporte recebidos (financeiro, bolsas, atividades, calendário, estágio e presença detalhada). V7 adiciona períodos, matriz, pré-requisitos, tentativas por período, turmas, horários e matrícula em turmas; vincula avaliações às tentativas. V8 vincula notas existentes e adiciona o catálogo e histórico demonstrativos dos seis cursos. V9 cria alunos fictícios iniciante e concluinte. V10 esclarece o metadado de peso efetivo da AV3: a fórmula confirmada equivale a (AV1+AV2+2*AV3)/4, sem introduzir pesos por créditos na PMG.

Não há exclusão de registros de alunos. As notas recebidas são preservadas; vagas de avaliações sem lançamento usam NULL. O migrador executa arquivos em ordem numérica e em transação. Em bancos legados sem registro de migrações, somente V1–V4 podem ser reconhecidas como baseline; V5 em diante precisam executar.

Scripts:

- `python -m app.db.migrate`: aplica migrações usando DATABASE_URL (conexão direta para migração).
- `python scripts/generate_demo_migration.py`: regenera somente a fixture V8 antes de seu uso inicial. Não modificar migrações já aplicadas; mudanças posteriores exigem uma nova versão.
- `PYTHONPATH=. python scripts/verify_academic_data.py`: valida consultas e perfis; somente leitura.
- `python -m unittest discover -s tests -v`: casos de limite das regras e classificação de intenções.

## RAG e conversa

Intenções adicionais: PMG/evolução, histórico, matriz, pré-requisitos, oferta, horários e progresso. Consultas sempre usam a matrícula da sessão autenticada, nunca uma matrícula fornecida na pergunta. Perguntas curtas podem recuperar a disciplina mencionada na conversa; o Gemini recebe no máximo as 12 mensagens mais recentes. O armazenamento limita a 24 mensagens por sessão. A sessão permanece em memória e pode expirar em reinício do Render.

Cálculos acadêmicos são feitos no Python, não pelo Gemini. Simulações com notas AV1/AV2/AV3 explicitamente digitadas são calculadas sem alterar registros. Respostas objetivas de notas, PMG, histórico, matriz, pré-requisitos, ofertas, horários, progresso e saldos de horas complementares e créditos optativos são formatadas diretamente a partir dos resultados do Python para evitar inconsistência e demora. Perguntas conceituais e abertas usam Gemini com documentos e histórico; cada chamada tem limite de 25 segundos. Se o modelo principal atingir a cota ou falhar, tenta `gemini-3.1-flash-lite` na mesma integração, modelo listado com faixa gratuita na documentação oficial (https://ai.google.dev/gemini-api/docs/pricing). A lista de reserva pode ser configurada por `GEMINI_FALLBACK_MODELS`; por padrão há somente esse modelo de reserva. Não habilita faturamento. Falhas de quota entram em espera de 15 minutos por processo. Se ambos falharem, retorna apenas fatos recuperados e orientações cadastradas, sem inventar uma explicação.

A matriz é reduzida e demonstrativa. O percentual e os créditos da matriz não constituem previsão oficial de formatura. Requisitos gerais de optativas do perfil e horas complementares são apresentados separadamente. A elegibilidade considera pré-requisitos, vagas, disciplina já concluída, matrícula existente e conflitos de horários no mesmo período. A próxima aula usa recorrência semanal em America/Fortaleza; feriados/cancelamentos sem cadastro não são inferidos.

## Contas e perguntas para demonstração

Senha de todas as contas fictícias: `senha`.

- `2310000`: curso de Computação, notas em andamento e histórico aprovado; PMG 8,13 (soma 32,50 / 4).
- `2310001`: reprovações, frequência insuficiente e repetição aprovada; PMG 5,80 (soma 29 / 5).
- `2610090`: iniciante, sem PMG por não possuir tentativas encerradas.
- `1910091`: próximo de concluir a matriz demonstrativa; apenas Inteligência Artificial em andamento.
- As demais contas existentes dos seis cursos também possuem matriz, ofertas e histórico.

Exemplos: “Quais minhas notas em Banco de Dados?”, “E quanto preciso tirar na AV3 nela?”, “Qual minha PMG e evolução por semestre?”, “Quais disciplinas já concluí?”, “Quais os pré-requisitos de Inteligência Artificial?”, “Quais matérias posso cursar em 2027.1?”, “Qual minha próxima aula?”, “Quais optativas existem?”, “Quanto do curso concluí?”, “Quantas horas complementares faltam?”, “Se eu tirar AV1 4, AV2 4 e AV3 4, passo?”.
