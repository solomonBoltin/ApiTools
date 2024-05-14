from typing import List

import cv2
import numpy as np
from flask import Flask, send_file, Request
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import io

from src.utils.deskew import deskew

ALLOWED_EXTENSIONS = {'pdf'}


def optimized_pdf_to_jpeg(request: Request):
    print(request.files)
    if 'file' not in request.files:
        return "No file part", 400

    pdf_file = request.files['file']
    if pdf_file.filename == '':
        return "No selected file", 400

    if not allowed_file(pdf_file.filename):
        return "File type not allowed", 400

    with tempfile.TemporaryDirectory() as temp_dir:
        # Save PDF temporarily
        pdf_file_path = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False).name
        pdf_file.save(pdf_file_path)
        pdf_file.close()

        # Convert PDF to images
        images = convert_from_path(pdf_file_path, dpi=300, output_folder=temp_dir, paths_only=True)
        print("PdfData")
        print(temp_dir)
        print(images)

        images = [cv2.imread(image_path) for image_path in images]
        joined = cv2.vconcat([deskew(im) for im in images])
        del images
        cv2.imwrite("joined.jpg", joined)
        _, encoded_image = cv2.imencode('.jpg', joined)
        del joined
        image_bytes = io.BytesIO(encoded_image)
        image_bytes.seek(0)
        return send_file(image_bytes, as_attachment=True, download_name="converted_images.jpg")

def pdf_to_jpeg(request: Request):
    print(request.files)
    if 'file' not in request.files:
        return "No file part", 400

    pdf_file = request.files['file']
    if pdf_file.filename == '':
        return "No selected file", 400

    if not allowed_file(pdf_file.filename):
        return "File type not allowed", 400

    with tempfile.TemporaryDirectory() as temp_dir:
        # Save PDF temporarily
        pdf_file_path = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False).name
        pdf_file.save(pdf_file_path)

        # Convert PDF to images
        images = convert_pdf_to_jpegs(pdf_file_path, temp_dir)
        images = autorotate_images(images)

        joined_image = join_images(images, vertical=True)

        # Prepare response
        response = prepare_response(joined_image)

        return response


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_pdf_to_jpegs(pdf_file_path, output_dir):
    images = convert_from_path(pdf_file_path, dpi=300, output_folder=output_dir)
    return images


def autorotate_images(images: List[Image.Image]):
    cv_images = [np.array(image.convert("RGB")) for image in images]
    rotated_images = [deskew(image) for image in cv_images]
    images = [Image.fromarray(image) for image in rotated_images]
    return images


def join_images(images: List[Image.Image], vertical=False):
    # combine images horizontally or vertically
    widths, heights = zip(*(i.size for i in images))
    if vertical:
        total_width = max(widths)
        total_height = sum(heights)
    else:
        total_width = sum(widths)
        total_height = max(heights)

    new_image = Image.new('RGB', (total_width, total_height))

    offset = 0
    for image in images:
        if vertical:
            new_image.paste(image, (0, offset))
            offset += image.height
        else:
            new_image.paste(image, (offset, 0))
            offset += image.width

    return new_image


def prepare_response(image):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    return send_file(image_bytes, as_attachment=True, download_name="converted_images.jpg")


def prepare_response_big_image(images):
    # prepare response to one big image horizontally
    # combine images horizontally
    widths, heights = zip(*(i.size for i in images))
    total_width = max(widths)
    max_height = sum(heights)

    new_image = Image.new('RGB', (total_width, max_height))

    y_offset = 0
    for image in images:
        new_image.paste(image, (0, y_offset))
        y_offset += image.height

    image_bytes = io.BytesIO()
    new_image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    return send_file(image_bytes, as_attachment=True, download_name="converted_images.jpg")
