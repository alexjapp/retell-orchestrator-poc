import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# --- Setup ---
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration from Environment Variables ---
# Get the URLs of the backend services from environment variables
TICKET_VALIDATOR_URL = os.environ.get('TICKET_VALIDATOR_URL')
CREDENTIAL_SERVICE_URL = os.environ.get('CREDENTIAL_SERVICE_URL')

# --- Health Check Endpoint ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Orchestrator is healthy"}), 200

# --- Main Orchestration Endpoint ---
@app.route('/getPasswordForTicket', methods=['POST'])
def get_password_for_ticket():
    """
    Orchestrates the entire workflow:
    1. Receives a request from Retell AI.
    2. Calls the Ticket Validator service.
    3. If valid, calls the Credential Service.
    4. Returns a final response to Retell AI.
    """
    logging.info("Orchestrator received a new request.")
    data = request.get_json()

    if not data or 'ticket_number' not in data or 'password_type' not in data:
        logging.warning("Bad request: Missing required fields.")
        return jsonify({"error": "Missing 'ticket_number' or 'password_type' in request body"}), 400

    ticket_number = data['ticket_number']
    password_type = data['password_type']

    # --- Step 1: Validate the ticket by calling the Ticket Validator service ---
    logging.info(f"Calling Ticket Validator for ticket: {ticket_number}")
    try:
        validation_response = requests.post(
            TICKET_VALIDATOR_URL,
            json={'ticket_number': ticket_number},
            timeout=5  # 5-second timeout for reliability
        )
        validation_response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        validation_data = validation_response.json()
        
        if validation_data.get('status') != 'valid':
            logging.info(f"Ticket {ticket_number} is invalid.")
            return jsonify({"status": "error", "message": "The provided ticket number is not valid or has been closed."}), 400
        
        device_id = validation_data.get('deviceId')
        logging.info(f"Ticket {ticket_number} is valid for device: {device_id}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Ticket Validator service: {e}")
        return jsonify({"status": "error", "message": "There was a problem validating the ticket. Please try again later."}), 503

    # --- Step 2: Retrieve the password by calling the Credential Service ---
    logging.info(f"Calling Credential Service for device: {device_id}, type: {password_type}")
    try:
        credential_response = requests.get(
            CREDENTIAL_SERVICE_URL,
            params={'deviceId': device_id, 'credentialType': password_type},
            timeout=5 # 5-second timeout
        )
        credential_response.raise_for_status()
        credential_data = credential_response.json()

        password_value = credential_data.get('value')
        logging.warning(f"[AUDIT] Successfully retrieved password for device {device_id}.") # SECURITY AUDIT LOG

        return jsonify({
            "status": "success",
            "password": password_value
        })

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logging.warning(f"Credential not found for device {device_id}, type: {password_type}")
            return jsonify({"status": "error", "message": f"The ticket is valid, but a {password_type} password could not be found for the associated device."}), 404
        else:
            logging.error(f"HTTP Error calling Credential Service: {e}")
            return jsonify({"status": "error", "message": "An unexpected error occurred while retrieving the credential."}), 500
    except requests.exceptions.RequestException as e:
        logging.error(f"Network Error calling Credential Service: {e}")
        return jsonify({"status": "error", "message": "Could not connect to the internal credential service."}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
