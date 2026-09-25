"""FatherTimeSDKP Kapnack discrete time-evolution integrator (syntax-recovered).

Recovered for importability from upstream GitHub content:
  FatherTimeSDKP/FatherTimeSDKP-HPC-Efficient-reliable-Secure/Kapnack_solver.py

Upstream author: Donald Paul Smith (Father Time)
ORCID: 0009-0003-7925-1653

Companion module: sdkp_sdvr_engine
"""

from __future__ import annotations

import csv
import io
import itertools
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sdkp_sdvr_engine import (
    BodySDVR,
    KapnackEngine,
    EOS,
    EOS_DEV_LOW,
    EOS_DEV_HIGH,
)


@dataclass(frozen=True)
class PhysicsState:
    """Immutable snapshot of one SDVR body at one epoch."""

    body_id: str
    epoch: int
    time: float
    pos: Tuple[float, float, float]
    vel: float
    rotation: float
    density: float
    size: float
    solid: str
    sdvr_phi: float
    tau_sdkp: Optional[float] = None


@dataclass
class EpochResult:
    """Full system diagnostic for a single integration epoch."""

    epoch: int
    elapsed_time: float
    dt_used: float
    coherence: float
    coherence_lo: float
    coherence_hi: float
    psi_total: float
    amiyah_active: bool
    body_states: List[PhysicsState]
    pair_diagnostics: Dict
    warnings: List[str]

    def summary_line(self) -> str:
        status = "ACTIVE" if self.amiyah_active else "EQUILIBRIUM"
        return (
            f"Epoch {self.epoch:>4d} | "
            f"t={self.elapsed_time:>12.4f}s | "
            f"dt={self.dt_used:.4e}s | "
            f"C={self.coherence:.8f} "
            f"[{self.coherence_lo:.8f}-{self.coherence_hi:.8f}] | "
            f"{status}"
        )


class KapnackIntegrator:
    """
    Discrete time-evolution integrator.

    Step size can be adaptive from SDKP timescales, or fixed via dt_scale * tau_min.
    Acceleration uses EOS^2 scaling of density gradient / density (upstream note).
    """

    def __init__(
        self,
        engine: KapnackEngine,
        amiyah_baseline: float = 1.0,
        adaptive_dt: bool = True,
        dt_scale: float = 0.01,
        max_velocity: float = EOS * 10,
        verbose: bool = True,
    ) -> None:
        self.engine = engine
        self.amiyah_baseline = amiyah_baseline
        self.adaptive_dt = adaptive_dt
        self.dt_scale = dt_scale
        self.max_velocity = max_velocity
        self.verbose = verbose
        self.history: List[EpochResult] = []

    def _compute_adaptive_dt(
        self, bodies: List[BodySDVR], fallback_dt: float = 1.0
    ) -> float:
        tau_min = float("inf")
        for a, b in itertools.combinations(bodies, 2):
            s_eff = math.sqrt(max(a.size * b.size, 1e-30))
            dv = abs(a.velocity - b.velocity)
            if dv > 0:
                tau = s_eff / dv
                if tau < tau_min:
                    tau_min = tau
        if math.isinf(tau_min):
            return fallback_dt
        return max(self.dt_scale * tau_min, 1e-12)

    def _compute_acceleration(self, gamma: float, kappa: float, density: float) -> float:
        if density <= 0:
            return 0.0
        eos_mid = EOS * (1.0 + (EOS_DEV_LOW + EOS_DEV_HIGH) / 2.0)
        return (gamma * (1.0 + kappa) / density) * (eos_mid ** 2)

    @staticmethod
    def _unit_vector(
        pos_a: Tuple[float, float, float],
        pos_b: Tuple[float, float, float],
        epsilon: float = 1e-15,
    ) -> Tuple[float, float, float]:
        dx = pos_b[0] - pos_a[0]
        dy = pos_b[1] - pos_a[1]
        dz = pos_b[2] - pos_a[2]
        r = math.sqrt(dx * dx + dy * dy + dz * dz)
        if r < epsilon:
            return (0.0, 0.0, 0.0)
        return (dx / r, dy / r, dz / r)

    def _snap(
        self, body: BodySDVR, epoch: int, elapsed: float, tau: Optional[float]
    ) -> PhysicsState:
        return PhysicsState(
            body_id=body.body_id,
            epoch=epoch,
            time=elapsed,
            pos=tuple(body.position),  # type: ignore[arg-type]
            vel=body.velocity,
            rotation=body.rotation,
            density=body.density,
            size=body.size,
            solid=body.solid,
            sdvr_phi=body.sdvr_field(),
            tau_sdkp=tau,
        )

    def execute_epoch_step(
        self,
        bodies: List[BodySDVR],
        epoch: int,
        elapsed: float,
        dt: Optional[float] = None,
    ) -> EpochResult:
        warnings: List[str] = []
        n = len(bodies)
        report = self.engine.system_coherence(bodies)

        if n < 2:
            snaps = [self._snap(b, epoch, elapsed, None) for b in bodies]
            return EpochResult(
                epoch=epoch,
                elapsed_time=elapsed,
                dt_used=dt or 0.0,
                coherence=float(report["coherence"]),
                coherence_lo=float(report["coherence_range_low"]),
                coherence_hi=float(report["coherence_range_high"]),
                psi_total=float(report["psi_total"]),
                amiyah_active=False,
                body_states=snaps,
                pair_diagnostics=report.get("pair_diagnostics", {}),
                warnings=warnings,
            )

        if dt is None:
            dt = self._compute_adaptive_dt(bodies) if self.adaptive_dt else 1.0

        # Net acceleration per body from pairwise gradients
        acc = {b.body_id: [0.0, 0.0, 0.0] for b in bodies}
        for a, b in itertools.combinations(bodies, 2):
            gamma = self.engine.packing_density_gradient(a, b)
            kappa = self.engine.kinetic_coupling(a, b)
            a_mag = self._compute_acceleration(gamma, kappa, 0.5 * (a.density + b.density))
            ux, uy, uz = self._unit_vector(a.position, b.position)
            # equal-and-opposite style push along connecting line
            acc[a.body_id][0] += a_mag * ux
            acc[a.body_id][1] += a_mag * uy
            acc[a.body_id][2] += a_mag * uz
            acc[b.body_id][0] -= a_mag * ux
            acc[b.body_id][1] -= a_mag * uy
            acc[b.body_id][2] -= a_mag * uz

        # Discrete update: position and speed
        for body in bodies:
            ax, ay, az = acc[body.body_id]
            a_net = math.sqrt(ax * ax + ay * ay + az * az)
            x, y, z = body.position
            # direction of motion: along velocity if present else along accel
            if body.velocity > 0 and a_net > 0:
                # advance along current +x-weighted path using speed scalar
                speed = min(body.velocity + a_net * dt, self.max_velocity)
                # unit direction from acceleration if nonzero else +x
                if a_net > 1e-30:
                    dx, dy, dz = ax / a_net, ay / a_net, az / a_net
                else:
                    dx, dy, dz = 1.0, 0.0, 0.0
                body.position = (
                    x + speed * dt * dx + 0.5 * ax * dt * dt,
                    y + speed * dt * dy + 0.5 * ay * dt * dt,
                    z + speed * dt * dz + 0.5 * az * dt * dt,
                )
                body.velocity = speed
            else:
                body.position = (
                    x + body.velocity * dt + 0.5 * ax * dt * dt,
                    y + 0.5 * ay * dt * dt,
                    z + 0.5 * az * dt * dt,
                )
                body.velocity = min(body.velocity + a_net * dt, self.max_velocity)

        report_after = self.engine.system_coherence(bodies)
        snaps = [self._snap(b, epoch, elapsed + dt, None) for b in bodies]
        amiyah_active = any(abs(b.density - self.amiyah_baseline) > 1e-6 for b in bodies)

        result = EpochResult(
            epoch=epoch,
            elapsed_time=elapsed + dt,
            dt_used=dt,
            coherence=float(report_after["coherence"]),
            coherence_lo=float(report_after["coherence_range_low"]),
            coherence_hi=float(report_after["coherence_range_high"]),
            psi_total=float(report_after["psi_total"]),
            amiyah_active=amiyah_active,
            body_states=snaps,
            pair_diagnostics=report_after.get("pair_diagnostics", {}),
            warnings=warnings,
        )
        if self.verbose:
            print(result.summary_line())
        return result

    def run_simulation(
        self,
        bodies: List[BodySDVR],
        total_time: float = 1.0,
        steps: int = 10,
    ) -> List[dict]:
        """
        Run N discrete epochs over total_time.

        Returns a list of dicts (API-friendly) derived from EpochResult history.
        """
        steps = max(int(steps), 1)
        # working copies so caller inputs are not mutated unexpectedly
        state = [
            BodySDVR(
                body_id=b.body_id,
                size=b.size,
                density=b.density,
                velocity=b.velocity,
                rotation=b.rotation,
                solid=b.solid,
                position=tuple(b.position),
            )
            for b in bodies
        ]
        self.history = []
        elapsed = 0.0
        fixed_dt = total_time / steps
        for epoch in range(steps):
            er = self.execute_epoch_step(state, epoch, elapsed, dt=fixed_dt)
            self.history.append(er)
            elapsed = er.elapsed_time

        # API-facing structure (matches earlier MCP client expectations loosely)
        return [
            {
                "epoch": er.epoch,
                "elapsed_time_seconds": er.elapsed_time,
                "system_coherence": er.coherence,
                "psi_total": er.psi_total,
                "dt_used": er.dt_used,
                "amiyah_active": er.amiyah_active,
                "states": [
                    {
                        "id": s.body_id,
                        "pos": list(s.pos),
                        "v": s.vel,
                        "rotation": s.rotation,
                        "density": s.density,
                    }
                    for s in er.body_states
                ],
            }
            for er in self.history
        ]

    def convergence_report(self) -> Dict:
        if not self.history:
            return {"epochs": 0}
        return {
            "epochs": len(self.history),
            "final_coherence": self.history[-1].coherence,
            "final_psi": self.history[-1].psi_total,
            "amiyah_active": self.history[-1].amiyah_active,
        }

    def export_csv(self, filepath: Optional[str] = None) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            ["epoch", "elapsed_s", "coherence", "psi_total", "body_id", "x", "y", "z", "v"]
        )
        for er in self.history:
            for s in er.body_states:
                writer.writerow(
                    [
                        er.epoch,
                        er.elapsed_time,
                        er.coherence,
                        er.psi_total,
                        s.body_id,
                        s.pos[0],
                        s.pos[1],
                        s.pos[2],
                        s.vel,
                    ]
                )
        data = buf.getvalue()
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(data)
        return data
