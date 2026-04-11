from flask import Flask, request, jsonify
import uuid
import datetime

app = Flask(__name__)

# Fake data stores in memory
USERS = {
    "usr_12345": {
        "id": "usr_12345",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "status": "ACTIVE",
        "created_at": "2023-10-27T10:00:00Z"
    }
}

ACCOUNTS = {
    "acc_67890": {
        "id": "acc_67890",
        "user_id": "usr_12345",
        "account_type": "INDIVIDUAL",
        "status": "OPEN",
        "configuration": {
            "margin_enabled": False,
            "options_level": 1
        },
        "created_at": "2023-10-27T10:05:00Z"
    }
}

KYC_CHECKS = {
    "kyc_11111": {
        "id": "kyc_11111",
        "user_id": "usr_12345",
        "status": "APPROVED",
        "provider_reference": "ref_abc987",
        "completed_at": "2023-10-27T10:02:00Z"
    }
}

ORDERS = {
    "ord_99999": {
        "id": "ord_99999",
        "account_id": "acc_67890",
        "symbol": "GOOG",
        "side": "BUY",
        "quantity": 10,
        "type": "MARKET",
        "status": "FILLED",
        "created_at": "2023-10-27T10:30:00Z"
    }
}

POSITIONS = {
    "acc_67890": [
        {"symbol": "GOOG", "quantity": 10, "average_price": 150.00}
    ]
}

DEPOSITS = {}

# 1. Create a User Profile (User Identity)
@app.route('/v1/users', methods=['POST'])
def create_user():
    data = request.json or {}
    new_user_id = f"usr_{uuid.uuid4().hex[:8]}"
    new_user = {
        "id": new_user_id,
        "first_name": data.get("first_name", "Jane"),
        "last_name": data.get("last_name", "Smith"),
        "email": data.get("email", "jane.smith@example.com"),
        "status": "PENDING",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    USERS[new_user_id] = new_user
    return jsonify(new_user), 201

# 2. Retrieve User Identity
@app.route('/v1/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = USERS.get(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404

# 3. Submit KYC/AML Check
@app.route('/v1/users/<user_id>/kyc-checks', methods=['POST'])
def submit_kyc(user_id):
    if user_id not in USERS:
        return jsonify({"error": "User not found"}), 404
        
    new_kyc_id = f"kyc_{uuid.uuid4().hex[:8]}"
    kyc_result = {
        "id": new_kyc_id,
        "user_id": user_id,
        "status": "PENDING_REVIEW", 
        "submitted_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    KYC_CHECKS[new_kyc_id] = kyc_result
    return jsonify(kyc_result), 202

# 4. Create an Account (Account Lifecycle Management)
@app.route('/v1/accounts', methods=['POST'])
def create_account():
    data = request.json or {}
    user_id = data.get("user_id")
    if not user_id or user_id not in USERS:
        return jsonify({"error": "Valid user_id is required"}), 400
        
    new_acc_id = f"acc_{uuid.uuid4().hex[:8]}"
    new_account = {
        "id": new_acc_id,
        "user_id": user_id,
        "account_type": data.get("account_type", "INDIVIDUAL"),
        "status": "PENDING_FUNDING",
        "configuration": {
            "margin_enabled": False,
            "options_level": 0
        },
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    ACCOUNTS[new_acc_id] = new_account
    return jsonify(new_account), 201

# 5. Update Account Configuration
@app.route('/v1/accounts/<account_id>/configuration', methods=['PATCH'])
def update_account_configuration(account_id):
    account = ACCOUNTS.get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
        
    data = request.json or {}
    if "margin_enabled" in data:
        account["configuration"]["margin_enabled"] = data["margin_enabled"]
    if "options_level" in data:
        account["configuration"]["options_level"] = data["options_level"]
        
    return jsonify(account), 200

# 11. Retrieve Account Details
@app.route('/v2/accounts/<account_id>', methods=['GET'])
def get_account(account_id):
    account = ACCOUNTS.get(account_id)
    if account:
        return jsonify(account), 200
    return jsonify({"error": "Account not found"}), 404

# --- APIs Outside the Core Team's Purview ---

# 6. Retrieve Market Data Quote
@app.route('/v1/market-data/quotes/<symbol>', methods=['GET'])
def get_quote(symbol):
    return jsonify({
        "symbol": symbol.upper(),
        "price": 150.25,
        "bid": 150.20,
        "ask": 150.30,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }), 200

# 7. Submit a Trade Order
@app.route('/v1/trading/orders', methods=['POST'])
def place_order():
    data = request.json or {}
    account_id = data.get("account_id")
    if not account_id or account_id not in ACCOUNTS:
        return jsonify({"error": "Valid account_id is required"}), 400
        
    new_ord_id = f"ord_{uuid.uuid4().hex[:8]}"
    new_order = {
        "id": new_ord_id,
        "account_id": account_id,
        "symbol": data.get("symbol", "GOOG").upper(),
        "side": data.get("side", "BUY"),
        "quantity": data.get("quantity", 1),
        "type": data.get("type", "MARKET"),
        "status": "PENDING",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    ORDERS[new_ord_id] = new_order
    return jsonify(new_order), 201

# 8. Retrieve Order Status
@app.route('/v1/trading/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = ORDERS.get(order_id)
    if order:
        return jsonify(order), 200
    return jsonify({"error": "Order not found"}), 404

# 9. Get Account Positions
@app.route('/v1/portfolio/<account_id>/positions', methods=['GET'])
def get_positions(account_id):
    if account_id not in ACCOUNTS:
        return jsonify({"error": "Account not found"}), 404
    positions = POSITIONS.get(account_id, [])
    return jsonify({"account_id": account_id, "positions": positions}), 200

# 10. Submit a Deposit
@app.route('/v1/payments/deposits', methods=['POST'])
def submit_deposit():
    data = request.json or {}
    account_id = data.get("account_id")
    amount = data.get("amount")
    if not account_id or account_id not in ACCOUNTS:
        return jsonify({"error": "Valid account_id is required"}), 400
    if not amount or amount <= 0:
        return jsonify({"error": "Valid positive amount is required"}), 400
        
    deposit_id = f"dep_{uuid.uuid4().hex[:8]}"
    deposit = {
        "id": deposit_id,
        "account_id": account_id,
        "amount": amount,
        "status": "PROCESSING",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    DEPOSITS[deposit_id] = deposit
    return jsonify(deposit), 202

# 12. Retrieve Deposit Status
@app.route('/v2/payments/deposits/<deposit_id>', methods=['GET'])
def get_deposit(deposit_id):
    deposit = DEPOSITS.get(deposit_id)
    if deposit:
        return jsonify(deposit), 200
    return jsonify({"error": "Deposit not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=8080)
