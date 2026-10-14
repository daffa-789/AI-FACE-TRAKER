import os
import time

import cv2
import mediapipe as mp

from .audio import play_audio_async
from .camera import enhance_frame, frame_quality_metrics, open_capture
from .config import WINDOW_NAME, audio_map, parse_args
from .drawing import (
    draw_face_overlay,
    draw_framing_guides,
    draw_hand_overlay,
    draw_hand_trails,
    draw_help,
    draw_pause,
    draw_status_panel,
    draw_toast,
    patch_mediapipe_mapping,
    update_hand_trails,
)
from .event_log import EventLogger
from .face import apply_privacy_blur, create_face_mesh, extract_face_infos
from .gestures import GestureStabilizer, create_gesture_recognizer, extract_hand_infos, recognize_raw_gesture
from .output import save_frame, start_recording
from .smoothing import LandmarkSmoother
from .stats import SessionStats
from .utils import FpsMeter, TimestampClock, Toast


def main():
    args = parse_args()

    cap = open_capture(args.source, args.width, args.height, args.fps)
    if not cap.isOpened():
        raise RuntimeError("Tidak bisa membuka sumber video. Periksa kamera atau path file.")

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands
    mp_face_mesh = mp.solutions.face_mesh
    patch_mediapipe_mapping(mp_drawing)

    face_mesh = None
    if not args.no_face:
        face_mesh = create_face_mesh(args)

    gesture_recognizer = None
    if not args.no_hands:
        gesture_recognizer = create_gesture_recognizer(args)

    gesture_stabilizer = GestureStabilizer(args.stable_frames, args.gesture_dominance)
    smoother = LandmarkSmoother(args.smoothing)
    fps_meter = FpsMeter()
    timestamp_clock = TimestampClock()
    toast = Toast()
    stats = SessionStats()
    logger = EventLogger(args.event_log, enabled=not args.no_event_log)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))

    sounds = audio_map()
    mirror_enabled = not args.no_mirror
    enhanced_enabled = not args.no_enhance
    show_face = not args.no_face
    show_hands = not args.no_hands
    dense_face = args.dense_face
    privacy_enabled = args.privacy_blur
    trails_enabled = not args.no_trails
    auto_snapshots = args.gesture_snapshots
    audio_enabled = not args.mute
    paused = False
    recording = False
    video_writer = None
    recording_path = None
    last_audio_times = {}
    last_event_times = {}
    last_stable_gesture = None
    last_display_frame = None
    last_quality = {"brightness": 0.0, "sharpness": 0.0, "health": 0.0}
    hand_trails = {}

    logger.log("app", "started", f"source={args.source}")

    try:
        while True:
            if paused and last_display_frame is not None:
                frame = last_display_frame.copy()
                draw_pause(frame)
                fps = fps_meter.fps
                face_count = 0
                hand_count = 0
                stable_gesture = last_stable_gesture
                stable_confidence = 0.0
                progress = 1.0 if stable_gesture else 0.0
                quality = last_quality
            else:
                success, frame = cap.read()
                if not success:
                    break

                if mirror_enabled:
                    frame = cv2.flip(frame, 1)

                if enhanced_enabled:
                    frame = enhance_frame(frame, clahe, args.enhance_strength)

                quality = frame_quality_metrics(frame)
                last_quality = quality
                height, width = frame.shape[:2]
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_image.flags.writeable = False

                face_results = face_mesh.process(rgb_image) if face_mesh is not None else None
                gesture_result = None
                if gesture_recognizer is not None:
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
                    gesture_result = gesture_recognizer.recognize_for_video(mp_image, timestamp_clock.next_ms())

                rgb_image.flags.writeable = True

                face_infos, active_face_indexes = extract_face_infos(face_results, smoother, width, height)
                hand_infos, active_hand_indexes = extract_hand_infos(gesture_result, smoother)
                face_count = len(face_infos)
                hand_count = len(hand_infos)
                stats.update_frame(face_count, hand_count)
                smoother.keep_only("face", active_face_indexes)
                smoother.keep_only("hand", active_hand_indexes)

                if privacy_enabled and face_infos:
                    apply_privacy_blur(frame, face_infos)

                draw_framing_guides(frame)

                if trails_enabled:
                    update_hand_trails(hand_trails, hand_infos, width, height)
                    draw_hand_trails(frame, hand_trails)
                else:
                    hand_trails.clear()

                if show_face:
                    for face_info in face_infos:
                        draw_face_overlay(frame, face_info, mp_drawing, mp_drawing_styles, mp_face_mesh, dense_face)

                if show_hands:
                    for hand_info in hand_infos:
                        draw_hand_overlay(frame, hand_info, mp_drawing, mp_drawing_styles, mp_hands)

                raw_gesture, raw_score = recognize_raw_gesture(hand_infos, args.gesture_score)
                stable_gesture, stable_confidence, progress = gesture_stabilizer.update(raw_gesture, raw_score)

                if stable_gesture:
                    now = time.perf_counter()
                    last_event = last_event_times.get(stable_gesture, -9999.0)
                    should_fire_event = now - last_event >= max(0.8, args.gesture_delay)
                    if should_fire_event:
                        stats.record_gesture(stable_gesture)
                        logger.log("gesture", stable_gesture, f"{stable_confidence:.3f}")
                        last_event_times[stable_gesture] = now
                        if auto_snapshots:
                            path = save_frame(frame, args.output_dir, "gesture")
                            logger.log("screenshot", "auto_gesture", os.path.basename(path))
                            toast.show(f"AutoShot: {os.path.basename(path)}")

                    audio_path = sounds.get(stable_gesture)
                    last_play = last_audio_times.get(stable_gesture, -9999.0)
                    if audio_enabled and audio_path and (now - last_play) >= max(0.0, args.gesture_delay):
                        print(stable_gesture)
                        play_audio_async(audio_path)
                        last_audio_times[stable_gesture] = now
                        if not auto_snapshots:
                            toast.show(f"Audio: {stable_gesture}")
                    last_stable_gesture = stable_gesture
                else:
                    last_stable_gesture = None

                fps = fps_meter.update()
                draw_status_panel(
                    frame,
                    fps,
                    face_count,
                    hand_count,
                    stable_gesture,
                    stable_confidence,
                    progress,
                    audio_enabled,
                    recording,
                    mirror_enabled,
                    enhanced_enabled,
                    privacy_enabled,
                    trails_enabled,
                    auto_snapshots,
                    quality,
                    stats,
                )

                if not args.hide_help:
                    draw_help(frame)

                last_display_frame = frame.copy()

            if toast.active():
                draw_toast(frame, toast.message)

            if recording and video_writer is not None:
                video_writer.write(frame)

            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(30 if paused else 1) & 0xFF

            if key in (27, ord("q")):
                break
            if key == ord("m"):
                mirror_enabled = not mirror_enabled
                toast.show(f"Mirror {'ON' if mirror_enabled else 'OFF'}")
                logger.log("toggle", "mirror", mirror_enabled)
            elif key == ord("f"):
                show_face = not show_face
                toast.show(f"Face overlay {'ON' if show_face else 'OFF'}")
                logger.log("toggle", "face_overlay", show_face)
            elif key == ord("h"):
                show_hands = not show_hands
                toast.show(f"Hand overlay {'ON' if show_hands else 'OFF'}")
                logger.log("toggle", "hand_overlay", show_hands)
            elif key == ord("d"):
                dense_face = not dense_face
                toast.show(f"Dense mesh {'ON' if dense_face else 'OFF'}")
                logger.log("toggle", "dense_face", dense_face)
            elif key == ord("a"):
                audio_enabled = not audio_enabled
                toast.show(f"Audio {'ON' if audio_enabled else 'OFF'}")
                logger.log("toggle", "audio", audio_enabled)
            elif key == ord("e"):
                enhanced_enabled = not enhanced_enabled
                toast.show(f"Enhance {'ON' if enhanced_enabled else 'OFF'}")
                logger.log("toggle", "enhance", enhanced_enabled)
            elif key == ord("b"):
                privacy_enabled = not privacy_enabled
                toast.show(f"Privacy blur {'ON' if privacy_enabled else 'OFF'}")
                logger.log("toggle", "privacy_blur", privacy_enabled)
            elif key == ord("t"):
                trails_enabled = not trails_enabled
                toast.show(f"Hand trail {'ON' if trails_enabled else 'OFF'}")
                logger.log("toggle", "hand_trail", trails_enabled)
            elif key == ord("g"):
                auto_snapshots = not auto_snapshots
                toast.show(f"AutoShot {'ON' if auto_snapshots else 'OFF'}")
                logger.log("toggle", "gesture_snapshots", auto_snapshots)
            elif key == ord("p"):
                paused = not paused
                toast.show("Pause" if paused else "Resume")
                logger.log("toggle", "pause", paused)
            elif key == ord("s"):
                path = save_frame(frame, args.output_dir, "screenshot")
                toast.show(f"Screenshot: {os.path.basename(path)}")
                logger.log("screenshot", "manual", os.path.basename(path))
            elif key == ord("r"):
                if recording:
                    recording = False
                    if video_writer is not None:
                        video_writer.release()
                    video_writer = None
                    toast.show(f"Saved: {os.path.basename(recording_path) if recording_path else 'recording'}")
                    logger.log("recording", "stop", os.path.basename(recording_path) if recording_path else "")
                else:
                    video_writer, recording_path = start_recording(frame, args.output_dir, fps_meter.fps or args.fps)
                    recording = video_writer is not None
                    toast.show("Recording ON" if recording else "Recording failed")
                    logger.log("recording", "start", os.path.basename(recording_path) if recording_path else "failed")

            if args.record and not recording and video_writer is None and last_display_frame is not None:
                video_writer, recording_path = start_recording(last_display_frame, args.output_dir, fps_meter.fps or args.fps)
                recording = video_writer is not None
                logger.log("recording", "start_arg", os.path.basename(recording_path) if recording_path else "failed")
                args.record = False

    finally:
        logger.log("app", "stopped", f"frames={stats.frames}")
        if video_writer is not None:
            video_writer.release()
        if gesture_recognizer is not None:
            gesture_recognizer.close()
        if face_mesh is not None:
            face_mesh.close()
        cap.release()
        cv2.destroyAllWindows()
