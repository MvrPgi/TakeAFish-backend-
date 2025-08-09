from flask import Flask, render_template, request, redirect, jsonify
import os
from waitress import serve
import tempfile
from species import predict_fish_specie, process_prediction

app = Flask(__name__)

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
        return {"error": "No Image File Provoded"}, 400
    

    file = request.files['image']

    if file.filename == '':
        return {"error": "No Image File Selected"}, 400
    
    if file:
        try:
            # Bagong Temporary File Path
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name

            result = predict_fish_specie(temp_file_path)

            os.unlink(temp_file_path)  # Delete the temporary file after processing

            if "error" in result:
                return jsonify(result), 500
            

            processed_result = process_prediction(result)
            return processed_result, 200 
        

        except Exception as e:
            # Clean Up Temporary File If It Exists
            if os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    return {"error": "Invalid Request"}, 400
              




if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)