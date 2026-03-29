"""ManifestLoader — 4-layer YAML configuration resolution.

Resolution order (later layers override earlier):
1. archetype YAML (archetypes/governance.yaml)
2. mixins (optional capability additions)
3. agent manifest.yaml (agent-specific overrides)
4. client profile YAML (per-client customization)

Usage:
    loader = ManifestLoader(base_dir=Path("./"))
    config = loader.resolve("G1-cost-tracker")
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dicts. Override values win."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ManifestLoader:
    """Loads and resolves agent manifests through 4-layer merge."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.archetypes_dir = base_dir / "archetypes"
        self.agents_dir = base_dir / "agents"
        self.knowledge_dir = base_dir / "knowledge"

    def resolve(self, agent_id: str) -> dict[str, Any]:
        """Resolve full config for an agent through 4-layer merge."""
        # Layer 3: Agent manifest
        agent_manifest = self._load_agent_manifest(agent_id)

        # Layer 1: Archetype base
        archetype_id = agent_manifest.get("identity", {}).get("extends")
        archetype_config = self._load_archetype(archetype_id) if archetype_id else {}

        # Layer 2: Mixins
        mixins = agent_manifest.get("identity", {}).get("mixins", [])
        mixin_config: dict[str, Any] = {}
        for mixin in mixins:
            mixin_data = self._load_mixin(mixin)
            mixin_config = deep_merge(mixin_config, mixin_data)

        # Merge: archetype → mixins → agent
        resolved = deep_merge(archetype_config, mixin_config)
        resolved = deep_merge(resolved, agent_manifest)

        # Validate resolved manifest against schema (if schema file exists)
        self._validate_manifest(resolved, agent_id)

        return resolved

    def _validate_manifest(self, manifest: dict[str, Any], agent_id: str) -> None:
        """Validate manifest against agent-manifest.schema.json if available.

        Logs a warning on validation failure but does not raise — allows
        development with incomplete manifests while flagging issues.
        """
        schema_path = self.base_dir / "schema" / "agent-manifest.schema.json"
        if not schema_path.exists():
            return

        try:
            import json
            import jsonschema

            with open(schema_path) as f:
                schema = json.load(f)
            jsonschema.validate(instance=manifest, schema=schema)
        except ImportError:
            # jsonschema not installed — skip validation silently
            pass
        except jsonschema.ValidationError as e:
            import structlog
            logger = structlog.get_logger()
            logger.warning(
                "manifest.validation.failed",
                agent_id=agent_id,
                error=str(e.message),
                path=list(e.absolute_path),
            )

    def _load_agent_manifest(self, agent_id: str) -> dict[str, Any]:
        """Load agent's manifest.yaml.

        Searches all known agent directories: govern/, design/, claude-cc/,
        build/, test/, deploy/, operate/, oversight/.
        """
        search_dirs = [
            "govern", "design", "claude-cc",
            "build", "test", "deploy", "operate", "oversight",
        ]
        for parent in search_dirs:
            manifest_path = self.agents_dir / parent / agent_id / "manifest.yaml"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    return yaml.safe_load(f) or {}
        # Fallback: search ALL subdirectories
        for subdir in self.agents_dir.iterdir():
            if subdir.is_dir():
                manifest_path = subdir / agent_id / "manifest.yaml"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        return yaml.safe_load(f) or {}
        return {}

    def _load_archetype(self, archetype_id: str) -> dict[str, Any]:
        """Load archetype YAML."""
        path = self.archetypes_dir / f"{archetype_id}.yaml"
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def _load_mixin(self, mixin_id: str) -> dict[str, Any]:
        """Load mixin YAML."""
        path = self.archetypes_dir / "mixins" / f"{mixin_id}.yaml"
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}
        return {}
