"""SESTER signer testleri — v0.7.0 imzalama-arayüzü sözleşmesi.

Kapsam: non-custodial sözleşme (Sester anahtar görmez — Signer sınıfı
anahtar-tutar ama Sester'e sadece hazır-yük döner), hazırlama-determinizmi,
fail-closed (prepare/broadcast patlaması → SettlementError, sessiz-kabul-asla),
prepare-only vs broadcast modları, batch-digest bağlantısı.
"""

from __future__ import annotations

import pytest

from sester.ledger import Ledger
from sester.settlement import SettlementError, build_settlement_batch
from sester.signer import (
    PreparingSigner,
    ResultTransport,
    Signer,
    build_signed_settlement,
)

CHAIN = 8453
CONTRACT = "0x" + "0c" * 20
FROM = "0x" + "f4" * 20


@pytest.fixture()
def led(tmp_path):
    l = Ledger(tmp_path / "signer.sqlite3", secret="signer-test")
    # 3 receipt → batch-eşiği (toplam 0.15)
    for i in range(3):
        l.append("charge_receipt", "0x" + "a1" * 20,
                 "/weather", 0.05, payload={"nonce": f"n{i}"})
    yield l
    l.close()


def _signer_that_exploses() -> Signer:
    class _Boom:
        def prepare(self, batch):
            raise RuntimeError("hsm-erişimi-yok")

    return _Boom()


def test_signer_protocol_runtime_checkable(led):
    assert isinstance(PreparingSigner(), Signer)
    assert not isinstance(object(), Signer)


def test_prepare_only_mode_returns_evidence_without_broadcast(led):
    ev = build_signed_settlement(
        led, "0x" + "a1" * 20, chain_id=CHAIN, contract=CONTRACT,
        from_address=FROM, signer=PreparingSigner())
    assert ev["broadcast"] is False
    assert ev["mode"] == "prepare-only"
    assert ev["result"] is None
    assert ev["raw"]["to"] == CONTRACT
    assert ev["raw"]["data"] == ev["batch"].calldata


def test_prepare_is_deterministic(led):
    a = build_signed_settlement(
        led, "0x" + "a1" * 20, chain_id=CHAIN, contract=CONTRACT,
        from_address=FROM, signer=PreparingSigner())
    b = build_signed_settlement(
        led, "0x" + "a1" * 20, chain_id=CHAIN, contract=CONTRACT,
        from_address=FROM, signer=PreparingSigner())
    assert a["raw"] == b["raw"]
    assert a["digest"] == b["digest"]


def test_broadcast_mode_success(led):
    class _OkTransport:
        def broadcast(self, raw):
            return {"tx_hash": "0x" + "77" * 32, "status": "pending"}

    ev = build_signed_settlement(
        led, "0x" + "a1" * 20, chain_id=CHAIN, contract=CONTRACT,
        from_address=FROM, signer=PreparingSigner(), transport=_OkTransport())
    assert ev["broadcast"] is True
    assert ev["mode"] == "broadcast"
    assert ev["result"]["tx_hash"] == "0x" + "77" * 32


def test_prepare_failure_is_fail_closed(led):
    with pytest.raises(SettlementError, match="hsm-erişimi-yok"):
        build_signed_settlement(
            led, "0x" + "a1" * 20, chain_id=CHAIN, contract=CONTRACT,
            from_address=FROM, signer=_signer_that_exploses())


def test_broadcast_failure_is_fail_closed(led):
    class _Failing:
        def broadcast(self, raw):
            raise ConnectionError("rpc-durdu")

    with pytest.raises(SettlementError, match="rpc-durdu"):
        build_signed_settlement(
            led, "0x" + "a1" * 20, chain_id=CHAIN, contract=CONTRACT,
            from_address=FROM, signer=PreparingSigner(), transport=_Failing())


def test_non_dict_prepare_output_rejected(led):
    class _Bad:
        def prepare(self, batch):
            return "not-a-dict"

    with pytest.raises(SettlementError, match="dict döndürmeli"):
        build_signed_settlement(
            led, "0x" + "a1" * 20, chain_id=CHAIN, contract=CONTRACT,
            from_address=FROM, signer=_Bad())


def test_non_dict_broadcast_output_rejected(led):
    class _Bad:
        def broadcast(self, raw):
            return 42

    with pytest.raises(SettlementError, match="dict döndürmeli"):
        build_signed_settlement(
            led, "0x" + "a1" * 20, chain_id=CHAIN, contract=CONTRACT,
            from_address=FROM, signer=PreparingSigner(), transport=_Bad())


def test_digest_binds_batch_and_payload(led):
    ev = build_signed_settlement(
        led, "0x" + "a1" * 20, chain_id=CHAIN, contract=CONTRACT,
        from_address=FROM, signer=PreparingSigner())
    # digest, batch-özeti + ham-yükün birleşimine bağlı — biri değişse değişir
    import hashlib
    expected = hashlib.sha256(
        (ev["batch"].sha_digest + "|" + str(sorted(ev["raw"].items()))).encode()
    ).hexdigest()
    assert ev["digest"] == expected
