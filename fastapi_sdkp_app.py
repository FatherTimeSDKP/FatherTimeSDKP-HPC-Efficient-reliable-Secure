"""
FatherTimeSDKP FastAPI surface wired to syntax-recovered engine modules.

Modules:
  - sdkp_sdvr_engine.py   (from SDKP_SDVR_Engine.py)
  - kapnack_integrator.py (from Kapnack_solver.py)
  - fts_auth_wrapper.py   (Dallas code seal)

Run:
  pip install fastapi uvicorn pydantic
  uvicorn fastapi_sdkp_app:app --reload --port 8000
"""

from __future__ import annotations

from typing import List, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sdkp_sdvr_engine import BodySDVR, KapnackEngine, EOS
from kapnack_integrator import KapnackIntegrator
from fts_auth_wrapper import DallasCodeSigner

app = FastAPI(
    title="FatherTimeSDKP Kapnack API",
    version="0.2.0",
    description=(
        "HTTP API over syntax-recovered sdkp_sdvr_engine + kapnack_integrator "
        "(upstream FatherTimeSDKP-HPC-Efficient-reliable-Secure)."
    ),
)
signer = DallasCodeSigner()


class BodyIn(BaseModel):
    body_id: str = "node"
    size: float = Field(1.0, gt=0, description="S [m]")
    density: float = Field(1.0, gt=0, description="D [kg/m^3]")
    velocity: float = Field(0.0, description="V [m/s]")
    rotation: float = Field(0.0, description="R [rad/s]")
    solid: str = "cube"
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)


class CoherenceRequest(BaseModel):
    bodies: List[BodyIn]
    harmonic_order: int = 9


class EvolveRequest(BaseModel):
    bodies: List[BodyIn]
    total_time: float = Field(1.0, gt=0)
    steps: int = Field(5, ge=1, le=10_000)
    harmonic_order: int = 9
    seal: bool = True


def _to_bodies(items: List[BodyIn]) -> list[BodySDVR]:
    try:
        return [
            BodySDVR(
                body_id=b.body_id,
                size=b.size,
                density=b.density,
                velocity=b.velocity,
                rotation=b.rotation,
                solid=b.solid,
                position=tuple(b.position),
            )
            for b in items
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "eos_m_s": EOS,
        "engine": "sdkp_sdvr_engine+kapnack_integrator (syntax-recovered)",
    }


@app.post("/v1/coherence")
def evaluate_coherence(req: CoherenceRequest):
    if req.harmonic_order not in (3, 6, 9, 12):
        raise HTTPException(400, "harmonic_order must be 3, 6, 9, or 12")
    if len(req.bodies) < 1:
        raise HTTPException(400, "at least one body required")
    engine = KapnackEngine(harmonic_order=req.harmonic_order)
    report = engine.system_coherence(_to_bodies(req.bodies))
    sealed = signer.generate_digital_crystal_seal(
        {"endpoint": "coherence", "report": report}
    )
    return {
        "status": "SUCCESS",
        "report": report,
        "dallas_code_seal": sealed["security_seal"],
    }


@app.post("/v1/evolve")
def simulate_time_evolution(req: EvolveRequest):
    if req.harmonic_order not in (3, 6, 9, 12):
        raise HTTPException(400, "harmonic_order must be 3, 6, 9, or 12")
    if len(req.bodies) < 2:
        raise HTTPException(400, "evolve needs at least 2 bodies")
    engine = KapnackEngine(harmonic_order=req.harmonic_order)
    integ = KapnackIntegrator(engine, verbose=False)
    history = integ.run_simulation(
        _to_bodies(req.bodies), total_time=req.total_time, steps=req.steps
    )
    payload = {
        "status": "SUCCESS",
        "epochs": len(history),
        "history": history,
        "convergence": integ.convergence_report(),
    }
    if req.seal:
        sealed = signer.generate_digital_crystal_seal(
            {
                "endpoint": "evolve",
                "epochs": len(history),
                "final": history[-1] if history else {},
            }
        )
        payload["dallas_code_seal"] = sealed["security_seal"]
    return payload
