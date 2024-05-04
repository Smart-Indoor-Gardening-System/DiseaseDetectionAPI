# DiseaseDetectionAPI
A python flask rest api that use a trained tensorflow keras model  from AWS S3 for predicting disease , deployed on AWS EC2 Ubuntu instance with NGINX . Application Performance Monitoring done by Elastic APM  through elastic apm agent configured on the flask app.
# AI Disease Detector API Documentation

## Endpoints

### Predict Disease
- **Endpoint**: `/predict`
- **Method**: `POST`
- **Description**: Predicts the disease in a plant image.
- **Request Body**:
  - Form data with key `file` containing the plant image file.
- **Response**:
  - If successful, returns a JSON object with the predicted disease class.
  - If unsuccessful, returns an error message.

### Health Check
- **Endpoint**: `/`
- **Method**: `GET`
- **Description**: A simple health check endpoint to verify if the API is running.
- **Response**: Returns a welcome message indicating that the API is operational.

## Error Handling
- If any errors occur during the prediction process, appropriate error messages are returned along with HTTP status codes.

## Usage Example

import requests

# API endpoint
url = 'https://ec2_instance_ip_or_domain/predict'

# Load image file
files = {'file': open('plant_image.jpg', 'rb')}

# Send prediction request
response = requests.post(url, files=files)

# Print prediction result
print(response.json())


## Installation and Setup

1. Clone the repository or download the source code.
2. Install required Python packages using `pip install -r requirements.txt`.
3. Set up AWS S3 bucket with the trained model file.
4. Configure NGINX to forward requests to the Flask app.
5. Set up Elastic APM and configure the Flask application with the Elastic APM agent.

### Configuration

#### AWS S3 Configuration
- Ensure that the AWS credentials with access to the S3 bucket are properly configured.
- Update the `download_model_from_s3` function with the appropriate S3 bucket name and model file name.

#### NGINX Configuration
- Configure NGINX to forward requests to the Flask app running on a port.

#### Elastic APM Configuration
- Set up an Elastic APM instance and obtain the service name, secret token, and server URL.
- Update the `app.config['ELASTIC_APM']` dictionary with the obtained credentials.

### Dependencies

- Flask
- Flask-CORS
- ElasticAPM
- TensorFlow
- Boto3



