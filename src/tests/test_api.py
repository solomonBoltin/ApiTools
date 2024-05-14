import requests
import unittest
import os

TEXT_FILE = "./files/test.txt"
PDF_FILE = "./files/test.pdf"

OUTPUT_FILE = "files/rotate_test.jpg"

DEPLOYED_BASE = 'https://apitools-bupdvuqama-uc.a.run.app/'
LOCAL_BASE = 'http://127.0.0.1:8080/'

BASE = LOCAL_BASE  # Change to DEPLOYED_BASE to test deployed API


class TestAPI(unittest.TestCase):
    def setUp(self):  # Use setUp for consistent test prep
        print("Setting up")

    def test_pdf_to_jpeg_conversion(self):
        url = BASE + 'pdfToJpeg'  # Corrected URL
        with open(PDF_FILE, 'rb') as f:
            files = {'file': ('test.pdf', f)}  # Correct file parameter
            response = requests.post(url, files=files)  # Use correct URL

        self.assertEqual(response.status_code, 200, "Failed to convert PDF")
        self.assertEqual(response.headers.get('Content-Type'), 'image/jpeg', "Invalid content type")

        with open(OUTPUT_FILE, 'wb') as f:
            f.write(response.content)
        self.assertTrue(os.path.isfile(OUTPUT_FILE), "Output file not created")

    def test_base_route(self):
        response = requests.get(BASE)
        self.assertEqual(response.status_code, 200, "Base route failed")
        self.assertEqual(response.text, "Hello API!", "Unexpected base route response")


if __name__ == '__main__':
    unittest.main()
