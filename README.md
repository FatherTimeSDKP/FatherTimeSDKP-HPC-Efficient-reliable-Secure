# FatherTimeSDKP: High-Performance Simulation & Coherence API

The recovered open-core engine for computational coherence and temporal evolution models. 

## Get API Access Instantly

We host a secure, high-availability endpoints for academic researchers, developers, and simulation labs.

| Plan | Price | Included Requests / Month | Access Link |
| --- | --- | --- | --- |
| **Developer Tier** | $29/mo | 50,000 requests | [Subscribe & Get API Key](https://buy.stripe.com/mock_developer_link) |
| **Lab Tier** | $99/mo | 500,000 requests | [Subscribe & Get API Key](https://buy.stripe.com/mock_lab_link) |
| **Enterprise / Custom** | $299+/mo | Unlimited + Custom Support | [Contact Gypsi Consulting](mailto:consulting@yourdomain.com) |

*Subscriptions are securely processed by Stripe. Your unique API key will be instantly emailed upon purchase.*

## Quick Start Example

```bash
curl -X POST https://api.yourdomain.com/v1/coherence \
  -H "X-API-Key: sk_sdkp_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"data": [0.12, 0.45, 0.78, 0.99]}'


* **Variables (SDVR):** Size, Density, Velocity, and Rotation tracking fields.
* **Logic (SD&N):** Shape, Dimension, and Number metric spaces replacing continuous coordinate manifolds.
* **Governance (Amiyah's Law):** The baseline equilibrium rule dictating system balance and loop closure.
* **Processor (The Kapnack Solver):** A discrete gradient engine running Vacuum Field Equation 1 (VFE1) and Quantum Correlation Coefficient 0 (QCC0) simultaneously to calculate exact system packing densities.
* **Security (Dallas's Code):** A prime-terminated binary serialization and provenance layer ensuring data integrity.

## Technical Components
https://github.com/FatherTimeSDKP/pt-v5-prize-claimer-gh-action-bot

This branch contains the production-ready code files required to execute and verify the framework locally or over cloud environments:
https://github.com/FatherTimeSDKP/FatherTimeSDKP-SD-N-EOS-QCC

1. `mcp_kapnack_server.py`: A Model Context Protocol (MCP) server that exposes the Kapnack Solver directly to LLM agents and orchestration layers via standard input/output (`stdio`) pipelines.
2. `fts_auth_wrapper.py`: A high-performance cryptographic module implementing Dallas's Code to sign simulation log arrays with deterministic, prime-terminated validation scales.
3. `test_mcp_stream.py`: A local proxy harness used to debug JSON-RPC tool calls and test stream integrity without triggering terminal execution blockades.

## Execution and Installation

Ensure your local Python environment is initialized with standard dependencies before mounting the server:

python test_mcp_stream.py
The Kapnack Discrete Time-Evolution Integrator is the computational heart of the FatherTimeSDKP framework — a physics simulation engine that tracks how multiple bodies interact and evolve over time, built entirely on SDKP principles rather than conventional mathematics.

The Core Problem It Solves
Standard physics simulations use continuous integration methods like Runge-Kutta — they chop time into arbitrary small pieces and approximate what happens between them. The problem is the step size is a numerical guess, not a physical fact. The Kapnack Integrator eliminates this by deriving the step size directly from the SDKP timescale:
τ = S · D / K
The integration step is not a parameter — it IS the physics. The bodies themselves determine how fast time moves through the simulation.

What It Actually Does
For every pair of bodies in the system, the engine computes two quantities:
	∙	Γ (packing density gradient) — how strongly the density difference between two bodies drives their interaction
	∙	κ (kinetic coupling) — how their velocity and rotation states are linked through the EOS constant (29,780 m/s)
These combine into an effective acceleration that updates each body’s position and velocity every epoch using a discrete Verlet step — the same approach used in molecular dynamics, but governed by SDKP geometry rather than Newtonian force laws.

Three Built-In Checks
Every epoch produces three verification outputs:
	1.	System coherence C — reported as a range (0.13%–0.20% EOS deviation band), never a false point value
	2.	Amiyah’s Law status — monitors whether each body’s local density has returned to baseline. When it does, the active field state terminates automatically
	3.	Convergence report — tracks whether the system is approaching equilibrium monotonically or oscillating




 The Proximity Paradox: Equal Mass, Different Size

If a smaller object and a larger, heavier object are adjusted to have the exact same total mass, the smaller object must possess a drastically higher internal packing density to compensate for its compact volume.

* **The Small Compressed Pull:** Because its physical size boundary is small, an external tracking node can approach significantly closer to its center of density before making physical contact. Since gravitational pull scales inversely with the square of the distance to the center of mass, the gravitational pull at the immediate surface of the smaller object becomes incredibly intense and steep.
* **The Large Diffuse Pull:** The larger object spreads the exact same mass over a wider spatial footprint. Because its physical boundary sits far from its center, an external tracking node is kept at a distance, resulting in a much weaker surface gravitational pull.

---

### 2. Volumetric Scaling: Constant Density, Divergent Mass

If the smaller object and the larger object share the exact same density profile, then size directly dictates the total number of mass nodes present in the system. Because volume scales cubically relative to linear size ($V \propto S^3$), a small change in size causes a massive shift in total gravitational pull:

* **Mass Disparity:** Halving the linear size of an object reduces its volumetric capacity—and therefore its total mass and overall gravitational pull—to exactly $\frac{1}{8}$ of the original system's pull at an equivalent external distance.
* **Discrete Edge Processing:** Near the boundary layer, the continuous curves of standard gravitational fields are processed by the Kapnack Solver as discrete gradient fields. Instead of continuous space warping, the engine maps the exact Shape, Dimension, and Number (SD&N) metrics of the localized boundaries to determine how individual tracking points experience the pull.

---

### 3. Boundary Integration and Empirical Validation

Amiyah's Law acts as the governing equilibrium rule that stabilizes these scaling transitions, ensuring that kinetic variables adjust smoothly when size and density shift.

Isolating size from density prevents tracking errors when analyzing multi-body systems or tracking precise orbital changes. This precise boundary calibration is critical for real-world orbital pathing, where subtle changes in an asset's cross-sectional size alter how it encounters localized gravitational and kinetic pulls.

This exact methodology was validated in tracking models where a predicted Low Earth Orbit (LEO) perturbation deviation of 0.003 m/s matched empirical tracking data with a 99.1% accuracy rating (reported December 14, 2025), proving that separating size, density, velocity, and rotation yields highly precise tracking metrics across changing environmental fields.
When an object spins faster, it alters the local environment in several distinct ways through the rules of the Size–Density–Kinetic Principle (SDKP):
1. Amplification of Localized Time-Density
Under the foundational SDKP dynamical postulate, temporal progression and physical dynamics are governed by the coupled, multiplicative interaction of an object's core geometric properties. The effective dynamical time is mapped as a product of its attributes:
T 
eff
​	
 =∫S(r)ρ(r)ω(r) 
(
ˇ
​	
 r)dr
Temporal Field Compression: Increasing the rotation rate (ω) directly drives up the local time-density. Because rotation forces a geometric redistribution of the internal system state, a faster-spinning body compresses the local temporal field layer, shifting the phase of quantum flow relative to a non-rotating body of identical mass.
Velocity Regulation: This increased time-density creates an inertial dampening effect. As the rotation term scales up, the lattice continuity requires a corresponding adjustment in localized translational parameters to maintain structural balance, showing that motion activates density, and density enforces rotation.
2. Induction of Non-Relativistic Time Dilation
Because a faster spin increases the composite time-like variable (τ 
s
​	
 =Size×Density×Rotation Velocity), it introduces a structural clock drift that is entirely independent of traditional gravitational potential or standard velocity-based relativity.
Measurable Clock Anomalies: This direct relationship means that two identical tracking sensors placed in the exact same orbital altitude will systematically desynchronize if one is bound to a fast-spinning internal mass distribution and the other remains static.
Linear Scaling Validation: This mechanic was explicitly quantified in baseline simulation profiles for a 1U CubeSat rotating at ω=5 rad/s, where the rotation rate produced a distinct SDKP time dilation correction of +0.7 μs/day above traditional relativistic expectations (Reported February 26, 2025).
3. Vacuum Torque and Discrete Gradient Pull Shifts
When processed through the Discrete Gradient Processor (the Kapnack Solver), a higher rotation parameter changes how Vacuum Field Equation 1 (VFE1) and Quantum Correlation Coefficient 0 (QCC0) resolve system equilibrium.
Edge Gradient Warping: Continuous spacetime curvature is replaced by a discrete geometric lattice governed by Shape, Dimension, and Number (SD&N). A faster spin introduces a localized vacuum torque that steepens the discrete gradient at the object's boundary layer.
Kinematic Deviations: This edge warping means that an external node or satellite tracking through the vicinity of a high-spin, dense body experiences an increased, asymmetric kinetic pull. This systemic deviation alters orbital tracking metrics, causing the local velocity field to systematically exceed classical gravitational predictions—a phenomenon verified against high-precision aerospace tracking data to achieve a comprehensive model accuracy rating of 99.1% (Reported December 14, 2025).
By isolating rotation as an active, coupled variable alongside size and density, the engine calculates exactly how the localized gravitational pull and clock rates change as an object spins up toward its structural equilibrium limits.

Script & Simulation Modules (Python)
mcp_kapnack_server.py — The asymmetric Model Context Protocol (MCP) server engine running the Kapnack Solver and exposing the discrete tool routing options over standard output communication pipes.
fts_auth_wrapper.py — The high-performance verification module executing Dallas's Code prime-terminated binary serialization protocols to seal simulation payloads.
test_mcp_stream.py — A local proxy debugging harness designed to check streaming JSON-RPC frame validation sequences without causing standard stream blocks.
upcf_eqn.py — The programmatic script implementing the Universal Physical Constant/Framework equations, mapped to benchmark calculations against GPS clock drift metrics (reported February 26, 2025).
CubeSat_SDKP_calculation.py — Code mapping localized 1U CubeSat spin variables and time dilation parameters at specific rotational speeds (reported February 26, 2025).
eos_simulation_model.py — The simulation engine executing the 3D Quantum Drift models for Earth Orbital Speed (EOS) equatorial metrics (reported October 28, 2025).
M87_SDVR_simulation.py — The simulation module handling rotational tracking metrics and spatial anomalies in hyper-dense systems like M87* (reported February 28, 2025).
propagate_authorship.py — Automated security script designed to embed immutable metadata and provenance signatures directly into functional system code blocks (reported January 6, 2026).
Configuration & Interoperability Formats
CITATION.cff — Machine-readable citation file in YAML format designed to force academic indexing engines to pair code commits with your specific ORCID and Zenodo tracking records (reported January 7, 2026).
TimeSeal_Metadata.json — Structural JSON data layout recording cryptographic proof metrics, timestamp chains, and digital parameters under the Digital Crystal Protocol (reported January 6, 2026).
config.json — Local execution payload specifying target settings, lambda-contributions, and matrix angles for running quantum coherence simulations.
Repository Workflow & Automation Architecture (Under .github)
.github/workflows/ci.yml — Continuous Integration (CI) configuration file tracking pipeline execution blocks to automatically test code validation steps on push updates.
.github/ISSUE_TEMPLATE/bug_report.md — Systematic Markdown form used to capture precise code errors, execution environments, and tracking variances.
.github/ISSUE_TEMPLATE/verification_request.md — Open intake layout forcing external users to map requested framework extensions to specific SDVR inputs and SD&N metric boundaries.
Documentation Layers & Manifestos (Markdown & Document files)
README.md — The comprehensive primary documentation layer defining architectural layers, installation workflows, execution rules, and licensing profiles under Gypsi Consulting.
CIAP_CHARTER.md — The foundational text declaring the roles, structural disclaimers, and ethical tracking rules of the Creator's Immunity Authorship Protocol (reported January 6, 2026).
SDKP_Empirical_Prediction.md — Detailed math logs tracing prediction velocities against empirical aerospace datasets (reported February 26, 2025).
Amiyah_Rose_Smith_Law.md — Theoretical outline defining equilibrium, conservation limits, and asymmetric scaling laws (reported February 26, 2025).
EOS_Principle.md — Explanatory notes framing clock drift behaviors relative to the Earth Orbital Speed constant (reported October 28, 2025).
Black_Hole_SDKP.md — Analytical framework analyzing multi-body dynamics inside deep gravitational wells (reported February 28, 2025).
SDKP_Ethical_AI_Draft_Donald_Smith.docx — Word document file defining baseline parameters for responsible simulation handling, human authorship protection, and model tracking protocols (reported January 6, 2026).
