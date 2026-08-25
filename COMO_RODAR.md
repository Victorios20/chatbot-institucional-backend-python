# Como rodar o Backend Python

Este backend substitui os serviços Java e a antiga API Node da IA.

Fluxo atual:

```text
Frontend -> Backend Python -> PostgreSQL no Docker + Gemini
```

## Terminal 1: Backend Python

Abra um terminal na pasta do backend:

```powershell
cd "C:\dev\codigos UNIFOR\Projeto Final Integrador 1\CHATBOT-IA\Backend python"
```

Suba o banco PostgreSQL:

```powershell
docker compose up -d
```

Ative o ambiente virtual Python:

```powershell
.\.venv\Scripts\activate
```

Crie/popule as tabelas do banco, se necessario:

```powershell
python -m app.db.migrate
```

Rode o backend:

```powershell
python run.py
```

O backend ficara disponivel em:

```text
http://localhost:8080
```

Para testar se subiu corretamente:

```powershell
Invoke-WebRequest http://localhost:8080/health
```

A resposta esperada e:

```json
{"status":"ok"}
```

## Terminal 2: Frontend

Abra outro terminal e entre na pasta do front:

```powershell
cd "C:\dev\codigos UNIFOR\Projeto Final Integrador 1\CHATBOT-IA\chatbot-institucional - front"
```

Rode o frontend:

```powershell
npm run dev
```

O frontend ficara disponivel em:

```text
http://localhost:3000
```

## Credenciais de teste

```text
matricula: 2310000
senha: senha
```

Outras matriculas seedadas:

```text
2410002
2210004
2110006
2510008
2010010
```

Todas usam a senha:

```text
senha
```

## Finalidade de cada comando

```powershell
cd "...\Backend python"
```

Entra na pasta do backend Python.

```powershell
docker compose up -d
```

Sobe o banco PostgreSQL dentro do Docker. O `-d` deixa o banco rodando em segundo plano.

```powershell
.\.venv\Scripts\activate
```

Ativa o ambiente virtual Python do projeto. Isso faz o terminal usar as dependencias instaladas em `.venv`.

```powershell
python -m app.db.migrate
```

Cria e popula o banco, se ainda nao existir. Esse comando usa as migrations SQL do projeto antigo em Java.

```powershell
python run.py
```

Inicia o servidor FastAPI na porta `8080`.

```powershell
npm run dev
```

Inicia o frontend Next.js na porta `3000`.

## Observacoes importantes

Nao precisa rodar:

```text
backend Java
API Node da IA
```

O backend Python ja faz:

```text
login
consulta no banco
sessao do aluno
chamada ao Gemini
resposta para o front
```

O arquivo `.env` contem configuracoes locais e a chave do Gemini. Ele nao deve ser enviado para o GitHub.

O arquivo `.env.example` serve como modelo para configurar outro computador.
