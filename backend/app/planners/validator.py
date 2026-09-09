from collections import defaultdict, deque

from app.ai.schemas import Blueprint


def validate_blueprint(blueprint: Blueprint) -> list[str]:
    errors: list[str] = []
    roles = {role.name for role in blueprint.roles}
    keys = {task.key for task in blueprint.tasks}
    if not blueprint.functional_requirements:
        errors.append("at least one functional requirement is required")
    if not blueprint.entities:
        errors.append("at least one database entity is required")
    for task in blueprint.tasks:
        if task.role not in roles:
            errors.append(f"task {task.key} references missing role {task.role}")
        for dependency in task.depends_on:
            if dependency not in keys:
                errors.append(f"task {task.key} references missing dependency {dependency}")
            if dependency == task.key:
                errors.append(f"task {task.key} cannot depend on itself")
    graph = defaultdict(list)
    indegree = {key: 0 for key in keys}
    for task in blueprint.tasks:
        for dependency in task.depends_on:
            if dependency in keys:
                graph[dependency].append(task.key)
                indegree[task.key] += 1
    queue = deque(key for key, value in indegree.items() if value == 0)
    visited = 0
    while queue:
        key = queue.popleft()
        visited += 1
        for child in graph[key]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(keys):
        errors.append("task dependencies contain a cycle")
    return errors


def topological_order(tasks: list[dict]) -> list[str]:
    by_key = {task["key"]: task for task in tasks}
    remaining = {key: set(task.get("depends_on", [])) for key, task in by_key.items()}
    order: list[str] = []
    while remaining:
        ready = sorted(key for key, deps in remaining.items() if not deps)
        if not ready:
            raise ValueError("task dependencies contain a cycle")
        order.extend(ready)
        for key in ready:
            remaining.pop(key)
        for deps in remaining.values():
            deps.difference_update(ready)
    return order

