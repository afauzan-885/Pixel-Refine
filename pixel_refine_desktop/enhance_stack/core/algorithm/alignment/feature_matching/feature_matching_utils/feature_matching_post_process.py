import cv2
import numpy as np


def estimate_transform(base_points, target_points, transformation_type="homography", ransac_threshold=5.0):
    if base_points is None or target_points is None:
        return None, None
    if len(base_points) < 4 or len(target_points) < 4:
        return None, None

    try:
        if transformation_type == "affine":
            return cv2.estimateAffine2D(
                target_points.reshape(-1, 2),
                base_points.reshape(-1, 2),
                method=cv2.USAC_MAGSAC,
                ransacReprojThreshold=float(ransac_threshold),
            )
        return cv2.findHomography(
            target_points,
            base_points,
            cv2.USAC_MAGSAC,
            float(ransac_threshold),
        )
    except cv2.error:
        return None, None


def calculate_keep_edges_padding(matrix, width, height, transformation_type):
    corners = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32).reshape(-1, 1, 2)
    try:
        if transformation_type == "homography":
            if matrix.shape != (3, 3):
                return None
            transformed = cv2.perspectiveTransform(corners, matrix)
        else:
            if matrix.shape != (2, 3):
                return None
            transformed = cv2.transform(corners, matrix)
        transformed = transformed.reshape(-1, 2)
        min_x, min_y = transformed.min(axis=0)
        max_x, max_y = transformed.max(axis=0)
        return max(
            0,
            int(np.ceil(max_x - width)),
            int(np.ceil(max_y - height)),
            int(np.ceil(-min_x)),
            int(np.ceil(-min_y)),
        )
    except cv2.error:
        return None


def warp_with_keep_edges(image, matrix, transformation_type):
    height, width = image.shape[:2]
    pad = calculate_keep_edges_padding(matrix, width, height, transformation_type)
    if pad is None or pad <= 0:
        return warp_plain(image, matrix, transformation_type)

    try:
        padded = cv2.copyMakeBorder(image, pad, pad, pad, pad, cv2.BORDER_REFLECT)
        out_size = (padded.shape[1], padded.shape[0])
        if transformation_type == "homography":
            warped = cv2.warpPerspective(
                padded,
                matrix,
                out_size,
                flags=cv2.INTER_LANCZOS4,
                borderMode=cv2.BORDER_REFLECT,
            )
        else:
            warped = cv2.warpAffine(
                padded,
                matrix,
                out_size,
                flags=cv2.INTER_LANCZOS4,
                borderMode=cv2.BORDER_REFLECT,
            )
        if pad + height > warped.shape[0] or pad + width > warped.shape[1]:
            return warp_plain(image, matrix, transformation_type)
        return warped[pad : pad + height, pad : pad + width]
    except cv2.error:
        return None


def warp_plain(image, matrix, transformation_type):
    if image is None or matrix is None:
        return None
    height, width = image.shape[:2]
    try:
        if transformation_type == "homography":
            return cv2.warpPerspective(
                image,
                matrix,
                (width, height),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_CONSTANT,
            )
        return cv2.warpAffine(
            image,
            matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
        )
    except cv2.error:
        return None


def compensate_motion(image, base_points, target_points, config):
    transformation_type = str(config.get("transformation", "homography")).lower()
    matrix, mask = estimate_transform(
        base_points,
        target_points,
        transformation_type=transformation_type,
        ransac_threshold=config.get("ransacThreshold", 5.0),
    )
    if matrix is None:
        return None
    if config.get("keep_edges", False):
        return warp_with_keep_edges(image, matrix, transformation_type)
    return warp_plain(image, matrix, transformation_type)


def transform_bounds(base_points, target_points, width, height, transformation_type, ransac_threshold=5.0):
    matrix, mask = estimate_transform(
        base_points,
        target_points,
        transformation_type=transformation_type,
        ransac_threshold=ransac_threshold,
    )
    if matrix is None or mask is None:
        return None
    corners = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32).reshape(-1, 1, 2)
    try:
        if transformation_type == "homography":
            transformed = cv2.perspectiveTransform(corners, matrix)
        else:
            transformed = cv2.transform(corners, matrix)
    except cv2.error:
        return None
    transformed = transformed.reshape(-1, 2)
    return transformed.min(axis=0), transformed.max(axis=0)


def compute_global_crop_bounds(motion_plan, width, height, config):
    transformation_type = str(config.get("transformation", "homography")).lower()
    global_min_x = float("inf")
    global_min_y = float("inf")
    global_max_x = -float("inf")
    global_max_y = -float("inf")

    for item in motion_plan:
        if not item.get("success"):
            continue
        bounds = transform_bounds(
            item["base_points"],
            item["target_points"],
            width,
            height,
            transformation_type,
            ransac_threshold=config.get("ransacThreshold", 5.0),
        )
        if bounds is None:
            continue
        min_xy, max_xy = bounds
        global_min_x = min(global_min_x, float(min_xy[0]))
        global_min_y = min(global_min_y, float(min_xy[1]))
        global_max_x = max(global_max_x, float(max_xy[0]))
        global_max_y = max(global_max_y, float(max_xy[1]))

    if not np.isfinite([global_min_x, global_min_y, global_max_x, global_max_y]).all():
        return None

    crop_x = int(max(0, np.ceil(-global_min_x)))
    crop_y = int(max(0, np.ceil(-global_min_y)))
    crop_w = width - int(np.ceil(global_max_x - width)) - crop_x
    crop_h = height - int(np.ceil(global_max_y - height)) - crop_y
    if crop_w <= 0 or crop_h <= 0:
        return None
    return crop_x, crop_y, crop_w, crop_h


def crop_image(image, crop_bounds):
    if image is None or crop_bounds is None:
        return None
    x, y, width, height = crop_bounds
    return image[y : y + height, x : x + width]


def apply_non_crop(image, motion_item, config):
    if motion_item is None or not motion_item.get("success"):
        return np.array(image, copy=True)
    result = compensate_motion(
        image,
        motion_item["base_points"],
        motion_item["target_points"],
        config,
    )
    return result if result is not None else np.array(image, copy=True)


def apply_global_crop(image, motion_item, crop_bounds, config):
    if motion_item is None:
        return crop_image(image, crop_bounds)
    if not motion_item.get("success"):
        return None
    compensated = compensate_motion(
        image,
        motion_item["base_points"],
        motion_item["target_points"],
        config,
    )
    return crop_image(compensated, crop_bounds)
