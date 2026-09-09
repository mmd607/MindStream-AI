from app.ai.schemas import Blueprint


def markdown_for_blueprint(project_name: str, description: str, blueprint: Blueprint) -> str:
    lines = [f"# {project_name}", "", description, "", "## Overview", "", blueprint.objective, "", "## Actors", ""]
    lines += [f"- {actor}" for actor in blueprint.actors]
    lines += ["", "## Assumptions", ""] + [f"- {item}" for item in blueprint.assumptions]
    lines += ["", "## Constraints", ""] + [f"- {item}" for item in blueprint.constraints]
    lines += ["", "## Risks", ""] + [f"- {item}" for item in blueprint.risks]
    lines += ["", "## Open Questions", ""] + [f"- {item}" for item in blueprint.open_questions]
    lines += ["", "## Requirements", ""]
    for item in blueprint.functional_requirements + blueprint.non_functional_requirements:
        lines += [f"### {item.title} ({item.priority})", "", item.description, ""]
    lines += ["## Architecture", "", f"**Style:** {blueprint.architecture_style}", "", blueprint.architecture_rationale, "", "```mermaid", "flowchart TD", "    User --> Frontend", "    Frontend --> Backend", "    Backend --> Planner", "    Planner --> Database", "```", ""]
    lines += ["### Components", ""] + [f"- **{item.name}:** {item.responsibility}" for item in blueprint.components] + ["", "### Technologies", ""] + [f"- **{item.name}:** {item.rationale}" for item in blueprint.technologies] + ["", "## Database", ""]
    for entity in blueprint.entities:
        lines += [f"### {entity.name}", "", entity.description, "", "| Field | Type | Key | Nullable |", "|---|---|---|---|"]
        lines += [f"| {field.name} | {field.data_type} | {'PK' if field.primary_key else 'Unique' if field.unique else ''} | {'yes' if field.nullable else 'no'} |" for field in entity.fields] + [""]
    lines += ["## API and Modules", ""] + [f"- {module}" for module in blueprint.api_modules] + ["", "## Implementation Tasks", "", "| Key | Task | Role | Effort | Depends on |", "|---|---|---|---:|---|"]
    lines += [f"| {task.key} | {task.title} | {task.role} | {task.effort} | {', '.join(task.depends_on) or '—'} |" for task in blueprint.tasks] + ["", "## Roles", ""]
    lines += [f"- **{role.name}:** {role.description}" for role in blueprint.roles] + ["", "## Assumptions and Risks", ""]
    lines += [f"- Assumption: {item}" for item in blueprint.assumptions] + [f"- Risk: {item}" for item in blueprint.risks]
    return "\n".join(lines) + "\n"
