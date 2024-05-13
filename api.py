

from flask import Flask, request, send_file
from pdf2image import convert_from_path
from PIL import Image
import tempfile
import io
import zipfile

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def home():
    return "Hello, World!"

@app.route('/upload', methods=['POST'])
def upload_pdf():
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
        images = convert_pdf_to_jpeg(pdf_file_path, temp_dir)

        # Process images (optional)
        # for i, image in enumerate(images):
        #     image_path = f"{temp_dir}/image{i+1}.jpg"
        #     process_image(image_path, image_path)  # Overwrites original image

        # Prepare response (ZIP file)
        response = prepare_response_big_image(images)
        
        return response

def convert_pdf_to_jpeg(pdf_file_path, output_dir):
    images = convert_from_path(pdf_file_path, dpi=300, output_folder=output_dir)
    return images

def process_image(image_path, output_path):
    image = Image.open(image_path)
    # Apply image processing here (e.g., resize, crop)
    # ...
    image.save(output_path, quality=90)

def prepare_response(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a") as zip_file:
        for i, image in enumerate(images):
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="JPEG")
            zip_file.writestr(f"image{i+1}.jpg", image_bytes.getvalue())

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name="converted_images.zip")


def prepare_response_big_image(images):
   # prepare response to one big image horizontally 
    # combine images horizontally
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)

    new_image = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for image in images:
        new_image.paste(image, (x_offset, 0))
        x_offset += image.width

    image_bytes = io.BytesIO()
    new_image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    return send_file(image_bytes, as_attachment=True, download_name="converted_images.jpg")
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)