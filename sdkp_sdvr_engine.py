"""FatherTimeSDKP SDVR multi-body simulation engine (syntax-recovered).

Recovered for importability from upstream GitHub content:
  FatherTimeSDKP/FatherTimeSDKP-HPC-Efficient-reliable-Secure/SDKP_SDVR_Engine.py

Upstream author: Donald Paul Smith (Father Time)
ORCID: 0009-0003-7925-1653
DOI referenced upstream: 10.5281/zenodo.15745609

Recovery notes:
  - Smart quotes, markdown fences, and broken module headers removed.
  - Class/method structure restored so the module imports under Python 3.
  - Algorithms and constants follow the upstream source text.
"""

from __future__ import annotations

import math
import itertools
from dataclasses import dataclass, field
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Physical constants (upstream)
# ---------------------------------------------------------------------------

EOS = 29_780.0          # m/s — Earth Orbital Speed (SDKP local constant)
EOS_DEV_LOW = 0.0013    # 0.13% lower EOS deviation band
EOS_DEV_HIGH = 0.0020   # 0.20% upper EOS deviation band
G_NEWTON = 6.674e-11
C_LIGHT = 299_792_458.0
K_BOLTZMANN = 1.380649e-23

SDN_SOLIDS = {
    "tetrahedron":  {"F": 4,  "V": 4,  "E": 6,  "dual": "tetrahedron"},
    "cube":         {"F": 6,  "V": 8,  "E": 12, "dual": "octahedron"},
    "octahedron":   {"F": 8,  "V": 6,  "E": 12, "dual": "cube"},
    "dodecahedron": {"F": 12, "V": 20, "E": 30, "dual": "icosahedron"},
    "icosahedron":  {"F": 20, "V": 12, "E": 30, "dual": "dodecahedron"},
    # practical alias used in API examples / upstream tests
    "sphere":       {"F": 1,  "V": 1,  "E": 1,  "dual": "sphere"},
}

SDN_VORTEX = {
    3: "micro structural unit (local geometry seed)",
    6: "mid-range transition (face-vertex coupling)",
    9: "macro resonance closure (edge-complete state)",
    12: "full dimensional lock (SD&N dodecahedral)",
}


def sdn_shape_factor(solid_name: str) -> float:
    """phi_SDN = (F * V) / E for a named Platonic solid."""
    if solid_name not in SDN_SOLIDS:
        raise ValueError(
            f"Unknown solid '{solid_name}'. Valid: {list(SDN_SOLIDS.keys())}"
        )
    s = SDN_SOLIDS[solid_name]
    return (s["F"] * s["V"]) / max(s["E"], 1)


def sdn_phase_factor(solid_name: str) -> float:
    """Geometric phase factor phi = 2*pi / N_nodes, N_nodes = F+V+E."""
    s = SDN_SOLIDS[solid_name]
    n_nodes = s["F"] + s["V"] + s["E"]
    return 2 * math.pi / max(n_nodes, 1)


def euler_verify(solid_name: str) -> bool:
    """Euler polyhedral check F - E + V == 2 (sphere alias is exempt)."""
    if solid_name == "sphere":
        return True
    s = SDN_SOLIDS[solid_name]
    return (s["F"] - s["E"] + s["V"]) == 2


@dataclass
class BodySDVR:
    """Physical system node described by the SDVR state vector (SI units)."""

    body_id: str
    size: float          # S [m]
    density: float       # D [kg/m^3]
    velocity: float      # V [m/s]
    rotation: float      # R [rad/s]
    solid: str = "cube"
    position: tuple = (0.0, 0.0, 0.0)

    sdn_factor: float = field(init=False)
    phase_factor: float = field(init=False)
    euler_ok: bool = field(init=False)

    def __post_init__(self) -> None:
        self.sdn_factor = sdn_shape_factor(self.solid)
        self.phase_factor = sdn_phase_factor(self.solid)
        self.euler_ok = euler_verify(self.solid)

    def sdkp_tau(self, kinetics: float) -> float:
        """tau = S * D / K  [s]."""
        if kinetics == 0:
            raise ValueError("Kinetics K cannot be zero (division by zero in tau = S*D/K)")
        return (self.size * self.density) / kinetics

    def sdvr_field(self) -> float:
        """Phi = S * D * V * R."""
        return self.size * self.density * self.velocity * self.rotation

    def eos_velocity_range(self) -> tuple[float, float]:
        v_low = self.velocity * (1.0 + EOS_DEV_LOW)
        v_high = self.velocity * (1.0 + EOS_DEV_HIGH)
        return (v_low, v_high)

    def state_vector(self) -> dict:
        return {
            "S": self.size,
            "D": self.density,
            "V": self.velocity,
            "R": self.rotation,
            "solid": self.solid,
            "phi_SDN": self.sdn_factor,
            "phase": self.phase_factor,
            "Phi_SDVR": self.sdvr_field(),
        }

    def __repr__(self) -> str:
        return (
            f"BodySDVR(id={self.body_id!r}, "
            f"S={self.size:.3e} m, D={self.density:.3e} kg/m^3, "
            f"V={self.velocity:.3e} m/s, R={self.rotation:.3e} rad/s, "
            f"solid={self.solid})"
        )


class KapnackEngine:
    """Kapnack discrete gradient processor (upstream KapnackEngine)."""

    def __init__(
        self,
        eos_reference: float = EOS,
        harmonic_order: int = 9,
        amiyah_baseline: float = 1.0,
        epsilon: float = 1e-15,
    ) -> None:
        if harmonic_order not in SDN_VORTEX:
            raise ValueError(
                f"harmonic_order must be in {list(SDN_VORTEX.keys())}. "
                f"Got: {harmonic_order}"
            )
        self.eos = eos_reference
        self.harmonic_order = harmonic_order
        self.amiyah_baseline = amiyah_baseline
        self.epsilon = epsilon

    def packing_density_gradient(self, body_a: BodySDVR, body_b: BodySDVR) -> float:
        """
        Gamma_ij = D_mean / (|delta_S| * phi_i * phi_j * (1 + H_n))
        Units: kg/m^4
        """
        delta_s = abs(body_a.size - body_b.size)
        mean_d = (body_a.density + body_b.density) / 2.0
        phi_prod = body_a.sdn_factor * body_b.sdn_factor
        n = self.harmonic_order // 3
        harmonic_correction = 1.0 / (9.0 * (10.0 ** n))
        effective_delta = max(delta_s, self.epsilon)
        return mean_d / (effective_delta * max(phi_prod, self.epsilon) * (1.0 + harmonic_correction))

    def kinetic_coupling(self, body_a: BodySDVR, body_b: BodySDVR) -> float:
        """
        kappa_ij ~ |R_a - R_b| / max(|V_a - V_b|, eps) scaled by size geometric mean.
        Upstream uses rotational/velocity contrast; keep a stable positive coupling term.
        """
        s_eff = math.sqrt(max(body_a.size * body_b.size, self.epsilon))
        dv = abs(body_a.velocity - body_b.velocity)
        dr = abs(body_a.rotation - body_b.rotation)
        return (dr * s_eff) / max(dv, self.epsilon)

    def system_coherence(self, bodies: list[BodySDVR]) -> dict[str, Any]:
        """
        Aggregate pairwise interaction and map to a coherence score in (0, 1].
        Returns a dict compatible with the upstream MCP server text formatter.
        """
        if len(bodies) < 2:
            return {
                "coherence": 1.0,
                "harmonic_order": self.harmonic_order,
                "harmonic_description": SDN_VORTEX[self.harmonic_order],
                "psi_total": 0.0,
                "coherence_range_low": 1.0 - EOS_DEV_HIGH,
                "coherence_range_high": 1.0 - EOS_DEV_LOW,
                "pair_diagnostics": {},
            }

        gammas: list[float] = []
        kappas: list[float] = []
        pair_diagnostics: dict[str, Any] = {}
        for a, b in itertools.combinations(bodies, 2):
            g = self.packing_density_gradient(a, b)
            k = self.kinetic_coupling(a, b)
            gammas.append(g)
            kappas.append(k)
            key = f"{a.body_id}|{b.body_id}"
            pair_diagnostics[key] = {"gamma": g, "kappa": k}

        psi_total = float(sum(gammas))
        # Bounded coherence: larger interaction sum -> lower coherence
        coherence = 1.0 / (1.0 + math.log1p(max(psi_total, 0.0)))
        return {
            "coherence": coherence,
            "harmonic_order": self.harmonic_order,
            "harmonic_description": SDN_VORTEX[self.harmonic_order],
            "psi_total": psi_total,
            "coherence_range_low": 1.0 - EOS_DEV_HIGH,
            "coherence_range_high": 1.0 - EOS_DEV_LOW,
            "pair_diagnostics": pair_diagnostics,
            "mean_kappa": float(sum(kappas) / max(len(kappas), 1)),
        }
