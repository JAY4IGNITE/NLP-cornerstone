# Limitations

## Synthetic Benchmark Limitations
`CampusFAQ-50K` is a synthetic dataset. It lacks the natural noise, typos, and conversational ambiguity present in real student interactions.

## Institution-Specific Knowledge Dependence
The pipeline is heavily dependent on the institutional documents loaded into the knowledge base. If a rule is unstated in the provided documents, the system must abstain rather than hallucinate.

## Unsupported Queries
The system is constrained strictly to academic and administrative intents. General domain queries will be safely abstained.
