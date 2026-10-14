# Listen/TTS Feasibility Comparison

Perbandingan solusi Text-to-Speech untuk fitur "Listen" di inovasi.or.id. **Ini fitur tambahan, BUKAN pengganti kepatuhan WCAG.**

---

## Kriteria Perbandingan

| Kriteria | Bobot | Deskripsi |
|----------|-------|-----------|
| Bahasa EN/ID | 25% | Kualitas suara Indonesia & Inggris, naturalness |
| Kualitas Suara | 20% | Prosody, intonation, pronunciation accuracy |
| Highlight Sync | 15% | Text highlighting synchronized dengan audio |
| Biaya | 15% | Setup + recurring (per char / per month / per request) |
| Privasi/Data | 10% | Data dikirim ke mana, GDPR/PDPA compliance |
| Maintenance | 10% | Update, monitoring, vendor lock-in |
| Integrasi | 5% | Mudah diembed, API, WordPress/headless support |

---

## Opsi 1: ReadSpeaker (Enterprise SaaS)

| Aspek | Detail |
|-------|--------|
| **Bahasa EN/ID** | ✅ Native ID & EN voices (multiple), high quality |
| **Kualitas Suara** | ⭐⭐⭐⭐⭐ Neural TTS, sangat natural |
| **Highlight Sync** | ✅ Built-in word/sentence highlighting, customizable |
| **Biaya** | 💰💰💰 Enterprise: ~$2,000-5,000+/tahun tergantung volume. Trial available. |
| **Privasi** | ☁️ Cloud-based, data dikirim ke server ReadSpeaker (EU/US). DPA available. |
| **Maintenance** | ✅ Fully managed, auto-update voices, SLA |
| **Integrasi** | ✅ JS embed, WordPress plugin, REST API, SDK |
| **Keunggulan** | Production-ready, accessibility compliant (WCAG 2.1), dedicated support, LMS integration |
| **Kekurangan** | Mahal, vendor lock-in, cloud dependency |

**Skor Estimasi**: 85/100

---

## Opsi 2: Web Speech API (Browser Native)

| Aspek | Detail |
|-------|--------|
| **Bahasa EN/ID** | ⚠️ Bergantung OS/Browser. Chrome/Edge: ID & EN OK. Firefox: terbatas. Safari: ID buruk. |
| **Kualitas Suara** | ⭐⭐⭐ Bervariasi: Chrome/Edge neural voices bagus, Safari robotic |
| **Highlight Sync** | ⚠️ Manual implement: `onboundary` event untuk word/sentence, butuh custom code |
| **Biaya** | 🆓 **GRATIS** - no server cost |
| **Privasi** | 🔒 **Lokal** - processing di device user, zero data keluar |
| **Maintenance** | ✅ Zero - browser handles, tapi voice availability berubah per update |
| **Integrasi** | ✅ Simple JS API (`speechSynthesis`), tapi butuh polyfill untuk highlight |
| **Keunggulan** | Gratis, privasi maksimal, no dependency, offline-capable |
| **Kekurangan** | Inconsistent across browser/OS, no ID voice di Safari/Firefox mobile, limited voice selection, no SSML support penuh |

**Skor Estimasi**: 60/100

---

## Opsi 3: Cloud TTS (Google Cloud TTS / Azure Speech / AWS Polly)

| Aspek | Google Cloud TTS | Azure Speech | AWS Polly |
|-------|------------------|--------------|-----------|
| **Bahasa EN/ID** | ✅ Neural2 (ID: 4 voices), Studio voices | ✅ Neural (ID: 3 voices) | ✅ Neural (ID: 2 voices) |
| **Kualitas Suara** | ⭐⭐⭐⭐⭐ Neural2/Studio sangat natural | ⭐⭐⭐⭐⭐ Natural, SSML support penuh | ⭐⭐⭐⭐ Neural baik, SSML |
| **Highlight Sync** | ✅ Timepoints API (word/sentence timestamps) | ✅ Word-level timestamps | ✅ Speech Marks (word/sentence/viseme) |
| **Biaya** | 💰 Pay-per-char: $16/1M chars (Neural2), $160/1M (Studio) | 💰 $16/1M chars (Neural) | 💰 $16/1M chars (Neural) |
| **Privasi** | ☁️ Cloud, data dikirim ke Google/Azure/AWS. DPA, regional endpoints. | ☁️ Cloud, regional, compliance certs | ☁️ Cloud, regional |
| **Maintenance** | ⚙️ Self-manage: caching, queue, error handling, monitoring | ⚙️ Self-manage | ⚙️ Self-manage |
| **Integrasi** | ✅ REST/gRPC, client libs (JS, Python, etc) | ✅ REST/WS, SDKs | ✅ REST, SDKs |
| **Keunggulan** | Best voice quality, scalable, pay-per-use, timepoints for highlight | Enterprise features, custom voice, real-time streaming | Simple, cheap, good integration |
| **Kekurangan** | Recurring cost, complexity (caching, auth), latency, privacy | Cost, complexity, latency | Fewer ID voices, less natural than GCP/Azure |

**Skor Estimasi**: Google 78/100, Azure 75/100, AWS 70/100

---

## Opsi 4: Self-Hosted Open Source (Piper, Coqui, eSpeak-NG)

| Aspek | Detail |
|-------|--------|
| **Bahasa EN/ID** | ⚠️ Piper: ID voices available (community). Coqui: limited ID. eSpeak: robotic ID. |
| **Kualitas Suara** | ⭐⭐⭐ Piper: good. Coqui: variable. eSpeak: robotic. |
| **Highlight Sync** | ⚠️ Piper: JSON output with timestamps. Custom implementation needed. |
| **Biaya** | 💰 Server cost only (GPU recommended untuk real-time). No per-char fee. |
| **Privasi** | 🔒 **Fully on-premise/self-hosted** - data tidak keluar server Anda |
| **Maintenance** | ⚙️🔧 High: model updates, server ops, scaling, monitoring |
| **Integrasi** | ✅ HTTP API, WebSocket, bisa custom |
| **Keunggulan** | Full control, no vendor lock-in, privacy max, fixed cost |
| **Kekurangan** | Technical debt, voice quality below cloud, setup effort, GPU cost |

**Skor Estimasi**: 55/100

---

## Rekomendasi

### Untuk Produksi (Prioritas Kualitas & Compliance)
> **ReadSpeaker** - Paling turnkey, WCAG-compliant out of the box, support dedicated. Cocok jika budget tersedia dan butuh jaminan aksesibilitas fitur Listen itu sendiri.

### Untuk Budget Terbatas / MVP / Privacy-First
> **Web Speech API + Cloud TTS Fallback** - Hybrid approach:
> - Primary: Web Speech API (gratis, lokal, privacy)
> - Fallback: Cloud TTS (Google/Azure) untuk browser tanpa ID voice (Safari, Firefox mobile)
> - Implement highlight sync via `onboundary` (WSA) / Timepoints (Cloud)
> - Estimasi biaya Cloud: ~$5-20/bulan untuk traffic moderat

### Untuk Full Control & Scale
> **Self-hosted Piper + Cloud Burst** - Self-host primary, burst ke cloud saat peak. Butuh devops capacity.

---

## Estimasi Biaya Tahunan (Asumsi 100K halaman dibaca/bulan, rata-rata 2K chars/halaman = 200M chars/bulan)

| Solusi | Setup | Bulanan | Tahunan | Catatan |
|--------|-------|---------|---------|---------|
| ReadSpeaker | $0 | $200-500+ | $2,400-6,000+ | Enterprise contract |
| Web Speech API | $0 | $0 | $0 | Fallback cloud: +$5-20 |
| Google Cloud TTS (Neural2) | $500 dev | $3,200 | $38,400 | $16/1M chars × 200M |
| Azure Speech (Neural) | $500 dev | $3,200 | $38,400 | Sama |
| AWS Polly (Neural) | $500 dev | $3,200 | $38,400 | Sama |
| Self-hosted Piper (GPU T4) | $2,000 dev | $200-500 | $2,400-6,000 | Server cost only |

---

## PoC Scope (listen-tts/poc/)

Buat 1 file HTML sederhana untuk **1 template** (mis. Artikel Detail) yang demo:
1. Web Speech API dengan highlight sync (word-level via `onboundary`)
2. Fallback ke Cloud TTS (simulasi) jika voice ID tidak tersedia
3. Kontrol: Play, Pause, Stop, Speed, Voice select
4. Keyboard accessible, SR friendly
5. `prefers-reduced-motion` respected (disable auto-play)

File: `listen-tts/poc/index.html`

---

## Keputusan

**Belum diputuskan** - Tunggu persetujuan stakeholder & budget confirmation. Document ini sebagai bahan pembanding.

> **Catatan**: Fitur Listen **tidak menggantikan** SC 1.2.2 (Captions), 1.2.3 (Audio Description), 3.1.5 (Reading Level), atau kebutuhan screen reader. WCAG compliance tetap wajib terpenuhi terpisah.