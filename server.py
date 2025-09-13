from flask import Flask, render_template, request, redirect, jsonify
import os
from waitress import serve
import tempfile
from species import predict_fish_specie, process_prediction
import logging

app = Flask(__name__)


# Setup logging
logging.basicConfig(
    filename="app.log",            # Save logs in app.log file
    level=logging.INFO,            # Log INFO and above (INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Make sure the upload folder exists
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to process the image file
def process_image(file_path):
    print(f"Processing image at: {file_path}")



@app.route('/')
def index():
    return render_template('species.html')

# Handle the upload
@app.route('/upload', methods=['POST'])

def upload_image():
    if 'image' not in request.files:
        logging.warning("Upload attempted with no image file provided")
        return {"error": "No Image File Provoded"}, 400
    
    file = request.files['image']

    if file.filename == '':
        logging.warning("Upload attempted with empty filename")
        return {"error": "No Image File Selected"}, 400
    
    if file:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name

            logging.info(f"Image uploaded and saved temporarily at: {temp_file_path}")

            result = predict_fish_specie(temp_file_path)
            if "error" in result:
                logging.error(f"Prediction failed for {temp_file_path}: {result}")
                os.unlink(temp_file_path)
                return jsonify(result), 500

            processed_result = process_prediction(result, temp_file_path)
            os.unlink(temp_file_path)

            logging.info(f"Processing completed for {temp_file_path}")
            return jsonify(processed_result), 200

        except Exception as e:
            logging.exception("Unexpected error during upload/processing")
            if os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
    logging.error("Invalid upload request")
    return {"error": "Invalid Request"}, 500




if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)