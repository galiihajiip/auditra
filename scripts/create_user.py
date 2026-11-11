"""Buat akun (mis. reviewer) tanpa membuka pendaftaran publik.

    python scripts/create_user.py reviewer@instansi.go.id "Nama Reviewer" reviewer
    (kata sandi diminta interaktif)

Untuk server publik: set AUDITRA_SEED_DEMO=0 dan AUDITRA_SECRET=<string acak panjang>.
"""

import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.appdb import db  # noqa: E402
from api.auth import hash_password  # noqa: E402


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[3] not in ("auditor", "reviewer"):
        sys.exit(__doc__)
    email, name, role = sys.argv[1].strip().lower(), sys.argv[2], sys.argv[3]
    pw = getpass.getpass("Kata sandi (min 8): ")
    if len(pw) < 8:
        sys.exit("Kata sandi terlalu pendek.")
    with db() as conn:
        conn.execute(
            "INSERT INTO users(email,name,role,password_hash) VALUES (?,?,?,?)",
            (email, name, role, hash_password(pw)),
        )
    print(f"OK: {role} {email} dibuat.")


if __name__ == "__main__":
    main()
