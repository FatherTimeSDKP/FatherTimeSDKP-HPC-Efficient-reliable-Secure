import os
import secrets
from flask import Flask, jsonify, request
import stripe

app = Flask(__name__)

# Load keys securely from environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
ENDPOINT_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@app.route("/", methods=["GET"])
def home():
  return (
      jsonify({
          "status": "online",
          "framework": "FatherTimeSDKP-HPC-AI-Engine",
          "message": (
              "Backend operational. Framework Abell predictions match empirical"
              " data[cite: 1]."
          ),
      }),
      200,
  )


@app.route("/health", methods=["GET"])
def health_check():
  return jsonify({"status": "healthy"}), 200


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
  payload = request.get_data(as_text=True)
  sig_header = request.headers.get("Stripe-Signature")

  try:
    event = stripe.Webhook.construct_event(payload, sig_header, ENDPOINT_SECRET)
  except ValueError:
    return jsonify({"error": "Invalid payload"}), 400
  except stripe.error.SignatureVerificationError:
    return jsonify({"error": "Invalid signature"}), 400

  if event["type"] == "checkout.session.completed":
    session = event["data"]["object"]
    customer_email = session.get("customer_email") or session.get(
        "customer_details", {}
    ).get("email")
    payment_status = session.get("payment_status")

    if payment_status == "paid":
      api_key = f"ftp_{secrets.token_hex(24)}"
      print(f"Success: Payment confirmed for {customer_email}.")
      print(f"Generated API Key: {api_key}")
      # Add your database logic or automated email dispatch here

  return jsonify({"status": "success"}), 200


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
