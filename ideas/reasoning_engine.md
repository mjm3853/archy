# Project: "Reasoning Engine" (Conversational Causal AI)

## Core Concept

A conversational AI that doesn't just predict text, but understands the Mediation Formula. It allows users to query "Why" and "What if" through structural causal models.

## Key Features to Build

- **Mechanism Analysis**: Use the Mediation Formula to separate Natural Direct Effects (NDE) from Natural Indirect Effects (NIE).

- **Fairness Auditor**: Detect direct discrimination by "freezing" mediators (like department choice) to isolate protected traits (like gender).

- **Counterfactual Engine**: Handle $M=M_0$ queries—simulating outcomes where the mediator is held at its natural baseline while the treatment is intervened upon.

## Development Goal

Bridge the gap between "seeing" (standard LLMs) and "doing/imaging" (Causal AI) using Pearl's formal mediation algebra.

- **Deep Self-Awareness Module**: A software package integrating a causal model of the world, a causal model of itself, and a dynamic memory. This allows the AI to explain its own internal reasoning paths and learn from past counterfactual experiences.

- **Semantic Translator**: A specialized layer designed to translate informal user queries (natural language "why" and "what if" questions) into formal causal notation and $do$-calculus operations.
