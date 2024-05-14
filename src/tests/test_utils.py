import unittest
import cv2
from PIL import Image

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

if __name__ == '__main__':
    unittest.main()
