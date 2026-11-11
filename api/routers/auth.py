import re

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from api.appdb import db
from api.auth import (
    check_login_rate,
    current_user,
    hash_password,
    make_token,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=120)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: str = Field(max_length=120)
    password: str = Field(max_length=128)


def _session(user: dict) -> dict:
    return {"token": make_token(user["id"]), "user": user}


@router.post("/register", status_code=201)
def register(body: RegisterIn):
    email = body.email.strip().lower()
    if not _EMAIL.match(email):
        raise HTTPException(status_code=422, detail="Format email tidak valid.")
    with db() as conn:
        if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            raise HTTPException(status_code=409, detail="Email sudah terdaftar.")
        # pendaftaran publik selalu 'auditor'; reviewer hanya dibuat admin/seed (pemisahan tugas)
        cur = conn.execute(
            "INSERT INTO users(email,name,role,password_hash) VALUES (?,?,?,?)",
            (email, body.name.strip(), "auditor", hash_password(body.password)),
        )
        user = {"id": cur.lastrowid, "email": email, "name": body.name.strip(), "role": "auditor"}
    return _session(user)


@router.post("/login")
def login(body: LoginIn, request: Request):
    email = body.email.strip().lower()
    check_login_rate(f"{request.client.host if request.client else '?'}|{email}")
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Email atau kata sandi salah.")
    user = {k: row[k] for k in ("id", "email", "name", "role")}
    return _session(user)


@router.get("/me")
def me(user: dict = Depends(current_user)):
    return user
