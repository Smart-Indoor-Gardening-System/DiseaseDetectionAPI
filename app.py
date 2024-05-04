from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticapm.contrib.flask import ElasticAPM
import os
import traceback
import logging
import boto3
import tensorflow as tf
import numpy as np
from werkzeug.utils import secure_filename
from pathlib import Path

file_path = Path('trained_plant_disease_model.keras')
app = Flask(__name__)

app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'AI-DiseaseDetector',
    'SECRET_TOKEN': 'SECRET',
    'SERVER_URL': 'https://03083cf3455c42ff9e7fcefc6db1a6c6.apm.us-east-1.aws.cloud.es.io:443',
    'DEBUG': True
}
apm = ElasticAPM(app)
# Configure CORS
CORS(app, resources={r"/predict": {"origins": "https://master.d3d439a2zipsvi.amplifyapp.com"}})

# Configure logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

# Define paths
MODEL_DIR = '/home/ubuntu'
MODEL_FILE = 'trained_plant_disease_model.keras'
MODEL_PATH = "trained_plant_disease_model.keras"

# Function to check if model exists locally
def model_exists():
    if os.path.exists(MODEL_PATH) and os.access(MODEL_PATH, os.R_OK):
        logging.info("Model file exists and is readable.")
        return True
    else:
        logging.error("Model file does not exist or is not readable.")
        return False

# Function to download model from S3 if it doesn't exist locally
def download_model_from_s3(bucket_name, object_name):
    local_file_path = os.path.join(MODEL_DIR, object_name)
    if not model_exists():
        try:
            # Download the file from S3
            s3 = boto3.client('s3')
            s3.download_file(bucket_name, object_name, local_file_path)
        except Exception as e:
            logging.error(f"Failed to download model from S3: {str(e)}")

# Usage example
download_model_from_s3('disease-ml-bucket', 'trained_plant_disease_model.keras')

# Tensorflow Model Prediction
def model_prediction(test_image_path):
    try:
        if  model_exists():
            image = tf.keras.preprocessing.image.load_img(test_image_path, target_size=(128, 128))
            input_arr = tf.keras.preprocessing.image.img_to_array(image)
            input_arr = np.array([input_arr])  # Convert single image to batch
            model = tf.keras.models.load_model(file_path)
            predictions = model.predict(input_arr)
            return np.argmax(predictions)  # Return index of max element
    except Exception as e:
        logging.error(f"Failed to make prediction: {str(e)}")

# Endpoint for prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        # Save the file to a temporary location
        filename = secure_filename(file.filename)
        temp_file_path = os.path.join('/tmp', filename)
        file.save(temp_file_path)
        
        
        result_index = model_prediction(temp_file_path)
        os.remove(temp_file_path)  # Remove the temporary file
        
        if result_index is None:
            return jsonify({'error': 'Failed to make prediction'}),
            
        
        class_name = ['Apple__Apple_scab', 'Apple_Black_rot', 'Apple_Cedar_apple_rust', 'Apple__healthy',
                    'Blueberry__healthy', 'Cherry(including_sour)___Powdery_mildew', 
                    'Cherry_(including_sour)__healthy', 'Corn(maize)___Cercospora_leaf_spot Gray_leaf_spot', 
                    'Corn_(maize)__Common_rust', 'Corn_(maize)__Northern_Leaf_Blight', 'Corn(maize)___healthy', 
                    'Grape__Black_rot', 'Grape_Esca(Black_Measles)', 'Grape__Leaf_blight(Isariopsis_Leaf_Spot)', 
                    'Grape__healthy', 'Orange_Haunglongbing(Citrus_greening)', 'Peach___Bacterial_spot',
                    'Peach__healthy', 'Pepper,_bell_Bacterial_spot', 'Pepper,_bell__healthy', 
                    'Potato__Early_blight', 'Potato_Late_blight', 'Potato__healthy', 
                    'Raspberry__healthy', 'Soybean_healthy', 'Squash__Powdery_mildew', 
                    'Strawberry__Leaf_scorch', 'Strawberry_healthy', 'Tomato__Bacterial_spot', 
                    'Tomato__Early_blight', 'Tomato_Late_blight', 'Tomato__Leaf_Mold', 
                    'Tomato__Septoria_leaf_spot', 'Tomato__Spider_mites Two-spotted_spider_mite', 
                    'Tomato__Target_Spot', 'Tomato_Tomato_Yellow_Leaf_Curl_Virus', 'Tomato__Tomato_mosaic_virus',
                    'Tomato___healthy'] 
        predicted_class = class_name[result_index]
        return jsonify({'prediction': predicted_class})
    except Exception as e:
        error_message = str(e)  # Get the error message
        logging.error(f"Prediction endpoint failed: {error_message}")
        traceback.print_exc()  # Print the traceback to get more details
        model_abs_path = os.path.abspath(MODEL_PATH)
        return jsonify({'error': error_message}), 500
        

@app.route('/')
def hello_world():
    return 'Welcome to Floravision Image Disease Detector!'

if __name__ == "__main__":
    app.run()
