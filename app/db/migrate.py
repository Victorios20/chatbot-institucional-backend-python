import argparse
from pathlib import Path

from app.database import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES = [
    PROJECT_ROOT.parent / "chatbot-institucional" / "university-erp-service" / "src" / "main" / "resources" / "db" / "migration",
    PROJECT_ROOT / "migrations",
]


def migration_number(file: Path) -> int:
    return int(file.stem.split("__", 1)[0].removeprefix("V"))


def migration_files(source: Path | None = None) -> list[Path]:
    if source:
        files = sorted(source.glob("V*.sql"), key=migration_number)
        if files:
            return files

    files_by_version: dict[str, Path] = {}
    for source_path in DEFAULT_SOURCES:
        if not source_path.exists():
            continue
        for file in sorted(source_path.glob("V*.sql"), key=migration_number):
            files_by_version.setdefault(file.stem, file)

    if files_by_version:
        return sorted(files_by_version.values(), key=migration_number)

    raise RuntimeError("Nenhuma pasta de migrations encontrada.")


def run_migrations(files: list[Path]) -> None:
    if not files:
        raise RuntimeError("Nenhuma migration SQL encontrada.")

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
            baseline_files = [file for file in files if migration_number(file) <= 4]
            for file in baseline_files:
                conn.execute(
                    "INSERT INTO python_schema_migrations (version) VALUES (%s) ON CONFLICT DO NOTHING",
                    (file.stem,),
                )
                applied.add(file.stem)
            print("Banco ja tinha o schema academico base. Migrations antigas marcadas como aplicadas.")

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
    run_migrations(migration_files(args.source))


if __name__ == "__main__":
    main()
