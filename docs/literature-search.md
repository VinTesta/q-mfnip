# Systematic search for prior work

Date: 2026-11-06. Purpose: find prior work that applies quantum algorithms to network interdiction (Section III-E of the paper). A work was considered relevant if it combines a quantum algorithm with the removal of network elements. For the arXiv API, all results were examined; for the other sources, the first 15 to 20 results by relevance.

| Source | Exact query | Results | Relevant |
|---|---|---|---|
| arXiv API | `all:quantum AND all:interdiction` | 3 | arXiv:2602.22943 (variational minimum cut; cites interdiction only as motivation) |
| arXiv API | `abs:"network interdiction" AND abs:quantum` | 1 | the same arXiv:2602.22943 |
| arXiv API | `abs:interdiction AND abs:Grover` | 0 | none |
| arXiv API | `abs:interdiction AND abs:annealing` | 1 | none (classical simulated annealing) |
| arXiv API | `abs:interdiction AND abs:QAOA` | 0 | none |
| arXiv API | `abs:"maximum flow" AND abs:interdiction AND abs:quantum` | 0 | none |
| arXiv API | `abs:"bilevel" AND abs:quantum AND abs:interdiction` | 0 | none |
| arXiv API | `abs:"most vital" AND abs:quantum` | 6 | none |
| arXiv API | `abs:"edge removal" AND abs:Grover` | 1 | **arXiv:2604.26692** (Sutcliffe and Mutyamsetty) |
| arXiv API | `abs:"minimum finding" AND abs:edges AND abs:remov*` | 1 | the same arXiv:2604.26692 |
| arXiv API | `abs:quantum AND abs:"vital edges"` | 0 | none |
| arXiv API | `abs:quantum AND abs:"bilevel"` | 10 | none |
| arXiv API | `abs:"Stackelberg" AND abs:quantum AND abs:network` | 0 | none |
| arXiv API | `abs:"Durr" AND abs:"Hoyer" AND abs:graph` | 1 | none |
| Semantic Scholar Graph API | `quantum algorithm maximum flow interdiction` | 191 (20 examined) | none on quantum interdiction |
| Semantic Scholar Graph API | `quantum annealing network interdiction` | 1,024 (20 examined) | **Peddireddy et al. (2026)** |
| Semantic Scholar Graph API | `quantum network interdiction`, `Grover interdiction`, `quantum bilevel optimization interdiction`, `QAOA network interdiction` | HTTP 429 (rate limit), also on retries | not executed |
| Crossref API | `quantum network interdiction`; `quantum interdiction Grover`; `quantum annealing interdiction`; `quantum maximum flow interdiction` (15 examined each) | not recorded | Peddireddy et al. (2026) |
| Web search | `quantum network interdiction` | ~25 | no papers (one code repository on vehicle routing with interdiction on an annealer) |
| Web search | `Grover algorithm network interdiction problem` | ~10 | Sutcliffe and Mutyamsetty (2026) |
| Web search | `quantum annealing OR QAOA "network interdiction"` | ~10 | Peddireddy et al. (2026); arXiv:2602.22943 |
| Web search | `quantum algorithm "maximum flow" interdiction` | ~10 | none (only arXiv:2602.22943) |
| Web search | `quantum bilevel optimization interdiction Grover OR "quantum annealing" OR "quantum computing"` | ~10 | Peddireddy et al. (2026) |

## Relevant works found

1. Peddireddy, Comert, Chowdhury and Aggarwal, "Arc Interdiction Vehicle Routing Problem Using Quantum Annealing", in *Quantum Computing and Artificial Intelligence* (CCIS), Springer, 2026, pp. 82–91, DOI 10.1007/978-3-032-15931-1_7. They formulate a bilevel arc-interdiction vehicle routing problem as a QUBO and solve it on D-Wave annealers.
2. Sutcliffe and Mutyamsetty, "Towards Quantum Optimised Malware Containment", arXiv:2604.26692, 29 April 2026. They combine Grover minimum finding with amplitude estimation to choose which edges to remove to contain malware. The objective is the expected influence in a cascade model, not a maximum flow.
3. Abbassi et al., arXiv:2602.22943 (February 2026). Minimum cut with variational algorithms; interdiction is cited only as motivation.

## Limitations of the search

Only titles and abstracts were searched. Only 2 of the 6 Semantic Scholar queries ran because of rate limiting. Scopus, Web of Science and Google Scholar were not queried.
