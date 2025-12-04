import cv2
import numpy as np
import os



plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')

def apply_filter(image_path, filter_type, output_path):
    img = cv2.imread(image_path)

    if filter_type == 'gray':
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    elif filter_type == 'blur':
        img = cv2.GaussianBlur(img, (15, 15), 0)

    elif filter_type == 'canny':
        img = cv2.Canny(img, 100, 200)

    elif filter_type == 'sepia':
        kernel = np.array([[0.272,0.534,0.131],
                           [0.349,0.686,0.168],
                           [0.393,0.769,0.189]])
        img = cv2.transform(img, kernel)
        img = np.clip(img, 0, 255)

    elif filter_type == 'invert':
        img = cv2.bitwise_not(img)

    elif filter_type == 'sharpen':
        kernel = np.array([[0,-1,0],
                           [-1,5,-1],
                           [0,-1,0]])
        img = cv2.filter2D(img, -1, kernel)

    elif filter_type == 'threshold':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    elif filter_type == 'bright_contrast':
        img = cv2.convertScaleAbs(img, alpha=1.5, beta=30)  # contrast=1.5, brightness=30

    elif filter_type == 'cartoon':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 250, 250)
        img = cv2.bitwise_and(color, color, mask=edges)

    elif filter_type == 'sketch':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = cv2.bitwise_not(gray)
        blur = cv2.GaussianBlur(inv, (21,21), 0)
        img = cv2.divide(gray, 255-blur, scale=256)

    elif filter_type == 'rotate':
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    cv2.imwrite(output_path, img)







def _clamp_int(val, a=0, b=255):
    return max(a, min(b, int(val)))

def process_image(input_path, output_path,
                  brightness=0, contrast=100,
                  blur=0, sharpen=0, threshold=0):
    """
    Apply chain of DIP ops to input_path and write to output_path.
    Returns dictionary of any detected data (stub for future).
    brightness: -100..100
    contrast: 50..200 (100 = no change)
    blur: odd kernel size px (0 disables)
    sharpen: 0..5 (0 disables)
    threshold: 0..255 (0 disables)
    """
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError("Cannot read input image")

    # 1. brightness & contrast
    # cv2.convertScaleAbs: dst = src*alpha + beta
    alpha = float(contrast) / 100.0  # 1.0 = original
    beta = int(brightness)           # added brightness
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    # 2. blur (Gaussian)
    if blur and blur > 0:
        # ensure odd kernel
        k = int(blur)
        if k % 2 == 0: k += 1
        img = cv2.GaussianBlur(img, (k,k), 0)

    # 3. sharpen
    if sharpen and sharpen > 0:
        # unsharp mask style (basic)
        amount = float(sharpen)
        blurred = cv2.GaussianBlur(img, (0,0), 3)
        img = cv2.addWeighted(img, 1.0 + amount, blurred, -amount, 0)

    # 4. threshold (binarize) - apply on grayscale copy if requested
    detected = {}
    if threshold and threshold > 0:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, int(threshold), 255, cv2.THRESH_BINARY)
        # convert single channel to BGR so output remains consistent
        img = cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)

    # 5. optional morphological operations (example): denoise / open
    # you can expose these as params later

    # 6. histogram equalization (optional) — good for low-contrast images
    # convert to YCrCb and equalize Y
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    ycrcb[:,:,0] = cv2.equalizeHist(ycrcb[:,:,0])
    img = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    # Save output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 3])

    # detected can hold info like plate OCR results later
    return detected




def apply_extra_filters(img, filter_type):
    if filter_type == "emboss":
        kernel = np.array([[-2,-1,0],
                           [-1,1,1],
                           [0,1,2]])
        return cv2.filter2D(img, -1, kernel)

    elif filter_type == "hdr":
        return cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)

    elif filter_type == "denoise":
        return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    elif filter_type == "pencil2":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        pencil = cv2.divide(gray, 255 - blur, scale=256)
        return cv2.cvtColor(pencil, cv2.COLOR_GRAY2BGR)

    elif filter_type == "warm":
        increase = np.full(img.shape, (20, 10, 0), dtype=np.uint8)
        return cv2.add(img, increase)

    elif filter_type == "cool":
        increase = np.full(img.shape, (0, 10, 20), dtype=np.uint8)
        return cv2.add(img, increase)

    elif filter_type == "vintage":
        gamma = 0.6
        look_up = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)]).astype("uint8")
        return cv2.LUT(img, look_up)

    elif filter_type == "oil_paint":
        return cv2.xphoto.oilPainting(img, 10, 1)

    return img
