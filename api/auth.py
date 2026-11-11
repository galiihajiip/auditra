"""Autentikasi: scrypt password hash + token bertanda tangan HMAC (tanpa dependensi tambahan)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import Depends, Header, HTTPException

from api.appdb import APP_DB_PATH, db

TOKEN_TTL = 60 * 60 * 12  # 12 jam


def _secret() -> bytes:
    env = os.getenv("AUDITRA_SECRET")
    if env:
        return env.encode()
    path = Path(APP_DB_PATH).with_suffix(".secret")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(secrets.token_hex(32))
        try:
            path.chmod(0o600)
        except OSError:
            pass
    return path.read_text().strip().encode()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, dk = stored.split("$")
        calc = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
        return hmac.compare_digest(calc.hex(), dk)
    except Exception:
        return False


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def make_token(user_id: int) -> str:
    payload = _b64(json.dumps({"uid": user_id, "exp": int(time.time()) + TOKEN_TTL}).encode())
    sig = _b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def read_token(token: str) -> int | None:
    try:
        payload, sig = token.split(".")
        good = _b64(hmac.new(_secret(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, good):
            return None
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if data["exp"] < time.time():
            return None
        return int(data["uid"])
    except Exception:
        return None


# ── rate limit login (per IP+email, in-memory) ───────────────────────────────
_attempts: dict[str, deque] = defaultdict(deque)


def check_login_rate(key: str, limit: int = 8, window: int = 300) -> None:
    now = time.time()
    q = _attempts[key]
    while q and q[0] < now - window:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(status_code=429, detail="Terlalu banyak percobaan login. Coba lagi beberapa menit.")
    q.append(now)


def reset_rate_limits() -> None:
    _attempts.clear()


# ── dependencies ─────────────────────────────────────────────────────────────
def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Perlu login.")
    uid = read_token(authorization[7:].strip())
    if uid is None:
        raise HTTPException(status_code=401, detail="Sesi tidak valid atau kedaluwarsa. Silakan login lagi.")
    with db() as conn:
        row = conn.execute("SELECT id,email,name,role FROM users WHERE id=?", (uid,)).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Pengguna tidak ditemukan.")
    return dict(row)


def require_role(*roles: str):
    def dep(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Peran Anda tidak diizinkan untuk aksi ini.")
        return user

    return dep


def seed_demo_users() -> None:
    """Akun demo (juri): hanya dibuat bila belum ada pengguna sama sekali."""
    with db() as conn:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            return
        for email, name, role in (
            ("auditor@auditra.demo", "Dewi Auditor", "auditor"),
            ("reviewer@auditra.demo", "Raka Reviewer", "reviewer"),
        ):
            conn.execute(
                "INSERT INTO users(email,name,role,password_hash) VALUES (?,?,?,?)",
                (email, name, role, hash_password("auditra2026")),
            )
