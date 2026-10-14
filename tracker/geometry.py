from mediapipe.framework.formats import landmark_pb2

from .utils import clamp


def points_to_landmark_list(points):
    landmark_list = landmark_pb2.NormalizedLandmarkList()
    for x, y, z in points:
        landmark_list.landmark.add(x=float(x), y=float(y), z=float(z))
    return landmark_list


def normalized_bbox(points, width, height, padding=12):
    if len(points) == 0:
        return None

    xs = points[:, 0] * width
    ys = points[:, 1] * height
    x0 = int(clamp(float(xs.min()) - padding, 0, width - 1))
    y0 = int(clamp(float(ys.min()) - padding, 0, height - 1))
    x1 = int(clamp(float(xs.max()) + padding, 0, width - 1))
    y1 = int(clamp(float(ys.max()) + padding, 0, height - 1))
    return x0, y0, x1, y1


def landmark_center(points, width, height, index=0):
    if len(points) <= index:
        return None
    return int(points[index][0] * width), int(points[index][1] * height)
