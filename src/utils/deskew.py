import cv2
import numpy as np

from src.utils.rotation_calc import calculate_rotated_size

DEBUGGING_ROTATED_IMAGE_PATH = 'tests/debugging_rotate_image.jpg'
DEBUGGING_DESKEWED_IMAGE_PATH = 'tests/debugging_deskewed_image.jpg'


def deskew(im, max_skew=10):
    print(im.shape)
    o_height, o_width, _ = im.shape
    original_im = im.copy()

    # Resize image to a width of 500, maintaining aspect ratio, unless the image is smaller
    if o_width > 500:
        width = 500
        ratio = width / o_width
        height = int(o_height * ratio)
        im = cv2.resize(original_im, (width, height))

    print("New image size: ", im.shape)

    # Create a grayscale image and denoise it
    im_gs = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    im_gs = cv2.fastNlMeansDenoising(im_gs, h=3)

    # Create an inverted B&W copy using Otsu (automatic) thresholding
    # im_bw = cv2.threshold(im_gs, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    im_bw = cv2.adaptiveThreshold(im_gs, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Detect lines in this image. Parameters here mostly arrived at by trial and error.
    lines = cv2.HoughLinesP(
        im_bw, 1, np.pi / 180, 200, minLineLength=width / 12, maxLineGap=width / 150
    )
    print("Lines: ", lines)

    if lines is None:
        lines = []

    # Collect the angles of these lines (in radians)
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angles.append(np.arctan2(y2 - y1, x2 - x1))

    # If the majority of our lines are vertical, this is probably a landscape image
    landscape = np.sum([abs(angle) > np.pi / 4 for angle in angles]) > len(angles) / 2
    print("Landscape: ", landscape)

    # Filter the angles to remove outliers based on max_skew
    if landscape:
        angles = [
            angle
            for angle in angles
            if np.deg2rad(90 - max_skew) < abs(angle) < np.deg2rad(90 + max_skew)
        ]
    else:
        angles = [angle for angle in angles if abs(angle) < np.deg2rad(max_skew)]

    print("Angles: ", angles)

    if len(angles) < 5:
        # Insufficient data to deskew
        return original_im

    # Average the angles to a degree offset
    angle_deg = np.rad2deg(np.median(angles))
    print("Angle: ", angle_deg)
    print("Landscape: ", landscape)
    print("OWidth: ", o_width, "OHeight: ", o_height)
    new_width, new_height = calculate_rotated_size(o_width, o_height, angle_deg)

    # If this is landscape image, rotate the entire canvas appropriately
    if landscape:
        if angle_deg < 0:
            original_im = cv2.rotate(original_im, cv2.ROTATE_90_CLOCKWISE)
            angle_deg += 90
        elif angle_deg > 0:
            original_im = cv2.rotate(original_im, cv2.ROTATE_90_COUNTERCLOCKWISE)
            angle_deg -= 90

    print("New Width:", new_width)
    print("New Height:", new_height)

    # Rotate the image by the residual offset
    M = cv2.getRotationMatrix2D((new_width / 2, new_height / 2), angle_deg, 1)
    # cv2.imwrite(DEBUGGING_ROTATED_IMAGE_PATH, original_im)

    original_im = cv2.warpAffine(original_im, M, (new_width, new_height), borderMode=cv2.BORDER_REPLICATE)
    # cv2.imwrite(DEBUGGING_DESKEWED_IMAGE_PATH, original_im)

    return original_im
