import os
import secrets
from flask import Flask, jsonify, request
import stripe

app = Flask(__name__)

# Load keys from secure environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
ENDPOINT_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
  payload = request.get_data(as_text=True)
  sig_header = request.headers.get("Stripe-Signature")

  try:
    # Verify the event came from Stripe securely
    event = stripe.Webhook.construct_event(payload, sig_header, ENDPOINT_SECRET)
  except ValueError:
    # Invalid payload structure
    return jsonify({"error": "Invalid payload"}), 400
  except stripe.error.SignatureVerificationError:
    # Invalid signature verification
    return jsonify({"error": "Invalid signature"}), 400

  # Handle successful checkout completion
  if event["type"] == "checkout.session.completed":
    session = event["data"]["object"]

    customer_email = session.get("customer_email") or session.get(
        "customer_details", {}
    ).get("email")
    payment_status = session.get("payment_status")

    if payment_status == "paid":
      # Generate a secure cryptographically random API key
      api_key = f"ftp_{secrets.token_hex(24)}"

      # TODO: Insert code here to save customer_email and api_key to your database
      # and associate it with your GitLab group (ID: 109656962) deployment pipelines.
      print(f"Success: Payment confirmed for {customer_email}.")
      print(f"Generated API Key: {api_key}")

      # Optional: integrate an SMTP/SendGrid call here to email the key to the client automatically.

  return jsonify({"status": "success"}), 200


if __name__ == "__main__":
  app.run(port=4242)
