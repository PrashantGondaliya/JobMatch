import os
import subprocess
import sys


def main() -> int:
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8000")

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        port,
    ]

    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())