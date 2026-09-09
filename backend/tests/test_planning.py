from app.ai.mock_provider import MockAIProvider
from app.planners.validator import topological_order, validate_blueprint


def test_mock_provider_is_structured_and_valid():
    blueprint = MockAIProvider().generate_blueprint("Demo", "A useful project description for a student team.", [])
    assert blueprint.architecture_style == "Modular monolith"
    assert not validate_blueprint(blueprint)


def test_topological_order_and_cycle_detection():
    tasks = [{"key": "A", "depends_on": []}, {"key": "B", "depends_on": ["A"]}, {"key": "C", "depends_on": ["B"]}]
    assert topological_order(tasks) == ["A", "B", "C"]
    cyclic = [{"key": "A", "depends_on": ["B"]}, {"key": "B", "depends_on": ["A"]}]
    try:
        topological_order(cyclic)
    except ValueError as error:
        assert "cycle" in str(error)
    else:
        raise AssertionError("cycle should be rejected")

