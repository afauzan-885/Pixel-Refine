import numpy as np


def select_top_keypoints(keypoints, descriptors, limit):
    if descriptors is None or len(keypoints) <= limit:
        return keypoints, descriptors
    indices = np.argsort([-kp.response for kp in keypoints])[:limit]
    return [keypoints[i] for i in indices], descriptors[indices]


def compute_features_block(
    detector,
    reference_gray,
    target_gray,
    x,
    y,
    block_w,
    block_h,
    overlap_px,
    max_keypoints_per_block=400,
):
    image_h, image_w = reference_gray.shape
    x0 = max(0, x - overlap_px)
    y0 = max(0, y - overlap_px)
    x1 = min(image_w, x + block_w + overlap_px)
    y1 = min(image_h, y + block_h + overlap_px)
    if x1 <= x0 or y1 <= y0:
        return [], None, [], None

    ref_roi = reference_gray[y0:y1, x0:x1]
    target_roi = target_gray[y0:y1, x0:x1]
    kp_ref, des_ref = detector.detectAndCompute(ref_roi, None)
    kp_target, des_target = detector.detectAndCompute(target_roi, None)

    def adjust(keypoints, descriptors):
        adjusted = []
        indices = []
        if keypoints and descriptors is not None:
            for idx, keypoint in enumerate(keypoints):
                px = keypoint.pt[0] + x0
                py = keypoint.pt[1] + y0
                if x <= px < x + block_w and y <= py < y + block_h and idx < len(descriptors):
                    keypoint.pt = (px, py)
                    adjusted.append(keypoint)
                    indices.append(idx)
        if descriptors is None or not indices:
            return [], None
        return adjusted, descriptors[np.array(indices)]

    kp_ref, des_ref = select_top_keypoints(
        *adjust(kp_ref, des_ref),
        max_keypoints_per_block,
    )
    kp_target, des_target = select_top_keypoints(
        *adjust(kp_target, des_target),
        max_keypoints_per_block,
    )
    return kp_ref, des_ref, kp_target, des_target
