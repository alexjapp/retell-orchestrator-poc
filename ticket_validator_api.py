from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# --- Synthetic Data Store ---
# In a real-world scenario, this would query a database.
# For our PoC, we use a simple Python dictionary to simulate the database.
SIMULATED_TICKETS = {
    # Existing Tickets
    "TICKET-12345": {"status": "valid", "deviceId": "ATM-CLE-001"},
    "TICKET-67890": {"status": "valid", "deviceId": "ATM-CHI-007"},
    "TICKET-54321": {"status": "valid", "deviceId": "ATM-NYC-003"},
    "TICKET-99999": {"status": "invalid", "deviceId": None},
    
    # --- Newly Enumerated Tickets ---
    "TICKET-11223": {"status": "valid", "deviceId": "ATM-CLE-001"},
    "TICKET-33445": {"status": "valid", "deviceId": "ATM-CHI-007"},
    "TICKET-55667": {"status": "valid", "deviceId": "ATM-NYC-003"},
    "TICKET-77889": {"status": "valid", "deviceId": "ATM-LAX-001"}, # New device
    "TICKET-24680": {"status": "closed", "deviceId": "ATM-CLE-001"}, # Closed ticket
    "TICKET-13579": {"status": "invalid", "deviceId": None}
}

@app.route('/validate', methods=['POST'])
def validate_ticket():
    """
    Validates a ticket number from a POST request JSON body.
    """
    print("Received validation request...")
    data = request.get_json()

    if not data or 'ticket_number' not in data:
        print("Error: 'ticket_number' not in request body.")
        return jsonify({"error": "Missing 'ticket_number' in request body"}), 400

    ticket_number = data['ticket_number']
    print(f"Validating ticket: {ticket_number}")

    # Look up the ticket in our simulated database
    ticket_info = SIMULATED_TICKETS.get(ticket_number)

    if ticket_info and ticket_info['status'] == 'valid':
        print(f"Ticket {ticket_number} is valid for device {ticket_info['deviceId']}.")
        return jsonify({
            "ticket_number": ticket_number,
            "status": "valid",
            "deviceId": ticket_info['deviceId']
        })
    else:
        print(f"Ticket {ticket_number} is invalid or not found.")
        return jsonify({
            "ticket_number": ticket_number,
            "status": "invalid"
        }), 404

if __name__ == '__main__':
    # The port is often set by the App Service environment, but we define a default.
    app.run(host='0.0.0.0', port=8000)
