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


def _read_csv(path: Path, nrows: int | None = None) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False, nrows=nrows)


def validate_raw(path: Path | None = None) -> ValidationResult:
    cfg = load_config()
    path = path or Path(cfg["paths"]["raw"])
    res = ValidationResult(stage="raw", path=str(path))

    if not path.exists():
        res.fail(f"File tidak ditemukan: {path}")
        return res

    df = _read_csv(path, nrows=5000)
    res.ok(f"Sample readable ({len(df):,} baris di-sample)")

    required = {"id", "paket", "metode", "lembaga", "pagu", "lokasi"}
    missing = required - set(df.columns)
    if missing:
        res.fail(f"Kolom wajib hilang: {sorted(missing)}")
    else:
        res.ok(f"Kolom wajib ada: {sorted(required)}")

    null_id = df["id"].isnull().sum() if "id" in df.columns else 0
    if null_id:
        res.fail(f"id null pada sample: {null_id}")
    else:
        res.ok("id tidak null (sample)")

    return res


