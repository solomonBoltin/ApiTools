import requests
import unittest
import os

TEXT_FILE = "./tests/files/test.txt"
PDF_FILE = "./tests/files/test.pdf"
OUTPUT_FILE = "./tests/files/output.jpg"

DEPLOYED_BASE = 'https://apitools-bupdvuqama-uc.a.run.app/' 


class TestAPI(unittest.TestCase):
    
    def setUp(self):  # Use setUp for consistent test prep
        print("Setting up")

    def test_pdf_to_jpeg_conversion(self):
        url = DEPLOYED_BASE + 'pdfToJpeg'  # Corrected URL
        with open(PDF_FILE, 'rb') as f:
            files = {'file': ('test.pdf', f)}  # Correct file parameter
            response = requests.post(url, files=files)  # Use correct URL
            print(response.text)

        self.assertEqual(response.status_code, 200, "Failed to convert PDF")
        self.assertEqual(response.headers.get('Content-Type'), 'image/jpeg', "Invalid content type")

        with open(OUTPUT_FILE, 'wb') as f:
            f.write(response.content)
        self.assertTrue(os.path.isfile(OUTPUT_FILE), "Output file not created")
        

    def test_base_route(self):
        response = requests.get(DEPLOYED_BASE)
        self.assertEqual(response.status_code, 200, "Base route failed")
        self.assertEqual(response.text, "Hello API!", "Unexpected base route response")

    

if __name__ == '__main__':
    unittest.main()
