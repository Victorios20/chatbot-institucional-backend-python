# Experiência do chat e feedback — 27/10/2026

## Contratos e responsabilidades
- `chat_presentation.py`: cartões montados a partir das notas e médias já calculadas pelo backend; sugestões de continuidade sem chamada ao modelo.
- `academic_answers.py`: texto compatível com clientes anteriores e apresentação opcional para o frontend atual. O frontend não calcula notas nem interpreta números de respostas livres.
- `chat_repository.py`: respostas persistidas e feedback com consultas parametrizadas e escopo obrigatório do aluno autenticado.
- `schemas.py`: validação dos contratos, UUIDs, avaliações permitidas e limite de 4.000 caracteres.
- Frontend: `use-academic-chat.ts` coordena sessão, envio e reenvio; `chat-answer.tsx` apresenta dados, copia texto e registra avaliação. O proxy do servidor preserva o contrato e não armazena respostas em cache.

## API
- GET /chat/session com Authorization: Bearer <sessionId>: retorna apenas nome, curso e semestre do próprio aluno.
- POST /chat/message: sessionId, message, requestId opcional UUID. Retorna response, messageId, presentation opcional e suggestions.
- POST /chat/feedback: sessionId, messageId e rating (helpful/not_helpful). Somente o dono da resposta pode avaliar. Reavaliar atualiza o voto existente.

## Persistência e reenvio
V12 cria chatbot_responses e chatbot_response_feedback. Cada resposta tem UUID; o par aluno/requestId é único. Reenvio de uma solicitação já concluída recupera a resposta salva, sem outra geração nem duplicação do histórico. Reutilizar o identificador com outra pergunta retorna conflito. A garantia cobre respostas já persistidas, não promete execução única de chamadas simultâneas ainda em andamento.
Não são persistidos senhas, tokens de sessão nem chaves do modelo nessas tabelas. Os registros de alunos permanecem os dados fictícios do TCC; os avisos de demonstração não aparecem no atendimento.

## Interface
Cartões por matéria, médias e situação destacadas; sugestões sem corte, recolhíveis em celular/janelas baixas; cabeçalhos compactos; campo de mensagem acessível; carregamento textual e animação; nome/curso/semestre; copiar e avaliar; sugestões por assunto e disciplina. Texto livre aceita apenas formatação simples por React, sem injeção de HTML. Erros permitem reenvio com o mesmo identificador. A rolagem respeita quem está lendo mensagens anteriores e oferece acesso à última mensagem.

## Avaliação do TCC
Uma avaliação por resposta; votos podem ser atualizados. Para consolidar: SELECT rating, count(*) FROM chatbot_response_feedback GROUP BY rating. A identificação é vinculada ao cadastro do aluno; não se trata de pesquisa anônima.

## Publicação
Migração antes do backend; backend antes do frontend. Ambos preservam o campo response usado pelo cliente anterior. Publicar sem chamadas de teste ao Gemini. O usuário pediu para interromper os testes e fará a validação no site; após esse pedido, acompanhar somente o estado das publicações.
