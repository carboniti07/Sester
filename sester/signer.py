"""SESTER signer — v0.7.0: işlem-imzalama ARAYÜZÜ (non-custodial sözleşme).

K0-tasarım-kuralı (donuk): **Sester anahtar-TUTMAZ.** Bu modül yalnız
imzalayıcılar arası bir sözleşme tanımlar; anahtar-yönetimi tamamen
operatördedir (HSM, imza-servisi, donanım-cüzdan…).

Sözleşme (v1):
    signer.prepare(batch) -> dict
        batch'i imza-hazır yük'e çevir (broadcast edilebilir ham-işlem).
    transport.broadcast(raw) -> dict
        ham-yükü ağa taşır; hata → SettlementError (fail-closed).
    build_signed_settlement(ledger, agent, *, chain_id, contract,
                            from_address, signer, transport=None)
        batch → prepare → (transport varsa) broadcast → kanıt-döndür.

Fail-closed:
    · prepare RuntimeError/Exception → SettlementError (yayın-yok)
    · transport YOK    → kanıt döner ama `broadcast=False` (bilinçli-tepki)
    · broadcast hata   → SettlementError; kanıt yok (sessiz-kabul-asla)
"""

from __future__ import annotations

import hashlib
from typing import Any, Protocol, runtime_checkable

from .settlement import SettlementBatch, SettlementError


@runtime_checkable
class Signer(Protocol):
    """Anahtar-tutan tarafın uygulayacağı arayüz — Sester anahtar görmez."""

    def prepare(self, batch: SettlementBatch) -> dict[str, Any]:
        """batch → ham-işlem-yükü (broadcast-edilebilir).
        Anahtar-kullanımı imzalayıcının sorumluluğudur; Sester görmesin."""
        ...


@runtime_checkable
class ResultTransport(Protocol):
    """Ham-yükü ağa taşıyan taraf (rpc, firehose, imza-servisi…)."""

    def broadcast(self, raw: dict[str, Any]) -> dict[str, Any]:
        """raw-yükü yayınla; hata-olursa Exception → SettlementError."""
        ...


def _raw_payload(batch: SettlementBatch) -> dict[str, Any]:
    """Standart ham-yük: batch'in kanıt-çifti + calldata. Deterministik."""
    return {
        "to": batch.contract,
        "from": batch.from_address,
        "chain_id": batch.chain_id,
        "data": batch.calldata,
        "value": "0x0",
        "sester_batch_digest": batch.sha_digest,
        "sester_merkle_root": batch.merkle_root,
        "sester_event_count": batch.event_count,
    }


class PreparingSigner:
    """Batch'i ham-yük'e hazırlayan imzalayıcı — hazırlama-anında
    deterministik: aynı batch → aynı yük (test-pinned)."""

    def prepare(self, batch: SettlementBatch) -> dict[str, Any]:
        return _raw_payload(batch)


def build_signed_settlement(
    ledger: Any,
    agent_id: str,
    *,
    chain_id: int,
    contract: str,
    from_address: str,
    signer: Signer,
    transport: ResultTransport | None = None,
) -> dict[str, Any]:
    """batch → imza-hazır yük → (ops.) broadcast → kanıt.

    transport YOKSA: kanıt döner, `broadcast: False` (operatör ham-yükü
    kendi kanalıyla yayınlar — non-custodial varsayılan).
    transport VARSA: broadcast sonucu kanıta bağlanır; hata → fail-closed.
    """
    from .settlement import build_settlement_batch  # döngüsel-import önleme

    batch = build_settlement_batch(
        ledger, agent_id,
        chain_id=chain_id, contract=contract, from_address=from_address)

    try:
        raw = signer.prepare(batch)
        if not isinstance(raw, dict):
            raise SettlementError("signer.prepare dict döndürmeli")
    except SettlementError:
        raise
    except Exception as e:
        raise SettlementError(f"signer.prepare hatası: {e}") from e

    evidence: dict[str, Any] = {
        "batch": batch,
        "raw": raw,
        "broadcast": False,
        "result": None,
        "digest": hashlib.sha256(
            (batch.sha_digest + "|" + str(sorted(raw.items()))).encode()
        ).hexdigest(),
        "mode": "prepare-only" if transport is None else "broadcast",
    }

    if transport is None:
        return evidence

    try:
        result = transport.broadcast(raw)
        if not isinstance(result, dict):
            raise SettlementError("transport.broadcast dict döndürmeli")
    except SettlementError:
        raise
    except Exception as e:
        raise SettlementError(f"transport.broadcast hatası: {e}") from e

    evidence["broadcast"] = True
    evidence["result"] = result
    return evidence
