"""
FatherTimeSDKP HPC Engine — High-Performance API Service
Author: Donald Paul Smith (Father Time)
ORCID: 0009-0003-7925-1653
File: fastapi_sdkp_app.py
Deployment: Render / IBM Cloud Code Engine compatible
"""

import os
import time
import math
import secrets
import sqlite3
from typing import List, Dict, Any, Optional

import stripe
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import cryptographic signer and subscriber verification from local wrapper
from fts_auth_wrapper import DallasCodeSigner, verify_fts_client, DB_PATH

# -------------------------------------------------------------------
# Configuration & Environment
# -------------------------------------------------------------------
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
DOMAIN = os.getenv("DOMAIN", "http://localhost:8000")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Stripe Price IDs (Set these in your Render / IBM Cloud environment dashboard)
STRIPE_PRICE_TIERS = {
    "starter": os.getenv("STRIPE_PRICE_STARTER", "price_starter_sample_id"),      # $29/mo
    "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_sample_id"),                  # $99/mo
    "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE", "price_enterprise_sample_id") # $299/mo
}

# -------------------------------------------------------------------
# Application Initialization
# -------------------------------------------------------------------
app = FastAPI(
    title="FatherTimeSDKP HPC Engine API",
    description="Deterministic state evolution, coherence metrics, and Dallas's Code crystal sealing.",
    version="1.0.0"
)

# Enable CORS for frontend landing pages & web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

signer = DallasCodeSigner()

# -------------------------------------------------------------------
# Pydantic Request & Response Schemas
# -------------------------------------------------------------------
class CoherenceRequest(BaseModel):
    state_vector: List[float] = Field(..., example=[0.7071, 0.0, 0.7071, 0.0])
    coupling_constant: float = Field(1.0, example=1.05)
    dimension: Optional[int] = Field(4, example=4)

class EvolveRequest(BaseModel):
    state_vector: List[float] = Field(..., example=[1.0, 0.0, 0.0, 0.0])
    steps: int = Field(50, ge=1, le=5000, example=100)
    dt: float = Field(0.01, gt=0, example=0.01)
    damping_factor: float = Field(0.02, ge=0, example=0.01)

class CheckoutRequest(BaseModel):
    tier: str = Field(..., example="pro")  # 'starter', 'pro', or 'enterprise'
    customer_email: str = Field(..., example="researcher@lab.org")

class VerifySealRequest(BaseModel):
    provenance_payload: Dict[str, Any]
    security_seal: Dict[str, Any]


# -------------------------------------------------------------------
# Core Math / Engine Projection Routines
# -------------------------------------------------------------------
def calculate_coherence_metric(vector: List[float], coupling: float) -> Dict[str, Any]:
    """Calculates deterministic entropy and phase coherence for state vectors."""
    norm_sq = sum(x**2 for x in vector)
    norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
    normalized = [x / norm for x in vector]

    # Deterministic Shannon-like coherence index
    entropy = -sum((x**2) * math.log(x**2 + 1e-12) for x in normalized)
    coherence_index = math.exp(-entropy * coupling)

    return {
        "norm": round(norm, 6),
        "coherence_index": round(coherence_index, 6),
        "normalized_states": [round(x, 6) for x in normalized],
        "coupling_applied": coupling
    }

def project_state_evolution(initial: List[float], steps: int, dt: float, damping: float) -> Dict[str, Any]:
    """Computes forward-state manifold projection over discrete time steps."""
    current = list(initial)
    dim = len(current)
    history = []

    for step in range(steps):
        # State transformation: harmonic coupling with damping dissipation
        next_state = []
        for i in range(dim):
            coupled_term = sum(current[(i + j) % dim] * 0.1 for j in range(dim))
            val = current[i] + (-damping * current[i] + coupled_term) * dt
            next_state.append(val)

        # Normalize to maintain metric bounds
        mag = math.sqrt(sum(v**2 for v in next_state)) or 1.0
        current = [v / mag for v in next_state]

        if step % max(1, steps // 5) == 0 or step == steps - 1:
            history.append({
                "step": step,
                "time": round(step * dt, 4),
                "state": [round(v, 6) for v in current]
            })

    return {
        "steps_completed": steps,
        "delta_t": dt,
        "final_state": [round(v, 6) for v in current],
        "trajectory_snapshots": history
    }


# -------------------------------------------------------------------
# Unprotected / Health Endpoints
# -------------------------------------------------------------------
@app.get("/health", tags=["Status"])
def health_check():
    """Public health monitor for uptime monitors and load balancers."""
    return {
        "status": "healthy",
        "engine": "FatherTimeSDKP-HPC",
        "author": "Donald Paul Smith (Father Time)",
        "crystal_version": "FTS-AUTH-CRYSTAL-369",
        "timestamp_epoch": time.time()
    }

@app.post("/v1/verify-seal", tags=["Provenance"])
def verify_seal(envelope: VerifySealRequest):
    """Public validation endpoint to verify any Dallas's Code digital crystal seal."""
    valid = signer.verify_digital_crystal_seal(envelope.model_dump())
    return {
        "valid": valid,
        "signature_intact": valid,
        "inspected_at": time.time()
    }


# -------------------------------------------------------------------
# Protected Calculation Endpoints (Gated by X-API-Key)
# -------------------------------------------------------------------
@app.post("/v1/coherence", tags=["Compute"])
def run_coherence(request: CoherenceRequest, client: Dict[str, Any] = Depends(verify_fts_client)):
    """Computes state coherence and returns a Dallas's Code cryptographically sealed envelope."""
    metrics = calculate_coherence_metric(request.state_vector, request.coupling_constant)
    
    payload = {
        "operation": "coherence_metric_v1",
        "subscriber_tier": client["tier"],
        "results": metrics,
        "execution_timestamp": time.time()
    }

    # Stamp payload with prime-terminated cryptographic seal
    sealed_block = signer.generate_digital_crystal_seal(payload)
    return sealed_block

@app.post("/v1/evolve", tags=["Compute"])
def run_evolve(request: EvolveRequest, client: Dict[str, Any] = Depends(verify_fts_client)):
    """Computes forward state projection and returns a Dallas's Code sealed envelope."""
    # Restrict step size according to paid subscription tier
    max_steps = 1000 if client["tier"] == "starter" else 5000
    if request.steps > max_steps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tier '{client['tier']}' allows a maximum of {max_steps} steps. Upgrade to Pro/Enterprise."
        )

    evolution = project_state_evolution(request.state_vector, request.steps, request.dt, request.damping_factor)

    payload = {
        "operation": "forward_state_evolution_v1",
        "subscriber_tier": client["tier"],
        "results": evolution,
        "execution_timestamp": time.time()
    }

    # Stamp payload with prime-terminated cryptographic seal
    sealed_block = signer.generate_digital_crystal_seal(payload)
    return sealed_block


# -------------------------------------------------------------------
# Stripe Monetization & Webhooks
# -------------------------------------------------------------------
@app.post("/v1/billing/create-checkout-session", tags=["Billing"])
def create_checkout_session(data: CheckoutRequest):
    """Generates a Stripe Hosted Checkout Session link for Starter, Pro, or Enterprise tiers."""
    tier = data.tier.lower()
    price_id = STRIPE_PRICE_TIERS.get(tier)

    if not price_id or price_id.startswith("price_") and len(price_id) < 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subscription tier '{tier}' is not currently configured with a valid Stripe Price ID."
        )

    try:
        session = stripe.checkout.Session.create(
            customer_email=data.customer_email,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            metadata={"tier": tier},
            success_url=f"{DOMAIN}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN}/billing/cancel",
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/v1/billing/webhook", tags=["Billing"])
async def stripe_webhook(request: Request):
    """
    Receives Stripe events:
    Automatically provisions and stores an API key in fts_subscribers.db upon payment.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="STRIPE_WEBHOOK_SECRET not set.")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Webhook signature error: {str(e)}")

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        tier = session.get("metadata", {}).get("tier", "starter")

        # Generate fresh production API Key
        new_api_key = f"fts_live_{secrets.token_urlsafe(32)}"

        # Store in SQLite database
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO subscribers 
                (api_key, tier, stripe_customer_id, stripe_subscription_id, active, created_at)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (new_api_key, tier, customer_id, subscription_id, time.time()))

        print(f"[FTS BILLING] Successfully provisioned API Key: {new_api_key} for {email} ({tier})")

    elif event_type in ("customer.subscription.deleted", "invoice.payment_failed"):
        subscription = event["data"]["object"]
        sub_id = subscription.get("id")

        # Revoke key access
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE subscribers SET active = 0 WHERE stripe_subscription_id = ?", (sub_id,))

        print(f"[FTS BILLING] Subscription {sub_id} deactivated.")

    return {"status": "success"}


# -------------------------------------------------------------------
# Entrypoint for Local / Cloud Runtimes (Render, IBM Cloud)
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    # Render and IBM Cloud Code Engine inject PORT automatically
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("fastapi_sdkp_app:app", host="0.0.0.0", port=port, reload=False)
