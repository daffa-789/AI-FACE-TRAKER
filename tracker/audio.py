import importlib
import os
import sys
import threading


_PYGAME = None
_AUDIO_READY = False
_AUDIO_LOCK = threading.Lock()


def _ensure_pygame_mixer():
    global _PYGAME, _AUDIO_READY
    if _AUDIO_READY:
        return True

    try:
        _PYGAME = importlib.import_module("pygame")
        _PYGAME.mixer.init()
        _AUDIO_READY = True
        return True
    except Exception:
        _PYGAME = None
        _AUDIO_READY = False
        return False


def _play_audio(path):
    if not os.path.exists(path):
        print(f"Audio tidak ditemukan: {path}")
        return

    with _AUDIO_LOCK:
        if _ensure_pygame_mixer():
            try:
                _PYGAME.mixer.music.stop()
                _PYGAME.mixer.music.load(path)
                _PYGAME.mixer.music.play()
                return
            except Exception:
                pass

    if sys.platform.startswith("win"):
        try:
            os.startfile(path)
            return
        except OSError:
            pass

    print(f"Gagal memutar audio: {path}")


def play_audio_async(path):
    threading.Thread(target=_play_audio, args=(path,), daemon=True).start()
