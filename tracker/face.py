import cv2
import mediapipe as mp
import numpy as np

from .geometry import normalized_bbox


def create_face_mesh(args):
    return mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=args.max_faces,
        refine_landmarks=True,
        min_detection_confidence=args.min_det,
        min_tracking_confidence=args.min_track,
    )


def extract_face_infos(face_results, smoother, width, height):
    face_landmarks_list = face_results.multi_face_landmarks if face_results else []
    face_infos = []
    active_indexes = []

    for face_idx, face_landmarks in enumerate(face_landmarks_list or []):
        active_indexes.append(face_idx)
        face_points = smoother.smooth(("face", face_idx), face_landmarks.landmark)
        bbox = normalized_bbox(face_points, width, height, padding=18)
        pose = estimate_head_pose(face_points, width, height)
        face_infos.append(
            {
                "index": face_idx,
                "points": face_points,
                "bbox": bbox,
                "pose": pose,
            }
        )

    return face_infos, active_indexes


def apply_privacy_blur(frame, face_infos):
    for info in face_infos:
        bbox = info.get("bbox")
        if not bbox:
            continue
        x0, y0, x1, y1 = bbox
        roi = frame[y0:y1, x0:x1]
        if roi.size == 0:
            continue
        width = x1 - x0
        height = y1 - y0
        kernel = max(25, int(min(width, height) * 0.18))
        if kernel % 2 == 0:
            kernel += 1
        frame[y0:y1, x0:x1] = cv2.GaussianBlur(roi, (kernel, kernel), 0)


def estimate_head_pose(face_points, width, height):
    if len(face_points) < 468:
        return None

    landmark_ids = [1, 152, 33, 263, 61, 291]
    image_points = np.array(
        [(face_points[idx][0] * width, face_points[idx][1] * height) for idx in landmark_ids],
        dtype=np.float64,
    )
    model_points = np.array(
        [
            (0.0, 0.0, 0.0),
            (0.0, -330.0, -65.0),
            (-225.0, 170.0, -135.0),
            (225.0, 170.0, -135.0),
            (-150.0, -150.0, -125.0),
            (150.0, -150.0, -125.0),
        ],
        dtype=np.float64,
    )

    focal_length = float(width)
    camera_matrix = np.array(
        [[focal_length, 0.0, width / 2.0], [0.0, focal_length, height / 2.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    success, rotation_vec, translation_vec = cv2.solvePnP(
        model_points,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not success:
        return None

    rotation_matrix, _ = cv2.Rodrigues(rotation_vec)
    projection = np.hstack((rotation_matrix, translation_vec))
    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(projection)
    pitch, yaw, roll = [normalize_angle(float(angle)) for angle in euler_angles.flatten()]

    nose = tuple(image_points[0].astype(int))
    axis_points, _ = cv2.projectPoints(
        np.array([(0.0, 0.0, 650.0)], dtype=np.float64),
        rotation_vec,
        translation_vec,
        camera_matrix,
        dist_coeffs,
    )
    nose_end = tuple(axis_points[0][0].astype(int))
    return pitch, yaw, roll, nose, nose_end


def normalize_angle(angle):
    return (angle + 180.0) % 360.0 - 180.0


def describe_pose(pitch, yaw):
    if yaw > 18:
        return "lihat kanan"
    if yaw < -18:
        return "lihat kiri"
    if pitch > 16:
        return "lihat bawah"
    if pitch < -13:
        return "lihat atas"
    return "hadap depan"
