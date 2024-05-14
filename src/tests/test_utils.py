import unittest
import cv2

from src.utils.deskew import deskew

IMAGE_FILE = "./tests/files/rotate_test.jpg"
OUTPUT_FILE = "./tests/files/rotate_test.jpg"


class TestUtils(unittest.TestCase):

    def test_deskew_image(self):
        # test image is rotated 90 degrees
        image = cv2.imread("files/rotate_test.jpg", 0)
        width, height = image.shape
        rotated_image = deskew(image)

        self.assertEqual((height, width), rotated_image.shape, "Deskewed image was not rotated correctly")


if __name__ == '__main__':
    unittest.main()
