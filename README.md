# 📷 AI Face + Hand Tracker MAX

Aplikasi desktop computer vision real-time berbasis OpenCV dan Google MediaPipe untuk mendeteksi landmark wajah (FaceMesh 468 titik), estimasi pose kepala (head-pose solvePnP), pengenalan gestur tangan (MediaPipe Tasks Gesture Recognizer), visualisasi motion trails, serta pemicu audio MP3 responsif.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-teal)

---

## ✨ Fitur Utama

- 👤 **FaceMesh 468 Titik**: Pelacakan kontur mata, bibir, iris, dan tessellation dense mesh.
- 📐 **Head Pose Estimation**: Estimasi pitch, yaw, roll sudut kepala via OpenCV `solvePnP`.
- ✋ **Hand & Gesture Recognizer**: Deteksi gestur tangan stabil (voting buffer multi-frame) untuk memicu efek audio (`Selamat.mp3`, `Berjuang.mp3`, `Sukses.mp3`).
- 🎨 **Visual Effects & Enhancement**:
  - Peningkatan kontras adaptif CLAHE.
  - Privacy blur untuk sensor wajah/lingkungan.
  - Motion trail pelacakan tangan.
- 📸 **Capture & Recording**: Screenshot instan dan perekaman video otomatis tersimpan di folder `captures/`.
- 📝 **Event Logger**: Pencatatan riwayat deteksi ke berkas CSV.

---

## ⌨️ Kontrol Keyboard

| Tombol | Fungsi |
|---|---|
| `q` / `ESC` | Keluar dari aplikasi |
| `m` | Mirror / balik frame horizontal |
| `f` | Toggle overlay FaceMesh |
| `h` | Toggle overlay Hand Landmark |
| `d` | Toggle Dense Mesh (tessellation) |
| `a` | Toggle audio pemicu gestur |
| `e` | Toggle CLAHE image enhancement |
| `b` | Toggle Privacy Blur |
| `t` | Toggle motion trail tangan |
| `g` | Toggle auto-snapshot saat gestur terdeteksi |
| `p` | Pause / resume video stream |
| `s` | Ambil screenshot manual |

---

## 🚀 Cara Menjalankan

### 1. Install Dependensi
```bash
pip install -r requirements.txt
```

### 2. Jalankan Program
```bash
# Menggunakan webcam default (device 0)
python main.py

# Atau menggunakan input spesifik / video file
python main.py --source 0
```

---

## 📁 Struktur Direktori

```
AI FACE TRAKER/
├── main.py                    # Entrypoint aplikasi
├── tracker/                   # Modul pelacakan modular
│   ├── app.py                 # Loop utama & event handling
│   ├── camera.py              # Abstraksi webcam OpenCV
│   ├── face.py                # FaceMesh & pose estimator
│   ├── gestures.py            # Stabilizer & recognizer gestur
│   ├── audio.py               # Pemutar audio Pygame / OS fallback
│   ├── drawing.py             # Rendering overlay & HUD
│   └── config.py              # Konfigurasi & parameter default
├── captures/                  # Folder output screenshot/video
├── gesture_recognizer.task    # Model biner MediaPipe
├── requirements.txt           # Dependensi modul Python
└── Master_Memory_Workflow.md  # Dokumentasi arsitektur terpusat
```
