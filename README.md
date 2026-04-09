# Fintech Users and Accounts API

This is a functional mock backend service for a generic B2B financial technology platform. It provides foundational APIs that power user identity, account lifecycle management, KYC/AML workflows, and account configuration.

## Available APIs

This service implements 5 core endpoints to handle standard fintech onboarding flows:

1. **`POST /v1/users` (User Identity Creation)**
   - Used by clients to onboard a new retail customer. Takes basic PII and creates a user profile.
2. **`GET /v1/users/{userId}` (User Identity Retrieval)**
   - Used to fetch the details and latest status of a user profile.
3. **`POST /v1/users/{userId}/kyc-checks` (KYC/AML Workflow)**
   - Used to submit a user's verification documents to trigger background checks for Anti-Money Laundering (AML) and Know Your Customer (KYC).
4. **`POST /v1/accounts` (Account Lifecycle Management)**
   - Used to create a brokerage application or trading account linked to a specific user identity.
5. **`PATCH /v1/accounts/{accountId}/configuration` (Account Configuration)**
   - Used to manage features on the account, such as updating margin settings, enabling options trading, or modifying associated risk limits.

## Implementation Details

The project is a lightweight web server built using Python and Flask. It functions fully in-memory and is pre-seeded with sample data to accelerate integration testing. 

### How to Run:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
*(The server will run on port 8080)*

### Example requests:
```bash
# Retrieve existing user
curl http://localhost:8080/v1/users/usr_12345

# Create a new user
curl -X POST -H "Content-Type: application/json" -d '{"first_name": "Alice", "last_name": "Zimmerman"}' http://localhost:8080/v1/users

# Configure account
curl -X PATCH -H "Content-Type: application/json" -d '{"options_level": 3}' http://localhost:8080/v1/accounts/acc_67890/configuration
```
