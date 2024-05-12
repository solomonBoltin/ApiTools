# test_api.py

import unittest
from api import app, allowed_file, convert_pdf_to_jpeg
import os
import tempfile


TEXT_FILE = "./test_files/test.txt"
PDF_FILE = "./test_files/test.pdf"

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_allowed_file(self):
        self.assertTrue(allowed_file(PDF_FILE))
        self.assertFalse(allowed_file(TEXT_FILE))

    def test_upload_no_file(self):
        response = self.app.post('/upload')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No file part", response.data)

    def test_upload_invalid_file(self):
        with open(TEXT_FILE, "rb") as f:
            response = self.app.post('/upload', data={"file": (f, TEXT_FILE)})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"File type not allowed", response.data)

    def test_upload_valid_file(self):
        # Assuming you have a test PDF file named "test.pdf"
        with open(PDF_FILE, "rb") as f:
            response = self.app.post('/upload', data={"file": (f, PDF_FILE)})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"File uploaded successfully", response.data)

    def test_convert_pdf_to_jpeg(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_pdf_to_jpeg(PDF_FILE, temp_dir)
            self.assertTrue(len(images) > 0)  # Check if any images were generated
            for image in images:
                self.assertIsInstance(image, PIL.Image.Image)  # Verify image type
                image_path = os.path.join(temp_dir, image.filename)
                self.assertTrue(os.path.exists(image_path))  # Check if image file exists



# test the api using requests
import requests

def testValidFileUpload():
    url = 'https://api-tools-bupdvuqama-uc.a.run.app/upload'
    with open('test_files/test.pdf', 'rb') as f:
        files = {'file': ('test.pdf', f)} 
        response = requests.post(url, files=files)

    # Check if the response has a 200 save response image to output.jpg
    assert response.status_code == 200
    with open('output.jpg', 'wb') as f:
        f.write(response.content)

    print("PDF converted to images and saved as output.jpg")




if __name__ == '__main__':
    testValidFileUpload()