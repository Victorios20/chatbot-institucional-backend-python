import argparse
from pathlib import Path

from app.database import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES = [
    PROJECT_ROOT / "migrations",
    PROJECT_ROOT.parent / "chatbot-institucional" / "university-erp-service" / "src" / "main" / "resources" / "db" / "migration",
]


def migration_source() -> Path:
    for source in DEFAULT_SOURCES:
        if source.exists():
            return source
    raise RuntimeError("Nenhuma pasta de migrations encontrada.")


def run_migrations(source: Path) -> None:
    files = sorted(source.glob("V*.sql"))
    if not files:
        raise RuntimeError(f"Nenhuma migration SQL encontrada em {source}")

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS python_schema_migrations (
                version VARCHAR(80) PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
            """
        )
        applied = {
            row["version"]
            for row in conn.execute("SELECT version FROM python_schema_migrations").fetchall()
        }

        schema_already_exists = conn.execute("SELECT to_regclass('public.courses') AS table_name").fetchone()["table_name"]
        if schema_already_exists and not applied:
            for file in files:
                conn.execute(
                    "INSERT INTO python_schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                    (file.stem,),
                )
            print("Banco ja tinha o schema academico. Migrations marcadas como aplicadas.")
            return

        for file in files:
            version = file.stem
            if version in applied:
                continue
            sql = file.read_text(encoding="utf-8")
            for statement in sql.split(";"):
                statement = statement.strip()
                if statement:
                    conn.execute(statement)
            conn.execute("INSERT INTO python_schema_migrations (version) VALUES (%s)", (version,))
            print(f"Aplicada: {file.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Aplica as migrations SQL do backend Python.")
    parser.add_argument("--source", type=Path, default=None, help="Pasta de migrations SQL.")
    args = parser.parse_args()
    source = args.source or migration_source()
    run_migrations(source)


if __name__ == "__main__":
    main()
