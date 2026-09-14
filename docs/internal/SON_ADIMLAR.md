# SESTER — Son Adımlar (yayın-öncesi konsol-rehberi, 2026-09-14)

> Yazılım/kod/kanıt-tarafı **tamamlandı** (tam-kapı-yeşili, commit `1274a55`,
> Release v0.5.0 canlı). Aşağıdaki maddeler yalnız senin konsol/oturumunda
> yapılabilir — her biri 1–5 dakika, sıra bağımsız.

## 1) Social preview (2 dk) — tek REST'siz madde

GitHub sosyal-kart yükleme REST-API'si olmadığı için konsoldan:

1. Aç: **https://github.com/goun7/Sester** → **Settings** → **General**
2. Sayfayı aşağı kaydır: **Social preview** bölümü
3. **Edit** → eski-kart varsa **Remove** → **Upload an image**
4. Seç: `.github/assets/og.png` (1280×640 — v2 Chain-S kartı; kapı-adımı üretti)
5. Kaydet — Twitter/Slack paylaşım-kartı artık markalı olur

## 2) CI billing (2 dk) + rerun

Son CI-koşumu billing-engeline takıldı (kod-hatası değil):

1. **https://github.com/settings/billing** → spending limit'i kontrol et
   (0 $ ise Actions çalışmaz — düşük bir limit ya da kredi-kartı bağla)
2. Terminalde son-koşumu yeniden koştur:
   ```bash
   gh run list --repo goun7/Sester --limit 3        # engellenen koşum-id'yi bul
   gh run rerun <run-id> --repo goun7/Sester
   ```
3. ~3 dk sonra rozet yeşile döner (README'deki CI-badge canlı görünür)

## 3) PyPI upload (5 dk — geri-alınamaz, ekranı dikkatle oku)

Ön-şartlar zaten kanıtlı: sweep = 0 iç-ad-hit, twine-check PASSED, eşik-kararı
(Açık-çekirdek) senin onayınla kayıtlı.

1. **https://pypi.org/account/register/** — hesap yoksa aç; **2FA'yı mutlaka aç**
2. **https://pypi.org/manage/account/token/** → "Add token" → scope: *Entire
   account* (ilk-yayın) → token'ı kopyala (`pypi-...`)
3. Repo-kökünde:
   ```bash
   .venv/bin/python -m twine upload dist/sester-0.5.0* \
     --repository pypi -u __token__ -p "pypi-BURAYA-TOKEN"
   ```
4. Doğrula:
   ```bash
   python -m venv /tmp/pypicheck && /tmp/pypicheck/bin/pip install sester
   /tmp/pypicheck/bin/python -c "import sester; print(sester.__version__)"
   ```
5. Sonrası: About → **Website** alanına `https://pypi.org/project/sester/`:
   ```bash
   gh repo edit goun7/Sester --homepage "https://pypi.org/project/sester/"
   ```
6. Sürüm-sonrası dev-bump (bir sonraki turda istersen ben yaparım):
   `sester/__init__.py` + `pyproject.toml` → `0.5.1.dev0`

> ⚠️ Sürüm-no'yu iki kez kontrol et (`grep version pyproject.toml`) — PyPI'da
> aynı numara bir daha kullanılamaz. Hata yaparsan 0.5.1 ile devam edilir.

## 4) S6 ortak-turu (Tenderix oturumu — ~30 dk)

Tetik zaten teslim edildi (`S6_KAPI_YESILI_SINYALI.md`); Tenderix'in §4
sırası + bizim koşumcu hazır. Ortak-oturumda:

1. **63-tarafı yerel-kanıt:**
   ```bash
   cd /home/gokun/projects/01_unicorn/63-Sester
   .venv/bin/python scripts/s6_joint_run.py            # deterministik mod
   ```
   Beklenen: S6.a–S6.f senaryoları KABUL + oturum-sonu tek-K0-bundle
   (harici-doğrulayıcı SAĞLAM + settlement-batch net-0)
2. **Canlı-tur (iki taraf ayaktayken):** 63 tarafında facilitator_svc'yi
   ayağa kaldır; 64 kendi escrow-akışını koşturur; ardından
   ```bash
   SESTER_FACILITATOR_URL=https://… SESTER_FACILITATOR_KEY=… \
     .venv/bin/python scripts/s6_joint_run.py --live
   ```
3. **Kapanış:** iki-tarafı yeşil → Tenderix "S6 KAPANDI" beyanını kendi
   repo'suna düşer; HAT DEFTERİ'ne ortak-satır — hat-geneli kabul tamamlanır

## 5) (Public-anı geldiğinde) sıra-koruma

1. PyPI-upload'dan SONRA secret-scanning'i aç (private-planda kapalı):
   Settings → Advanced Security → **Secret scanning + Push protection**
2. Repo görünürlüğü public'e geçtiğinde klasör-taşıma uygulanır
   (karar-kaydı: GATE_RUN_NOTU) — istersen o gün ben taşarım
