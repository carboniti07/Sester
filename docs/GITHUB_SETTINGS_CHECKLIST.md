# SESTER — GitHub Repo-Ayarları Kontrol-Listesi (goun7/sester)

> Amaç: rename-sonrası repoyu **profesyonel vitrin-durumuna** getirmek.
> Her madde ya ☐ konsol-eylemi (tarayıcı) ya da tek-komut (`gh` CLI).
> Not: `PUSH=1 REPO_RENAME=1 bash scripts/publish_gate.sh` zaten About +
> topics'i ayarlıyor — bu liste onun **ötesindeki** ayarlar içindir.

## 1) About (yan-panel "Info") — ✅ otomatik (kapı-adımı 8)

Kapı komutu şunu koşar:

```bash
gh repo edit goun7/sikke --name sester \
  --description "x402-style metering, quota, fail-closed policy and hash-chain receipts for AI-agent APIs — one ASGI middleware" \
  --add-topic x402 --add-topic ai-agents --add-topic metering --add-topic payments \
  --add-topic asgi-middleware --add-topic fintech
```

- ☐ **Website alanı** (About altına URL): PyPI-yayınından SONRA
  `https://pypi.org/project/sester/` — öncesinde boş bırak (ölü-link vitrini
  bozar). `gh repo edit goun7/sester --homepage "https://pypi.org/project/sester/"`

## 2) Görsel-kimlik — ☐ konsol (veya gh ile)

- [x] **Social preview** (yüklendi 2026-09-14): `Settings` → `General` →
      `Social preview` → `.github/assets/og.png` (1280×640).
- [x] **Repo-avatar** (yüklendi 2026-09-14, gh-API ile):
      `.github/assets/avatar.png` (512×512).

## 3) Release — ☐ tek-komut

```bash
# CHANGELOG §0.5.0 metniyle tag + GitHub Release (private repo'da da çalışır):
gh release create v0.5.0 --target main --title "v0.5.0 — identity, S5 facilitator, S6 joint acceptance" \
  --notes "- Identity migration → **sester** (frozen wire fields preserved)\n- S5 hosted-facilitator service (verify/settle/refund + seller metering)\n- S6 joint-acceptance contract + joint runner\n- Payee registry: explicit, digest-bound payee addresses\n- 216 test legs, PG parity zero-skip, live E2E 21/21"
```

## 4) Branch-koruma — ☐ konsol (private repo'da eski-fiyat kuralı değişti; kontrol et)

- `Settings` → `Branches` → `Add branch protection rule` → `main`:
  - ☐ Require a pull request before merging → **kapalı** bırak (tek-geliştirici
    dönemi; kural PR-gerçeğiyle çelişmesin)
  - ☐ Require status checks: `test` (CI job) — CI billing çözülünce işaretle
- ❗ Kendi commit'in: `-m` ile direkt push ediyorsun (kapı Push-adımı);
  koruma-kuralı bunu bloklamasın → şimdilik yalnız status-check şartı,
  merge-kuralı yok.

## 5) Güvenlik-özellikleri — ☐ konsol (2 dakika, itibar-değeri yüksek)

- `Settings` → `Advanced Security` (private repo'da bazıları ücretli; free
  olanlar):
  - [ ] **Dependency graph** (free)
  - [ ] **Dependabot alerts** (private'ta ücretli olabilir — olsa da olsa da
        aç; açılamıyorsa atla, not düş)
  - [ ] **Secret scanning + push protection** (private'ta free değilse
        public-anında mutlaka aç — PyPI-öncesi hatırlatıcı)
- `Security` tab → `Security policy`: SECURITY.md zaten görünecek (✅).

## 6) Actions — ☐ iki madde

- [x] ~~CI billing engeli~~ — **artık gerekli değil:** repo public olduğu
      için GitHub Actions koşumları sınırsız ve ücretsizdir (dakika-limiti
      yalnız private depolarda geçerli). Son koşumlar yeşil.
- [ ] `Settings` → `Actions` → `General` → Workflow permissions →
      **Read repository contents and packages permissions** (yeterli; write
      verme — kapı push'u lokalden yapar).

## 7) PyPI-yayınına bağlı son-adımlar (sıra önemli)

1. ☐ Kamusal-yüzey taraması (yeni script: `scripts/public_surface_sweep.py`
   — kapıya `SWEEP=1` adımı olarak bağlandı) → sıfır-iç-ad kanıtı
2. ☐ `twine upload dist/sester-0.5.0*` (2FA + API-token)
3. ☐ About → homepage: `https://pypi.org/project/sester/` (yukarıdaki komut)
4. ☐ `pip install sester` temiz-venv teyidi
5. ☐ PyPI sonrası: repo **public** kararı — public'e geçerken secret-scanning
   + push-protection İLK açılır, sonra görünürlük değişir.
