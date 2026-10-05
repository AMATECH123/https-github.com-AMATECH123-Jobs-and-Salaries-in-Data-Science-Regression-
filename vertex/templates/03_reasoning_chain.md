# Reasoning chain

<!-- Numbered from first look-up to final answer. One node, one fact or one operation. Every retrieval carries source, value, units, period, and citation (direct source, accession number or identifier). Every compute shows the operation and full-precision result. Mark layer and whether the step is a chained hop. -->

| Step | Layer | Kind | Keyed by | Look-up / operation | Source and citation | Value (units, period) |
| --- | --- | --- | --- | --- | --- | --- |
| N1 | 1 | retrieval | opening (not a hop) | | | |
| N2 | 2 | retrieval | N1 (hop 1) | | | |
| N3 | 3 | retrieval | N2 (hop 2) | | | |
| N4 | 4 | retrieval | N3 (hop 3) | | | |
| N5 | 5 | compute | N_, N_ | | n/a | |
| N6 | 6 | compute (answer Q_) | N_ | | n/a | |

## Counts
- Longest chain layers:
- Chained retrieval hops on longest chain:
- Final answers: Q1 = N_, Q2 = N_, Q3 = N_
