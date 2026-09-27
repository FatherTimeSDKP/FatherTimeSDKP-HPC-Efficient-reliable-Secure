import os
import stripe
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI()

# Loaded securely from environment variables — NOT hardcoded
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN = os.getenv("DOMAIN", "http://localhost:8000")

# Map your pricing tiers to Stripe Price IDs (created in your Stripe Dashboard)
PRICE_TIERS = {
    "starter": "price_starter_id_from_stripe",    # e.g., $29/mo
    "pro": "price_pro_id_from_stripe",            # e.g., $99/mo
    "enterprise": "price_enterprise_id_from_stripe" # e.g., $299/mo
}

class CheckoutRequest(BaseModel):
    tier: str
    customer_email: str

@app.post("/create-checkout-session")
def create_checkout_session(data: CheckoutRequest):
    price_id = PRICE_TIERS.get(data.tier.lower())
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid subscription tier selected.")

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=data.customer_email,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=f"{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN}/cancel",
        )
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
