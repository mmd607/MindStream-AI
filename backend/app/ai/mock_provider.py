from app.ai.schemas import Blueprint


class MockAIProvider:
    name = "mock"

    def generate_blueprint(self, project_name: str, description: str, preferred_stack: list[str]) -> Blueprint:
        context = f"{project_name} {description}".lower()
        blueprint = self._base_blueprint(project_name, description, preferred_stack)
        return self._apply_context(blueprint, context)

    def _base_blueprint(self, project_name: str, description: str, preferred_stack: list[str]) -> Blueprint:
        stack = preferred_stack or ["Next.js", "FastAPI", "PostgreSQL"]
        return Blueprint(
            objective=f"Deliver {project_name} as a useful, maintainable product for its intended users.",
            actors=["End user", "Project administrator", "System operator"],
            functional_requirements=[
                {"category": "functional", "title": "Create and manage core records", "description": "Users can create, view, update, and remove the primary records described by the project.", "priority": "high"},
                {"category": "functional", "title": "Search and view project information", "description": "Users can find relevant information through a clear, responsive interface.", "priority": "high"},
                {"category": "functional", "title": "Provide a documented API", "description": "The backend exposes versioned endpoints for the main workflows.", "priority": "medium"},
            ],
            non_functional_requirements=[
                {"category": "non_functional", "title": "Validate user input", "description": "Requests are validated for shape, size, and safe values before processing.", "priority": "high"},
                {"category": "non_functional", "title": "Maintain responsive performance", "description": "Common dashboard operations should return promptly and avoid unnecessary work.", "priority": "medium"},
                {"category": "non_functional", "title": "Protect sensitive configuration", "description": "Credentials stay in environment variables and never reach the browser.", "priority": "critical"},
            ],
            assumptions=["The first release is used by a small team.", "Authentication and multi-tenant ownership can be added in a later version.", "The team can run the application with Docker or a local Python/Node setup."],
            constraints=["Use a modular monolith for the MVP.", "Do not execute generated code, commands, or SQL.", "The application must work in mock AI mode without a provider key."],
            risks=["Natural-language project descriptions may contain ambiguity.", "A generated plan requires human review before production implementation.", "External model availability may vary."],
            open_questions=["Which workflows need authentication in the next release?", "What compliance or availability targets apply after the MVP?"],
            architecture_style="Modular monolith",
            architecture_rationale="A modular monolith keeps local development and debugging simple while separating the API, planning, validation, and persistence responsibilities for future growth.",
            components=[
                {"name": "Next.js web app", "responsibility": "Collect project ideas and present the generated blueprint."},
                {"name": "FastAPI API", "responsibility": "Validate requests and expose versioned project and blueprint endpoints."},
                {"name": "Planning orchestrator", "responsibility": "Run explicit planning stages and validate structured outputs."},
                {"name": "Relational database", "responsibility": "Persist projects, plans, tasks, documents, and generation audit records."},
            ],
            technologies=[{"name": item, "rationale": "Fits the MVP requirements and has a mature ecosystem."} for item in stack],
            communication_paths=["Browser → Next.js → FastAPI REST API", "FastAPI → application services → planning orchestrator", "Application services → SQLAlchemy → PostgreSQL/SQLite"],
            deployment_concept="Docker Compose runs the frontend, backend, and PostgreSQL database on a local network.",
            scalability_considerations=["Move generation to a background worker when runs become long-lived.", "Add authentication and project ownership before multi-user hosting.", "Add pagination and indexes as project collections grow."],
            entities=[
                {"name": "users", "description": "People who use the planned product.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "email", "data_type": "VARCHAR(255)", "nullable": False, "unique": True}, {"name": "created_at", "data_type": "TIMESTAMP", "nullable": False}]},
                {"name": "projects", "description": "Primary records for the planned product.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "name", "data_type": "VARCHAR(120)", "nullable": False}, {"name": "description", "data_type": "TEXT", "nullable": False}, {"name": "created_at", "data_type": "TIMESTAMP", "nullable": False}]},
                {"name": "activities", "description": "A record of meaningful actions or domain events.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "project_id", "data_type": "UUID", "nullable": False, "foreign_key": "projects.id"}, {"name": "title", "data_type": "VARCHAR(180)", "nullable": False}, {"name": "status", "data_type": "VARCHAR(30)", "nullable": False}]},
            ],
            roles=[
                {"name": "Project Manager", "description": "Clarifies scope, priorities, milestones, and acceptance criteria."},
                {"name": "Backend Developer", "description": "Implements domain services, persistence, and APIs."},
                {"name": "Frontend Developer", "description": "Builds accessible screens and connects them to the API."},
                {"name": "Database Engineer", "description": "Designs constraints, indexes, and migrations."},
                {"name": "QA Engineer", "description": "Verifies workflows, validation, and regression safety."},
                {"name": "DevOps Engineer", "description": "Maintains reproducible local and deployment environments."},
            ],
            tasks=[
                {"key": "T1", "title": "Define project scope and acceptance criteria", "description": "Turn the project idea into a reviewed scope baseline.", "task_type": "story", "priority": "high", "effort": 3, "role": "Project Manager", "acceptance_criteria": ["Scope and actors are documented", "Open questions are recorded"]},
                {"key": "T2", "title": "Create database schema and migration", "description": "Implement the core entities, fields, foreign keys, and indexes.", "task_type": "task", "priority": "high", "effort": 5, "role": "Database Engineer", "depends_on": ["T1"], "acceptance_criteria": ["Migration applies to a clean database", "Required keys and constraints are present"]},
                {"key": "T3", "title": "Implement backend services and API", "description": "Build validated service methods and versioned endpoints for core workflows.", "task_type": "task", "priority": "high", "effort": 8, "role": "Backend Developer", "depends_on": ["T2"], "acceptance_criteria": ["Happy path endpoints return typed responses", "Missing resources return safe 404 errors"]},
                {"key": "T4", "title": "Build responsive frontend workflow", "description": "Create project entry, dashboard, blueprint sections, and feedback states.", "task_type": "task", "priority": "high", "effort": 8, "role": "Frontend Developer", "depends_on": ["T3"], "acceptance_criteria": ["User can create and analyze a project", "Loading, empty, and error states are visible"]},
                {"key": "T5", "title": "Add integration and security tests", "description": "Verify generation, persistence, export, validation, and safe handling of untrusted content.", "task_type": "task", "priority": "critical", "effort": 5, "role": "QA Engineer", "depends_on": ["T3", "T4"], "acceptance_criteria": ["End-to-end mock flow passes", "Invalid input and cycle detection are covered"]},
                {"key": "T6", "title": "Document local deployment", "description": "Document manual startup, Docker Compose, environment variables, and roadmap.", "task_type": "task", "priority": "medium", "effort": 3, "role": "DevOps Engineer", "depends_on": ["T3"], "acceptance_criteria": ["A new developer can follow the setup guide", "Secrets are represented only by placeholders"]},
            ],
            api_modules=["Projects", "Requirements", "Architecture", "Database", "Tasks", "Team", "Documentation", "Exports", "Generation Runs"],
        )

    def _apply_context(self, blueprint: Blueprint, context: str) -> Blueprint:
        payload = blueprint.model_dump()
        if any(word in context for word in ("food", "restaurant", "delivery", "driver", "menu", "order", "payment")):
            payload.update({
                "objective": "Plan an online food delivery platform connecting customers, restaurants, delivery drivers, and payment workflows.",
                "actors": ["Customer", "Restaurant staff", "Delivery driver", "Administrator"],
                "functional_requirements": [
                    {"category": "functional", "title": "Browse restaurant menus", "description": "Customers can discover restaurants and browse available menus.", "priority": "high"},
                    {"category": "functional", "title": "Place and track food orders", "description": "Customers can place orders, pay securely, and track delivery status.", "priority": "critical"},
                    {"category": "functional", "title": "Manage restaurant fulfillment", "description": "Restaurant staff can accept orders, update preparation status, and manage menus.", "priority": "high"},
                    {"category": "functional", "title": "Coordinate delivery drivers", "description": "Drivers can accept deliveries and update pickup and drop-off progress.", "priority": "high"},
                ] + payload["functional_requirements"][:1],
                "entities": [
                    {"name": "customers", "description": "People who order food through the platform.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "email", "data_type": "VARCHAR(255)", "nullable": False, "unique": True}]},
                    {"name": "restaurants", "description": "Restaurants that publish menus and fulfill orders.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "name", "data_type": "VARCHAR(160)", "nullable": False}]},
                    {"name": "menus", "description": "Restaurant menu items available for ordering.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "restaurant_id", "data_type": "UUID", "nullable": False, "foreign_key": "restaurants.id"}, {"name": "name", "data_type": "VARCHAR(160)", "nullable": False}, {"name": "price", "data_type": "DECIMAL(10,2)", "nullable": False}]},
                    {"name": "orders", "description": "Customer orders moving from restaurant preparation to delivery.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "customer_id", "data_type": "UUID", "nullable": False, "foreign_key": "customers.id"}, {"name": "restaurant_id", "data_type": "UUID", "nullable": False, "foreign_key": "restaurants.id"}, {"name": "status", "data_type": "VARCHAR(30)", "nullable": False}]},
                    {"name": "delivery_drivers", "description": "Drivers assigned to deliver customer orders.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "name", "data_type": "VARCHAR(160)", "nullable": False}, {"name": "availability", "data_type": "VARCHAR(30)", "nullable": False}]},
                    {"name": "payments", "description": "Payment attempts associated with customer orders.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "order_id", "data_type": "UUID", "nullable": False, "foreign_key": "orders.id"}, {"name": "status", "data_type": "VARCHAR(30)", "nullable": False}]},
                ],
                "api_modules": ["Customers", "Restaurants", "Menus", "Orders", "Payments", "Delivery", "Documentation", "Exports"],
            })
            payload["tasks"][2]["description"] = "Implement order, payment, restaurant, and delivery services with versioned APIs."
        elif any(word in context for word in ("university", "course", "student", "professor", "academic", "assignment", "exam")):
            payload.update({
                "objective": "Plan a university course management platform for students, professors, and academic administrators.",
                "actors": ["Student", "Professor", "Administrator"],
                "functional_requirements": [
                    {"category": "functional", "title": "Browse and enroll in courses", "description": "Students can browse the course catalog, enroll in courses, and view their schedules.", "priority": "critical"},
                    {"category": "functional", "title": "Manage assignments and exams", "description": "Professors can publish assignments and exams, while students can track deadlines.", "priority": "high"},
                    {"category": "functional", "title": "Review submissions and progress", "description": "Professors can review submissions and students can view academic progress.", "priority": "high"},
                ] + payload["functional_requirements"][:1],
                "entities": [
                    {"name": "students", "description": "Students enrolled in the university platform.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "email", "data_type": "VARCHAR(255)", "nullable": False, "unique": True}, {"name": "program", "data_type": "VARCHAR(120)", "nullable": False}]},
                    {"name": "professors", "description": "Professors who teach courses and review work.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "name", "data_type": "VARCHAR(160)", "nullable": False}]},
                    {"name": "courses", "description": "Courses offered in the academic catalog.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "professor_id", "data_type": "UUID", "nullable": False, "foreign_key": "professors.id"}, {"name": "title", "data_type": "VARCHAR(180)", "nullable": False}, {"name": "term", "data_type": "VARCHAR(40)", "nullable": False}]},
                    {"name": "enrollments", "description": "Links students to the courses they take.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "student_id", "data_type": "UUID", "nullable": False, "foreign_key": "students.id"}, {"name": "course_id", "data_type": "UUID", "nullable": False, "foreign_key": "courses.id"}, {"name": "status", "data_type": "VARCHAR(30)", "nullable": False}]},
                    {"name": "assignments", "description": "Course assignments with submission deadlines.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "course_id", "data_type": "UUID", "nullable": False, "foreign_key": "courses.id"}, {"name": "title", "data_type": "VARCHAR(180)", "nullable": False}, {"name": "due_at", "data_type": "TIMESTAMP", "nullable": False}]},
                    {"name": "exams", "description": "Scheduled course exams.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "course_id", "data_type": "UUID", "nullable": False, "foreign_key": "courses.id"}, {"name": "starts_at", "data_type": "TIMESTAMP", "nullable": False}]},
                    {"name": "submissions", "description": "Student work submitted for review.", "fields": [{"name": "id", "data_type": "UUID", "nullable": False, "primary_key": True}, {"name": "assignment_id", "data_type": "UUID", "nullable": False, "foreign_key": "assignments.id"}, {"name": "student_id", "data_type": "UUID", "nullable": False, "foreign_key": "students.id"}, {"name": "status", "data_type": "VARCHAR(30)", "nullable": False}]},
                ],
                "api_modules": ["Students", "Professors", "Courses", "Enrollments", "Assignments", "Exams", "Submissions", "Documentation", "Exports"],
            })
            payload["tasks"][2]["description"] = "Implement course, enrollment, assignment, exam, and submission services with versioned APIs."
        return Blueprint.model_validate(payload)
