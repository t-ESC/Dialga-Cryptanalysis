Kerckhoffs’ principle motivates the design and evaluation of cryptographic systems under
the assumption that the algorithms and implementation details are public, with security
relying only on a secret key. This thesis studies the tweakable block cipher (TBC) fam-
ily Dialga [Ban+25], introduced in December 2025 by Banik et al. and comprising four
variants that differ only in tweak size (128 or 256 bits) and in the number of rounds, with
the full-round versions claimed to provide 128-bit security and the round-reduced variants
claimed to provide 80-bit security.
This thesis presents the first third-party cryptanalysis to the best of the author’s knowledge
of the Dialga family. The work focuses on differential cryptanalysis. A search for multi-
round differential characteristics was modeled as a boolean satisfiability (SAT) problem.
The probabilities of the resulting characteristic were bounded by encoding the probabilities
as cardinality constraints into the SAT problem as proposed by [Sin05]. To solve the
SAT problems, the SAT solver CryptoMiniSAT [SNC09] was used. Characteristics with
matching boundary conditions were combined to build characteristics for lengths that were
infeasible to solve directly.
For six-round differential characteristics, characteristics were found with higher proba-
bilities than the lower bounds reported by the original specification [Ban+25]. For the
remaining configurations, the characteristics found here yield equal or worse probabili-
ties than Banik et al.’s results. Especially for the full-round versions of Dialga only nine
round differential characteristics were found compared to the ten round characteristics
documented by Banik et al. Overall, the results confirm the security margin claimed for
Dialga.

[Ban+25] Banik, Subhadeep, et al. "Dialga: A Family of Low-Latency Tweakable Block Ciphers 
using Multiple Linear Layers (Full Version)." Cryptology ePrint Archive (2026).
