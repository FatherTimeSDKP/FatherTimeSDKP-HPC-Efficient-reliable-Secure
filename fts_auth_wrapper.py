"""
FatherTimeSDKP Unified Framework — Cryptographic Provenance & API Auth Wrapper
Author: Donald Paul Smith (Father Time)
ORCID: 0009-0003-7925-1653
Module: fts_auth_wrapper.py
Governance: Dallas's Code + Tiered API Key Gate
License: CC BY 4.0
"""

import os
import hashlib
import json
import time
import sqlite3
from typing import Dict, Any, Optional
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

# --- 1. DALLAS'S CODE PROVENANCE SIGNER ---

class DallasCodeSigner:
    """
    Secures simulation log arrays by binding structural payloads to a
    prime-terminated validation scalar.
    """
    def __init__(self):
        self.algorithm = "sha256"

    def _is_prime(self, n: int) -> bool:
        """Primality check with 6k +/- 1 step optimization."""
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        for i in range(5, int(n ** 0.5) + 1, 6):
            if n % i == 0 or n % (i + 2) == 0:
                return False
        return True

    def _generate_prime_terminus(self, seed_value: int) -> int:
        """Finds the nearest subsequent prime number."""
        target = max(2, seed_value)
        if target > 2 and target % 2 == 0:
            target += 1
        while not self._is_prime(target):
            target += 2
        return target

    def generate_digital_crystal_seal(self, simulation_log: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates SHA256 base hash and Dallas's Code prime terminus."""
        serialized = json.dumps(simulation_log, sort_keys=True).encode("utf-8")
        hasher = hashlib.new(self.algorithm)
        hasher.update(serialized)
        hex_digest = hasher.hexdigest()

        hash_seed = int(hex_digest[-8:], 16)
        prime_scalar = self._generate_prime_terminus(hash_seed)

        seal = {
            "version": "FTS-AUTH-CRYSTAL-369",
            "timestamp_epoch": time.time(),
            "data_hash": hex_digest,
            "dallas_code_terminus": prime_scalar,
            "signature_manifold": f"{hex_digest}::{prime_scalar}",
        }

        return {
            "provenance_payload": simulation_log,
            "security_seal": seal
        }

    def verify_digital_crystal_seal(self, protected_block: Dict[str, Any]) -> bool:
        """Validates payload integrity against the prime seal."""
        try:
            payload = protected_block.get("provenance_payload", {})
            seal = protected_block.get("security_seal", {})

            serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
            hasher = hashlib.new(self.algorithm)
            hasher.update(serialized)
            expected_hash = hasher.hexdigest()

            if seal.get("data_hash") != expected_hash:
                return False

            hash_seed = int(expected_hash[-8:], 16)
            expected_prime = self._generate_prime_terminus(hash_seed)

            return (
                seal.get("dallas_code_terminus") == expected_prime and
                seal.get("signature_manifold") == f"{expected_hash}::{expected_prime}"
            )
        except Exception:
            return False


# --- 2. STRIPE & API-KEY MIDDLEWARE GATE ---

DB_PATH = os.getenv("API_DB_PATH", "fts_subscribers.db")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def init_subscriber_db():
    """Initializes local SQLite database for API keys and Stripe tiers."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                api_key TEXT PRIMARY KEY,
                tier TEXT NOT NULL,         -- 'starter', 'pro', 'enterprise'
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                active INTEGER DEFAULT 1,
                created_at REAL
            )
        """)
init_subscriber_db()

def verify_fts_client(api_key: Optional[str] = Security(API_KEY_HEADER)) -> Dict[str, Any]:
    """
    FastAPI dependency: Blocks unauthorized requests and checks subscription status.
    """
    # Allow emergency admin bypass if configured in cloud environment variables
    master_key = os.getenv("FTS_MASTER_ADMIN_KEY")
    if master_key and api_key == master_key:
        return {"tier": "enterprise", "stripe_customer_id": "internal_admin"}

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing 'X-API-Key' header. Purchase an API key via Stripe."
        )

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tier, stripe_customer_id, active FROM subscribers WHERE api_key = ?",
            (api_key,)
        )
        row = cursor.fetchone()

        if not row or row[2] != 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or suspended API key. Check subscription status in Stripe."
            )

        return {
            "tier": row[0],
            "stripe_customer_id": row[1]
        }
