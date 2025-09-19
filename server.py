from flask import Flask, render_template, request, redirect, jsonify
import os
from waitress import serve
import tempfile
from services.species import predict_fish_specie, process_prediction
import logging
from services.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

app = Flask(__name__)


# Setup logging
logging.basicConfig(
    filename="app.log",            # Save logs in app.log file
    level=logging.INFO,            # Log INFO and above (INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.route('/')
def index():
    return render_template('species.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        logging.warning("Upload attempted with no image file provided")
        return jsonify({"error": "No Image File Provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No Image File Selected"}), 400
    
    if not allowed_file(file.filename):
        logging.warning(f"Unsupported file type attempted: {file.filename}")
        return jsonify({"error": "Unsupported file type"}), 400

    # File size validation
    content_length = request.content_length
    if content_length is not None and content_length > MAX_FILE_SIZE:
        logging.warning(f"File size {content_length} exceeds limit of {MAX_FILE_SIZE}")
        return jsonify({"error": f"File size exceeds {MAX_FILE_SIZE // (1024 * 1024)}MB limit"}), 400

    temp_file_path = None

    try:
        # Preserve extension
        ext = os.path.splitext(file.filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            file.seek(0)
            file.save(temp_file.name)
            file.seek(0)
            from werkzeug.datastructures import FileStorage
            if isinstance(file, FileStorage):
                file.save(temp_file.name)
            else:
                temp_file.write(file.read())
            temp_file_path = temp_file.name

        result = predict_fish_specie(temp_file_path)
        if "error" in result:
            logging.error(f"Prediction failed: {result['error']}")
            return jsonify(result), 500

        processed_result = process_prediction(result, temp_file_path)
        logging.info(f"Image uploaded and processed successfully: {temp_file_path}")
        return jsonify(processed_result), 200

    except Exception as e:
        logging.exception("Unexpected error during image processing")
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logging.info(f"Temporary file deleted: {temp_file_path}")
            except Exception as ex:
                logging.warning(f"Failed to delete temp file: {temp_file_path}. Exception: {ex}")

     





if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)