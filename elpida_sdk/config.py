from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .models import Axiom, Domain, parse_axioms, parse_domains


class ElpidaConfig:
    """Read-only access to canonical Elpida domain/axiom configuration."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[1]
        self.config_path = self.repo_root / "elpida_domains.json"

    def _load_raw(self) -> Dict[str, object]:
        with self.config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def list_domains(self) -> List[Domain]:
        raw = self._load_raw()
        domains = raw.get("domains", {})
        if not isinstance(domains, dict):
            raise ValueError("Invalid domains format in elpida_domains.json")
        return parse_domains(domains)

    def list_axioms(self) -> List[Axiom]:
        raw = self._load_raw()
        axioms = raw.get("axioms", {})
        if not isinstance(axioms, dict):
            raise ValueError("Invalid axioms format in elpida_domains.json")
        return parse_axioms(axioms)

    def list_rhythms(self) -> Dict[str, object]:
        raw = self._load_raw()
        rhythms = raw.get("rhythms", {})
        if not isinstance(rhythms, dict):
            raise ValueError("Invalid rhythms format in elpida_domains.json")
        return rhythms
