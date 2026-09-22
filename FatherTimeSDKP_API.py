# Import core modules
from fathertimesdkp.orbit import OrbitalSolver
from fathertimesdkp.quantum import QuantumEngine
from fathertimesdkp.utils import SimulationLogger

# Initialize logger
logger = SimulationLogger(log_file="simulation.log")

# Orbital computation
solver = OrbitalSolver()
trajectory = solver.compute_orbit(
    altitude_km=420,
    inclination_deg=51.6,
    duration_hours=6
)
logger.info(f"Predicted trajectory: {trajectory}")

# Quantum computation
qe = QuantumEngine(qubits=1024)
ghz_result = qe.run_ghz_perfection(iterations=10)
logger.info(f"GHZ perfection result: {ghz_result}")

print("Simulation complete. See simulation.log for details.")
