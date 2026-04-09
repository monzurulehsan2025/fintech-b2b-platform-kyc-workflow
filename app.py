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

if __name__ == '__main__':
    app.run(debug=True, port=8080)
