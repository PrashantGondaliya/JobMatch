import subprocess
import sys


def run_command(command: list[str]) -> int:
    completed_process = subprocess.run(command, check=False)

    return completed_process.returncode


def main() -> int:
    print("Running database migrations...")

    migration_exit_code = run_command(
        ["alembic", "upgrade", "head"]
    )

    if migration_exit_code != 0:
        print("Database migration failed.")
        return migration_exit_code

    print("Database migrations completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())