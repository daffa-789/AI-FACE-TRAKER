---
type: memory
kind: project
name: "master-ai-face-traker"
description: "Memory terpusat AI FACE TRAKER — desktop MediaPipe FaceMesh + GestureRecognizer real-time dari webcam, pemicu audio MP3 & screenshot"
scope: project
project: "AI FACE TRAKER"
status: archived
updated: 2026-09-25
tags: ["memory/project", "project/AI FACE TRAKER"]
---

# Master Memory Workflow — AI FACE TRAKER

> Memory terpusat proyek ini, disusun 23 September 2026 langsung dari kode.
> Proyek ini **tidak punya dokumentasi apa pun sebelumnya** — berkas ini adalah sumber utamanya.
> **Koreksi 2026-09-25:** peta tombol di R4 diverifikasi ulang baris-per-baris terhadap `tracker/app.py`
> (5 dari 13 tombol salah) dan dilengkapi fakta reproducibility di R6.

**Lokasi:** `C:\Users\Daffa\Desktop\Folder Space AI\Folder Space Semester 6\AI FACE TRAKER`
**Status:** karya kuliah Semester 6, **edit source terakhir 2026-06-03 23:45**, tanpa README.
**Tidak ada `.git`** di folder ini dan **tidak ada manifest dependensi apa pun**
(`requirements.txt` / `pyproject.toml` / `setup.py` semuanya absen) → **proyek ini tidak reproducible**:
tidak ada yang mencatat versi `mediapipe`/`opencv`/`pygame` yang dipakai, dan tidak ada riwayat
kode yang bisa dipulihkan. Lihat R6.

## R1. Angka Kunci

| Aspek | Nilai |
|---|---|
| Aplikasi | "AI Face + Hand Tracker MAX" v2.0.0 — desktop jendela OpenCV. Judul jendela di `tracker/config.py:6`. Versi **terkonfirmasi**: `__version__ = "2.0.0"` di `tracker/__init__.py:1` — itu satu-satunya sumbernya, ditulis tangan dan tidak ada tag git yang memvalidasi (proyek ini tidak punya git) |
| Stack | Python + `mediapipe` (FaceMesh legacy solutions **dan** Tasks API `GestureRecognizer`) + `opencv-python` + `numpy` + `pygame` (audio; fallback `os.startfile`) |
| Model | `gesture_recognizer.task` (8,3 MB) ada di **folder kerja** — bukan "repo", karena proyek ini tidak punya git. Bila file hilang, `ensure_gesture_model()` (`tracker/gestures.py:42`) mengunduhnya dari `storage.googleapis.com/mediapipe-models/…` → **jalan pertama kali butuh jaringan** |
| Aset audio | `Selamat.mp3`, `Berjuang.mp3`, `Sukses.mp3` |
| Kode | ±1.241 baris Python / 15 file, modular & rapi |
| Dependensi | ❌ **TIDAK ADA `requirements.txt`** — versi `mediapipe`/`opencv` harus ditebak |

## R2. Arsitektur

```
main.py → tracker/app.py (loop utama)
   frame → enhance (CLAHE) → FaceMesh + GestureRecognizer → smoothing
         → GestureStabilizer (voting antar-frame) → audio + screenshot/record
```

Modul di `tracker/`: `config` (argparse + `audio_map`), `camera`, `face`, `gestures`
(`GestureStabilizer`), `smoothing`, `drawing` (overlay/panel + `draw_help`), `output`,
`event_log` (CSV), `stats`, `utils`, `geometry`, **`audio`**.
**Koreksi 2026-09-25:** daftar lama tidak mencantumkan `tracker/audio.py`. Itu bukan modul sepele — lapisan audio
pygame + fallback-nya ada di situ (lihat R6). Total file Python tetap 15 (`main.py` + 14 di `tracker/`,
termasuk `__init__.py`) = 1.241 baris; itu sudah cocok dengan kode.

## R3. Fitur Nyata

Multi-wajah & multi-tangan · CLAHE enhancement · privacy blur · head-pose (`solvePnP`) ·
motion trails · **gesture stabil → trigger MP3** · screenshot & recording mp4/avi ke `captures/` ·
event log CSV · auto-download model (`ensure_gesture_model` dari GCS bila file hilang).

## R4. Cara Menjalankan

```bash
python main.py                 # kamera default (device 0)
python main.py --source 0      # atau path file video
```
### Peta tombol yang BENAR (dibaca ulang dari `tracker/app.py:210-268`, 25 Sep 2026)

| Tombol | Fungsi nyata |
|---|---|
| `q` **atau `ESC`** | keluar loop (`key in (27, ord("q"))`) |
| `m` | **mirror** — balik horizontal frame |
| `f` | **face overlay** on/off |
| `h` | **hand overlay** on/off |
| `d` | **dense mesh** (tessellation FaceMesh) on/off |
| `a` | audio on/off |
| `e` | **enhance / CLAHE** on/off |
| `b` | privacy blur on/off |
| `t` | hand trails on/off |
| `g` | gesture auto-snapshot on/off |
| `p` | pause / resume |
| `s` | screenshot frame ke `--output-dir` |
| `r` | mulai / hentikan rekaman |

**Koreksi 2026-09-25:** versi lama R4 menulis `m` mute · `f` fullscreen · `h` help · `d` debug ·
`e` event log. **Kelima-limanya salah** — dan tidak ada satu pun tombol untuk mute, fullscreen, debug,
atau membuka help. Sumber resmi yang bisa dibaca di aplikasi: panel help itu sendiri di
`tracker/drawing.py:135-140` ("Q/Esc keluar M mirror F face H hand D dense A audio E enhance /
B blur wajah T trail G auto-shot P pause S screenshot R record"), yang cocok 100% dengan kode.
Konsekuensi praktis: panel help **sudah tampil terus** sejak awal (dibuat oleh
`draw_help` saat `--hide-help` tidak dipakai, `tracker/app.py:196`) — menekan `h` karena mengira
itu "help" malah **mematikan overlay tangan**. `ESC` juga sebelumnya tidak terdokumentasi, padahal
itu jalan keluar paling aman di Windows.
**Butuh kamera** (atau video via `--source`). Tidak ada port/server.

## R5. Konvensi

- **100% path relatif** lewat helper `project_path` → proyek ini portable antar mesin, tidak ada path absolut rusak.
- Semua parameter lewat CLI flag ber-default (bukan config file).
- Komentar & pesan `print` Bahasa Indonesia.

## R6. Gotchas & Risiko

- **Tidak reproducible.** Folder ini **tanpa `.git`** dan **tanpa manifest dependensi** — tidak ada
  `requirements.txt`, tidak ada `pyproject.toml`/`setup.py`. Tidak ada catatan versi `mediapipe`,
  `opencv-python`, `numpy`, `pygame` yang dipakai saat itu, dan tidak ada riwayat kode yang bisa
  dipulihkan. Edit source terakhir: **2026-06-03 23:45** (semua file di `tracker/` + `main.py` pada
  timestamp yang sama). Langkah pertama menghidupkan proyek = kunci versi dependensi, dan
  MediaPipe sering *breaking change* antar versi.
- Kode sudah berisi `patch_mediapipe_mapping` (`tracker/drawing.py:12`, dipanggil di
  `tracker/app.py:42`) sebagai workaround migrasi API Tasks — **pertahankan, jangan dihapus.**
- **Jaringan dibutuhkan saat jalan pertama.** `gesture_recognizer.task` (8,3 MB) memang ada di folder,
  tapi `ensure_gesture_model()` (`tracker/gestures.py:42-57`) akan `urlretrieve` dari
  `https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/…`
  kalau file itu tidak ketemu (mis. setelah dipindah tanpa ikut disalin) → di mesin offline gagal
  dengan traceback unduhan, bukan pesan yang jelas.
- **Workaround capture kamera Windows** di `tracker/camera.py:9-24` — undocumented tapi penting,
  jangan "disederhanakan" jadi `VideoCapture(0)` polos:
  `cv2.VideoCapture(idx, cv2.CAP_DSHOW)` (backend DirectShow, hanya di `sys.platform.startswith("win")`),
  `CAP_PROP_FOURCC = MJPG`, dan `CAP_PROP_BUFFERSIZE = 1` (buang antrean frame biar latensi rendah).
  Menghapus salah satu dari trio ini membuat webcam laptop kembali laggy/mogok.
- **Kegagalan audio terlihat seperti kegagalan deteksi.** `tracker/audio.py` mencoba
  `pygame.mixer` → bila gagal (`_ensure_pygame_mixer()` menelan semua exception) jatuh ke
  `os.startfile(path)` khusus Windows → bila itu pun gagal, hanya mencetak
  `Gagal memutar audio: <path>`. Tidak ada exception, tidak ada log ke file, jendela tetap jalan.
  Jadi gesture bisa **terdeteksi benar** tapi terasa "tidak memicu apa-apa". Cek console untuk baris
  itu sebelum menyalahkan recognizer; di mesin tanpa audio device, `os.startfile` akan membuka MP3 di
  player asosiasi file (bukan memutar inline).
- Bukti pernah jalan: `captures/screenshot_20260603_233806.png` ada.
- Tidak ada git = tidak ada jaring pengaman; **buat repo sebelum mengubah kode.**

## R7. Aturan Memory Proyek Ini

Berkas ini satu-satunya memory terpusat proyek. Perubahan berarti dicatat di sini.

---

## Peta Dokumen Proyek

Berkas ini adalah **satu-satunya memory terpusat** untuk proyek `AI FACE TRAKER`.
Perubahan berarti dicatat di sini lewat commit `docs(memory): catat …`.

### Diserap ke arsip di bawah (file aslinya dihapus)
- (tidak ada — proyek ini tidak punya markdown lain untuk diserap)

### Dibiarkan (bukan memory)
- (tidak ada)

---

## Arsip Dokumen Sumber (verbatim)

Isi setiap sumber dipertahankan apa adanya; separator hanya menandai batas antar dokumen.
Diarsipkan saat konsolidasi memory 2026-09-23 (generator satu-kali pakai, sudah dihapus)

<!-- ARCHIVE-BEGIN -->
<!-- ARCHIVE-END -->
