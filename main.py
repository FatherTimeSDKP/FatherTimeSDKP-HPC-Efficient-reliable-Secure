import os
import yaml
import torch
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import stripe

from src.sdkp_tensor import SDKPStateTensor
from src.vortex_369 import Vortex369Compressor
from src.metatron_router import MetatronCubeRouter
from src.dcp_provenance import DigitalCrystalProtocol

app = FastAPI(
    title="FatherTimeSDKP-HPC-AI-Engine",
    description="High-Performance Computing & Stripe Monetization Gateway for SDKP Framework",
    version="2026.1"
)

# Initialize Stripe API keys from IBM Cloud environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")

class PaymentRequest(BaseModel):
    amount: int  # Amount in smallest currency unit (e.g., cents)
    currency: str = "usd"

@app.get("/health")
def health_check():
    """
    Health check route for IBM Cloud Code Engine container deployment.
    """
    return {
        "status": "healthy",
        "service": "FatherTimeSDKP-HPC-AI-Engine",
        "author": "Donald Paul Smith",
        "orcid": "0009-0003-7925-1653",
        "protocol": "Digital Crystal Protocol (DCP)"
    }

@app.post("/create-payment-intent")
def create_payment_intent(data: PaymentRequest):
    """
    Generates a Stripe Payment Intent for metered API usage and framework licensing.
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=data.amount,
            currency=data.currency,
            automatic_payment_methods={"enabled": True},
        )
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Validates incoming Stripe cryptographic signature headers and executes settlement logic.
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload structure.")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid cryptographic signature.")

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        print(f"Verified successful payment transaction: {payment_intent.get('id')}")

    return {"status": "success", "event_processed": event["type"]}

@app.post("/v1/predict")
def run_sdkp_inference_pipeline():
    """
    Executes the core SDKP tensor forward pass and generates immutable DCP cryptographic proof.
    """
    # 1. SDKP Continuous State Tensor Execution
    state_engine = SDKPStateTensor()
    current_state = state_engine.get_state_vector()
    
    # 2. Digital Crystal Protocol (DCP) Provenance Stamp
    dcp = DigitalCrystalProtocol(
        author="Donald Paul Smith", 
        orcid="0009-0003-7925-1653"
    )
    
    ledger_hash = dcp.generate_crystal_hash({
        "sdkp_state": current_state.detach().tolist(),
        "royalty_routing": "FatherTimeSDKP.eth"
    })
    
    return {
        "status": "inference_complete",
        "state_vector": current_state.detach().tolist(),
        "dcp_ledger_hash": ledger_hash
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
