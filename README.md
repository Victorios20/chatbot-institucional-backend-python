# Backend Python

Substituto leve para os dois serviços Java de `chatbot-institucional`.

Ele expõe os mesmos endpoints que o front já usa:

- `POST /auth/login` -> retorna `{ "sessionId": "..." }`
- `POST /chat/message` -> retorna `{ "response": "..." }`
- `GET /health`

E também mantém endpoints equivalentes ao ERP para teste/debug:

- `POST /erp/auth/login`
- `POST /auth/refresh`
- `GET /students/me/context`

## Como rodar

```bash
cd "Backend python"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
docker compose up -d
python -m app.db.migrate
python run.py
```

O front atual já aponta para `http://localhost:8080`, então não precisa mudar o `.env.local` dele.

## Banco

O banco continua sendo PostgreSQL, igual ao Java. O `docker-compose.yml` sobe:

- banco: `university_erp`
- usuário: `postgres`
- senha: `postgres`
- porta: `5432`

As migrations para criar o schema acadêmico e popular os dados de teste estão incluídas neste repositório:

```text
migrations/
```

Os arquivos `V1` a `V4` foram recuperados do projeto Java no arquivo
`Projeto Final Integrador 1.zip`, sem alterações. Não é necessário manter o projeto
Java ao lado deste backend. Com o PostgreSQL disponível, execute
`python -m app.db.migrate` para criar e popular o banco.

## Gemini

Configure a chave no `.env`:

```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3-flash-preview
```

Com isso, o fluxo fica:

```text
Front -> Backend Python -> PostgreSQL + Gemini
```

Você não precisa subir os serviços Java nem a API Node da IA para o fluxo principal.

## Credenciais seedadas

- senha padrão: `senha`
- matrículas: `2310000`, `2410002`, `2210004`, `2110006`, `2510008`, `2010010`


## Ampliação acadêmica

Notas individuais, PMG, histórico, matriz, pré-requisitos, oferta, horários e progresso: veja [ACADEMIC_EXPANSION.md](ACADEMIC_EXPANSION.md) para regras, contas fictícias, perguntas e scripts de validação.
