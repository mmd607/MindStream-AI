from app.ai.mock_provider import MockAIProvider


def test_mock_provider_is_context_aware_for_food_delivery():
    blueprint = MockAIProvider().generate_blueprint("Food Delivery", "Customers order food from restaurants and delivery drivers deliver orders with payments.", [])
    names = {entity.name for entity in blueprint.entities}
    assert {"customers", "restaurants", "menus", "orders", "delivery_drivers", "payments"} <= names
    assert "Customer" in blueprint.actors
    assert any("order" in item.title.lower() for item in blueprint.functional_requirements)


def test_mock_provider_is_context_aware_for_university():
    blueprint = MockAIProvider().generate_blueprint("Course Platform", "A university course management system for students, professors, assignments, exams, and submissions.", [])
    names = {entity.name for entity in blueprint.entities}
    assert {"students", "professors", "courses", "enrollments", "assignments", "exams", "submissions"} <= names
    assert "Student" in blueprint.actors
    assert any("enroll" in item.title.lower() for item in blueprint.functional_requirements)
