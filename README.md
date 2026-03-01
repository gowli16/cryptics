BB84 QKD Simulator
Security Analysis of Quantum Key Distribution Under Noise & Attack

Problem
Classical cryptographic systems (RSA, ECC) rely on computational hardness assumptions.
Future large-scale quantum computers running Shor’s algorithm threaten these systems.

The weak point in secure communication is key exchange.
We ask:
How secure is the BB84 Quantum Key Distribution protocol under realistic noise and active eavesdropping?
And more importantly:
At what Quantum Bit Error Rate (QBER) does secure key generation become infeasible?

Our Solution
We built a BB84 Quantum Key Distribution Simulator using Qiskit that:
-Implements full BB84 key exchange
-Simulates intercept–resend eavesdropping
-Models depolarizing quantum channel noise
-Measures QBER under different conditions
-Identifies the security threshold (~11%)

Instead of just demonstrating BB84, we evaluate its operational security boundaries.

Why Quantum?

Unlike classical cryptography:
Security is not based on computational difficulty
Security is guaranteed by quantum mechanics
In BB84:
Measuring a qubit disturbs its state
Diturbance increases QBER
High QBER → key discarded
Security emerges from physics.

Key Features

- Security analysis under adversarial attack
- Noise vs QBER mapping
- Security threshold visualization
- Key rate efficiency analysis
- Practical feasibility discussion

Tech Stack

-Python
-Qiskit
-Qiskit Aer
-NumPy
-Matplotlib
