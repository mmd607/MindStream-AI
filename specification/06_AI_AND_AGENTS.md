# AI Planning and Agent Design

## MVP Approach
Use a controlled orchestrator rather than a complicated autonomous-agent framework.

```text
Input
 ↓
Requirements Analyzer
 ↓
Architecture Planner
 ↓
Database Planner
 ↓
Task Planner
 ↓
Consistency Validator
 ↓
Documentation Generator
```

## Requirements Analyzer
Produces objective, actors, functional/non-functional requirements, assumptions, constraints, risks, and open questions.

## Architecture Planner
Produces architecture style, components, responsibilities, communication, technologies, rationale, and deployment concept. Prefer simple architectures when sufficient.

## Database Planner
Produces entities, attributes, relationships, indexes, and constraints.

## Task Planner
Produces epics, tasks, subtasks, dependencies, roles, estimates, priorities, and acceptance criteria.

## Consistency Validator
Checks requirement-to-task coverage, entity usage, valid roles, required fields, and dependency cycles.

## Documentation Generator
Produces coherent documents from persisted structured results.

## Reliability
All outputs must be schema-validated. Retry malformed outputs a limited number of times. Preserve assumptions and flag uncertainty.

## Prompt Injection
Project descriptions are untrusted data. They must not override system constraints or cause tools, shell commands, or generated code to execute.
