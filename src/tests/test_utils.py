import unittest
import cv2
import pytesseract
from PIL import Image, ImageDraw
from layoutparser.models import Detectron2LayoutModel

from src.utils.deskew import deskew

IMAGE_FILE = "./files/test.png"

OUTPUT_FILE = "./files/test_output.jpg"


class TestUtils(unittest.TestCase):

    def test_deskew_image(self):
        # test image is rotated 90 degrees
        image = cv2.imread("files/rotate_test.jpg", 0)
        width, height = image.shape
        rotated_image = deskew(image)

        self.assertEqual((height, width), rotated_image.shape, "Deskewed image was not rotated correctly")

    def test_resize(self):
        image = Image.open(IMAGE_FILE)

        joined_image = Image.new('RGB', (image.width, image.height * 10))
        y_offset = 0
        for i in range(10):
            image = Image.open(IMAGE_FILE)
            joined_image.paste(image, (0, y_offset))
            y_offset += image.height

        joined_image.save(OUTPUT_FILE)

    def test_tesseract_ocr(self):
        # im = cv2.imread("files/test_ocr.jpg")
        #
        # # Noise reduction (e.g., Gaussian blur)
        # im_gs = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # im_gs = cv2.fastNlMeansDenoising(im_gs, h=3)
        #
        # im_bw = cv2.adaptiveThreshold(im_gs, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        im = preprocess_for_ocr("files/test_ocr.jpg")
        cv2.imwrite("files/processed_test_ocr.jpg", im)

        image = Image.open("files/test_ocr.jpg")
        draw = ImageDraw.Draw(image)

        text = pytesseract.image_to_string(image, lang="heb")
        print(text)

        custom_config = r'--oem 1 --psm 6 -l heb'
        data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
        print("Data", data)

        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                text = data['text'][i]
                print(f"Text: '{text}', Bounding Box: ({x}, {y}, {w}, {h})")
                draw.rectangle([x, y, x + w, y + h], outline='red', width=2)
        draw.text((x, y), text, fill='red')
        image.save("files/output_processed_test_ocr.jpg")

    def test_layoutparser(self):
        image = cv2.imread("files/test_ocr.jpg")
        # Detect text blocks and OCR
        model = Detectron2LayoutModel(
            config_path="lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
            label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
        )
        layout = model.detect(image)
        print(layout)


def preprocess_for_ocr(image_path):
    """Preprocesses a scanned document image for optimal OCR performance."""

    # 1. Load and Grayscale
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # # 2. Noise Reduction (Optional, adjust as needed)
    # img = cv2.GaussianBlur(img, (1, 1), 0)  # Mild blur for noise removal

    cv2.imwrite("files/blurred.jpg", img)

    # 3. Adaptive Thresholding
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 11, 2)  # Block size 11, C = 2
    cv2.imwrite("files/tresh.jpg", img)

    # 4. Morphological Operations (Fine-tune based on your documents)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))  # Small kernel
    opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)  # Remove small noise
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)  # Close small gaps
    cv2.imwrite("files/closing.jpg", closing)

    # 5. Invert (Optional, if your text is light on a dark background)
    # inverted = cv2.bitwise_not(closing)  # Invert colors

    return closing


if __name__ == '__main__':
    unittest.main()
