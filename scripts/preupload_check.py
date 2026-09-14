#!/usr/bin/env python3
"""SESTER PyPI-öncesi son-güvenlik turu — tek-komut fail-loud denetim.

Koşum: `.venv/bin/python scripts/preupload_check.py [--skip-sweep]
Çıktı: her-kontrol OK/RED; ilk RED'de exit 1 (sessiz-geçiş yok).

Kontroller:
  1) dist/ içerik: tam-1 sürümün wheel+sdist çifti var mı (sürüm-karışıklığı yok)
  2) sürüm-senkronu: pyproject == sester.__version__ == dist dosya-adı sürümü
  3) metadata-sağlığı: wheel METADATA'da Name/Version/License/Requires-Python/description
  4) wheel-içerik: `sester/` paketi var; iç-örgü-artifaktı yok (sweep-özeti)
  5) sdist-üye-envanteri: only-include disiplini (26-dosya-klassı; test/plan yok)
  6) twine check (araç varsa)
  7) kamusal-yüzey sweep (yoksa --skip-sweep ile atlanır)
"""
from __future__ import annotations

import configparser
import re
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

_errors: list[str] = []


def ok(msg: str) -> None:
    print(f"OK  {msg}")


def red(msg: str) -> None:
    _errors.append(msg)
    print(f"RED {msg}")


def check_dist_pair() -> tuple[str, Path, Path]:
    wheels = sorted(DIST.glob("sester-*.whl"))
    sdists = sorted(DIST.glob("sester-*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        red(f"dist/ çift-değil: {len(wheels)} wheel, {len(sdists)} sdist — "
            "`rm -rf dist && python -m build` ile taze-üret")
        return "", Path(), Path()
    wv = re.match(r"sester-(.+)-py3-none-any\.whl", wheels[0].name)
    sv = re.match(r"sester-(.+)\.tar\.gz", sdists[0].name)
    if not wv or not sv or wv.group(1) != sv.group(1):
        red(f"wheel/sdist sürüm-uyuşmazlığı: {wheels[0].name} != {sdists[0].name}")
        return "", wheels[0], sdists[0]
    ok(f"dist/ çift-uyumlu: sester-{wv.group(1)} (wheel + sdist)")
    return wv.group(1), wheels[0], sdists[0]


def check_version_sync(version: str) -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.M)
    init = (ROOT / "sester" / "__init__.py").read_text(encoding="utf-8")
    n = re.search(r'__version__\s*=\s*"([^"]+)"', init)
    if not m or not n:
        red("sürüm-alanı okunamadı")
        return
    if not (m.group(1) == n.group(1) == version):
        red(f"sürüm-üçlüsü uyumsuz: pyproject={m.group(1)} "
            f"__init__={n.group(1)} dist={version}")
    else:
        ok(f"sürüm-üçlüsü senkron: {version}")


def check_metadata(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as zf:
        meta_name = next(n for n in zf.namelist() if n.endswith("METADATA"))
        meta = zf.read(meta_name).decode("utf-8", "replace")
    needed = {
        "Name:": r"^Name: sester$",
        "Version:": rf"^Version: {re.escape(_version)}$",
        "License-Expression:": r"^License-Expression: Apache-2\.0",
        "Requires-Python:": r"^Requires-Python: >=3\.11$",
        "Summary:": r"^Summary: .+",
    }
    for label, pat in needed.items():
        if re.search(pat, meta, re.M):
            ok(f"METADATA {label} yerinde")
        else:
            red(f"METADATA {label} eksik/uyuşmuyor (beklenen /{pat}/)")
    if "License-File: LICENSE" in meta or "Classifier: License" in meta:
        ok("METADATA lisans-dosyası bağlı")
    else:
        red("METADATA License-File eksik")


def check_wheel_contents(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as zf:
        names = zf.namelist()
    mods = {n.split("/")[0] for n in names}
    if "sester" in mods:
        ok(f"wheel `sester/` paketi taşıyor ({len(names)} üye)")
    else:
        red(f"wheel'de sester/ yok — üye-kökleri: {sorted(mods)}")
    junk = [n for n in names if re.search(
        r"(_cellE|_panel_check|logo\.png|\.pbm$|HAT_DEFTER|AGENT_MESH|01_unicorn)", n)]
    if junk:
        red(f"wheel'de iç-artifakt: {junk[:5]}")
    else:
        ok("wheel iç-artifakt = 0")


def check_sdist_members(sdist: Path) -> None:
    with tarfile.open(sdist) as tf:
        names = [m for m in tf.getnames()]
    top = {n.split("/")[1] if "/" in n else n for n in names}
    # hatchling sdist'e standart .gitignore ekler (içerik örgü-bilgisi taşımaz)
    allowed_roots = {"sester", "README.md", "LICENSE", "pyproject.toml",
                     "PKG-INFO", ".gitignore"}
    extras = {t for t in top if t not in allowed_roots}
    if extras:
        red(f"sdist'te only-include-dışı kökler: {sorted(extras)}")
    else:
        ok(f"sdist envanteri temiz ({len(names)} dosya; yalnız dağıtım-gerçeği)")
    forbidden_members = [n for n in names if re.search(
        r"(tests/|docs/|brand/|KAGIT|IS_PLANI|KARAR_63B|ARASTIRMA|SPEC_FARK|PRD\.md)", n)]
    if forbidden_members:
        red(f"sdist'te iç-belge/test taşıması: {forbidden_members[:5]}")
    else:
        ok("sdist iç-belge/test taşıması = 0")


def check_twine() -> None:
    r = subprocess.run([sys.executable, "-m", "twine", "check", "dist/*"],
                       capture_output=True, text=True, shell=False,
                       cwd=ROOT)
    out = r.stdout + r.stderr
    if r.returncode == 0 and "PASSED" in out:
        n = out.count("PASSED")
        ok(f"twine check PASSED ({n} artefakt)")
    else:
        red(f"twine check başarısız: {out.strip()[:300]}")


def check_sweep() -> None:
    r = subprocess.run([sys.executable, "scripts/public_surface_sweep.py"],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode == 0:
        ok("kamusal-yüzey sweep: sdist iç-ad = 0")
    else:
        red(f"sweep RED: {r.stdout.strip()[:400]}")


if __name__ == "__main__":
    skip_sweep = "--skip-sweep" in sys.argv
    print("== SESTER PyPI-öncesi son-güvenlik turu ==")
    _version, wheel, sdist = check_dist_pair()
    if _version:
        check_version_sync(_version)
        check_metadata(wheel)
        check_wheel_contents(wheel)
        check_sdist_members(sdist)
        check_twine()
        if not skip_sweep:
            check_sweep()
    if _errors:
        print(f"\nSONUÇ: RED ({len(_errors)} kusur) — UPLOAD YAPMA:")
        for e in _errors:
            print(f"  - {e}")
        sys.exit(1)
    print("\nSONUÇ: TAMAM — `twine upload dist/sester-<VERSION>*` için eşik temiz. "
          "(Son-teyit: sürüm-no'yu iki kez oku — PyPI tek-yönlüdür.)")
