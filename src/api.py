from flask import Flask, request, send_file
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import io

from src.pdf_to_jpeg import pdf_to_jpeg

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return "Hello API!"


@app.route('/pdfToJpeg', methods=['POST'])
def upload_pdf():
    return pdf_to_jpeg(request)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
