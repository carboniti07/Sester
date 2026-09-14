#!/usr/bin/env python3
"""Filo-için ödeme-üretici istemci — ajan-tarafı referans-içeriyesi.

Gerçek-dünyada bu kod ajanın içinde çalışır: her istekten önce taze-nonce
üretilir, MAC hesaplanır, X-Payment başlığı taşınır. Nonce tekrar edilirse
sunucu replay-402 döner (bu bilinçli-bir davranıştır, pinni vardır).

Kullanım:
    export SESTER_FLEET_SECRET="f1-fleet-secret-2026"
    python examples/fleet_lane/send_paid_request.py --agent f1-n1
    python examples/fleet_lane/send_paid_request.py --agent f1-n1 --path /history

Filo-ajanlarında secret'ı env-dosyasından oku; koda gömme.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.error
import urllib.request

BASE = os.environ.get("SESTER_FLEET_BASE", "http://127.0.0.1:8410")
SCHEME = "pugio0"  # DONUK kablo-alanı — değiştirme (identity-migration record)


def paid_header(agent: str, secret: str, amount: str, resource: str,
                nonce: str | None = None) -> str:
    nonce = nonce or f"{agent}-{int(time.time() * 1000)}-{secrets.token_hex(4)}"
    msg = f"{agent}|{nonce}|{amount}|{resource}".encode()
    mac = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
    return f"{SCHEME} {agent}:{nonce}:{amount}:{mac}"


def call(path: str, agent: str, secret: str, amount: str = "0.05",
         header: str | None = None) -> dict:
    req = urllib.request.Request(
        BASE + path,
        headers={
            "X-Sester-Agent": agent,
            "X-Payment": header or paid_header(agent, secret, amount, path),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            body = json.loads(r.read().decode())
            return {"status": r.status, "receipt": r.headers.get("X-Sester-Receipt"),
                    "body": body}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            body = json.loads(body)
        except Exception:
            body = {"raw": body[:200]}
        return {"status": e.code, "error": body.get("error", body)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="f1-n1")
    ap.add_argument("--path", default="/telemetry")
    ap.add_argument("--amount", default="0.05")
    ap.add_argument("--replay", action="store_true",
                    help="aynı zarfı iki-kez gönder (2. → 402 replay-kanıtı)")
    args = ap.parse_args()

    secret = os.environ.get("SESTER_FLEET_SECRET", "f1-fleet-secret-2026")
    nonce = f"{args.agent}-{int(time.time() * 1000)}-{secrets.token_hex(4)}"
    hdr = paid_header(args.agent, secret, args.amount, args.path, nonce)
    out = call(args.path, args.agent, secret, args.amount, header=hdr)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    if args.replay:
        out2 = call(args.path, args.agent, secret, args.amount, header=hdr)
        print("-- replay --")
        print(json.dumps(out2, indent=2, ensure_ascii=False))
