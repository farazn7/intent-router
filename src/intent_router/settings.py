"""Local paths shared by ingestion and retrieval."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    documents_dir: Path
    artifacts_dir: Path


def load_settings() -> Settings:
    """Read .env from the working directory; existing environment values win.

    Run from the repository root so default paths resolve inside the project.
    """
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
    return Settings(
        documents_dir=Path(os.getenv("DOCUMENTS_DIR", "data/documents")),
        artifacts_dir=Path(os.getenv("ARTIFACTS_DIR", "artifacts")),
    )
