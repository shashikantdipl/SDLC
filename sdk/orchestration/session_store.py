"""SessionStore — in-memory context passing between pipeline agents.

Each pipeline run has a session. Agents write their output to a session key.
Downstream agents read from session keys.

In production, this would be backed by PostgreSQL (migration 006).
For now, in-memory dict + filesystem persistence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SessionStore:
    """In-memory session store with filesystem persistence."""

    def __init__(self, run_id: str, output_dir: Path | None = None) -> None:
        self.run_id = run_id
        self._store: dict[str, str] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._output_dir = output_dir
        if self._output_dir:
            self._output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, key: str, value: str, written_by: str = "system") -> None:
        """Store a document output. Key is the session key (e.g., 'brd_doc')."""
        self._store[key] = value
        self._metadata[key] = {
            "written_by": written_by,
            "written_at": datetime.now(timezone.utc).isoformat(),
            "size_chars": len(value),
        }

    def read(self, key: str) -> str | None:
        """Read a document from the store. Returns None if not written yet."""
        return self._store.get(key)

    def read_many(self, keys: list[str]) -> dict[str, str]:
        """Read multiple documents. Missing keys are excluded."""
        return {k: self._store[k] for k in keys if k in self._store}

    def exists(self, key: str) -> bool:
        """Check if a document has been written."""
        return key in self._store

    def keys(self) -> list[str]:
        """List all written keys."""
        return list(self._store.keys())

    def get_metadata(self, key: str) -> dict[str, Any] | None:
        """Get metadata for a stored document."""
        return self._metadata.get(key)

    def save_to_file(self, key: str, filename: str) -> Path | None:
        """Save a session value to a file in the output directory."""
        if not self._output_dir or key not in self._store:
            return None
        filepath = self._output_dir / filename
        filepath.write_text(self._store[key], encoding="utf-8")
        return filepath

    def summary(self) -> dict[str, Any]:
        """Return session summary."""
        return {
            "run_id": self.run_id,
            "keys_stored": len(self._store),
            "total_chars": sum(len(v) for v in self._store.values()),
            "documents": {
                k: {
                    "size_chars": len(v),
                    "written_by": self._metadata.get(k, {}).get("written_by", "?"),
                    "written_at": self._metadata.get(k, {}).get("written_at", "?"),
                }
                for k, v in self._store.items()
            },
        }
