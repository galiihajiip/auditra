"""Data quality validation at each pipeline stage."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from pipeline.config import load_config


@dataclass
class ValidationResult:
    stage: str
    path: str
    passed: bool = True
    checks: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def ok(self, msg: str) -> None:
        self.checks.append(f"OK  {msg}")

    def fail(self, msg: str) -> None:
        self.errors.append(msg)
        self.passed = False

    def summary(self) -> str:
        lines = [f"=== Validation: {self.stage} ===", f"File: {self.path}"]
        lines.extend(self.checks)
        if self.errors:
            lines.append("ERRORS:")
            lines.extend(f"  - {e}" for e in self.errors)
        lines.append(f"Result: {'PASS' if self.passed else 'FAIL'}")
        return "\n".join(lines)

