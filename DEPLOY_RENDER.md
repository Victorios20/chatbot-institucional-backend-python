# Backend no Render Free

Usar somente o plano `free`. Não contratar serviços pagos, discos, bancos
adicionais, upgrades de instância ou planos de workspace pagos.

O `render.yaml` define um único Web Service Python, sem criar banco no Render.
O banco remoto já está no Neon Free: projeto `tcc-chatbot`, banco `university_erp`.
As migrations V1 a V4 já foram aplicadas; não executá-las em todo boot.

## Configuração

- Python 3.12, definido em `.python-version`.
- Build: `pip install -r requirements.txt`.
- Start: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`.
- Health check: `/health` (disponibilidade do processo).
- `DATABASE_URL`: conexão privada do Neon com pooling e `sslmode=require`.
- `JWT_SECRET`: segredo exclusivo do ambiente remoto, gerado na hospedagem.
- `ALLOWED_ORIGIN`: endereço do frontend quando ele for publicado.

Senhas e chaves devem ficar nas variáveis privadas do Render, nunca no YAML
ou em commits. O `.env.neon` local é ignorado pelo Git e fornece a URL do banco.
As configurações do Docker local permanecem separadas.

A chave Gemini não está no Blueprint. Essa integração é configurada
separadamente, após confirmar que o uso da conta/modelo não gera cobranças.

## Verificação

Após publicar, testar `/health` e `/auth/login` com um aluno fictício para
validar a conexão ao Neon. O endpoint de saúde sozinho não testa o banco.

O plano gratuito pode suspender a API após inatividade. Sessões do chatbot
são mantidas em memória e exigem novo login quando o processo reinicia.
Usar um único worker para que as requisições compartilhem as sessões.
