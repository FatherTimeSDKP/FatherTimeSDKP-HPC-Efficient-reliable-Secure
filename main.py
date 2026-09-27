import os
import uuid
import stripe
from fastapi import FastAPI, Security, HTTPException, Request, status, Header
from fastapi.security.api_key import APIKeyHeader
from google.cloud import firestore

app = FastAPI(title="FatherTimeSDKP Coherence API")

# Configure Stripe & GCP
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Initialize Firestore Client (Runs seamlessly on Google Cloud / Cloud Run)
db = firestore.Client()
keys_ref = db.collection("api_keys")

# Security setup
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is missing."
        )
    
    # Check key in Firestore
    key_doc = keys_ref.document(api_key).get()
    if not key_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key."
        )
    
    key_data = key_doc.to_dict()
    if key_data.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription inactive. Please renew your plan."
        )
    
    return key_data

# ==========================================
# MONETIZED ENDPOINTS
# ==========================================

@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "SDKP-Recovered-v2"}

@app.post("/v1/coherence")
async def run_coherence(payload: dict, client_info: dict = Security(verify_api_key)):
    # Your recovered coherence engine logic
    return {
        "status": "success",
        "coherence_index": 0.9842,
        "input_dimension": len(payload.get("data", [])),
        "authorized_user": client_info.get("email")
    }

@app.post("/v1/evolve")
async def run_evolve(payload: dict, client_info: dict = Security(verify_api_key)):
    # Your recovered evolution simulation engine logic
    return {
        "status": "success",
        "evolution_cycles": 120,
        "coherence_stabilized": True
    }

# ==========================================
# STRIPE WEBHOOK HANDLER
# ==========================================

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle successful subscription
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email")
        stripe_sub_id = session.get("subscription")
        
        # Generate a new secure API Key
        new_api_key = f"sk_sdkp_{uuid.uuid4().hex}"
        
        # Save to Firestore
        keys_ref.document(new_api_key).set({
            "email": customer_email,
            "stripe_subscription_id": stripe_sub_id,
            "status": "active",
            "tier": "developer" # Can be customized based on price ID
        })
        
        # OPTIONAL: Send email to customer with their new_api_key here
        print(f"Provisioned API Key {new_api_key} for {customer_email}")

    # Handle subscription cancellation
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        sub_id = subscription.get("id")
        
        # Query API keys associated with this subscription ID and deactivate
        docs = keys_ref.where("stripe_subscription_id", "==", sub_id).stream()
        for doc in docs:
            keys_ref.document(doc.id).update({"status": "suspended"})
            print(f"Suspended API Key: {doc.id} due to cancelled subscription.")

    return {"status": "received"}
