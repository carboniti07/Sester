# LinkedIn — founder/engineer voice (TR + EN)

## EN post

Shipping something we needed ourselves:

AI agents are starting to pay per API call. The rails exist (x402 and
friends). What's missing is the layer nobody demos: metering, spend limits,
and proof of what was actually spent.

Sester is that layer as one ASGI middleware — zero required dependencies,
stdlib-only core. The design rule that shaped everything: every failure path
denies spend. Corrupt policy file → all spending stops. Unknown payment
scheme → denied, never a free pass. Every charge and denial lands in a
hash-chained ledger that an auditor verifies with plain sha256, no library
needed.

Four agent-commerce protocols compile onto one receipt core. 214 tests
across SQLite and Postgres. Apache-2.0.

→ github.com/goun7/Sester · pypi.org/project/sester

If you're building agent-facing APIs, I'd genuinely like your scrutiny of
the fail-closed paths.

## TR post

Kendi ihtiyacımız için geliştirdiğimiz bir katmanı yayınladık:

AI ajanları artık API-başına ödeme yapabiliyor. Raylar var (x402 ve
arkadaşları). Eksik olan, kimse demo etmeyen katman: ölçüm, harcama-limiti
ve ne harcandığının kanıtı.

Sester tam bu katman — tek ASGI-middleware, çekirdek sıfır-bağımlılık.
Tasarımı şekillendiren tek kural: her hata-yolu harcamayı DURDURUR. Bozuk
politika-dosyası → tüm harcama durur. Bilinmeyen ödeme-şeması → reddedilir.
Her ücret ve red, hash-zincirli deftere düşer; denetçi salt sha256 ile
doğrular.

→ github.com/goun7/Sester · pypi.org/project/sester

Ajan-yönelimli API geliştirenler: fail-closed yolları kırmaya
çalışmanızı gerçekten isterim.
