from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Activity, Milestone, Person, Project, ProjectMembership, ProjectRisk, ProjectWorkspaceMetadata, Report
from app.planners.orchestrator import PlanningOrchestrator
from app.models import ArchitecturePlan, GenerationRun


DEMO_PROJECTS = [
    ("University Course Management", "Education", "A course workspace for students, professors, assignments, exams, and submissions.", "active", 84, 68, ["Sara Rahimi", "Omar Davis", "Nina Patel"]),
    ("Food Delivery Platform", "Consumer services", "A reliable food ordering platform connecting customers, restaurants, drivers, and payments.", "at_risk", 72, 49, ["Sara Rahimi", "Leo Martin", "Maya Chen"]),
    ("AI Customer Support", "Customer experience", "An AI-assisted support workspace for triage, knowledge, conversations, and human escalation.", "planning", 78, 32, ["Alex Morgan", "Sara Rahimi", "Maya Chen"]),
    ("Logistics Control Center", "Operations", "A control center for fleet visibility, shipment tracking, dispatch, and operational alerts.", "active", 81, 57, ["Omar Davis", "Nina Patel", "Leo Martin"]),
    ("Healthcare Appointment Platform", "Healthcare", "A privacy-conscious appointment platform for patients, clinicians, schedules, and reminders.", "paused", 69, 28, ["Maya Chen", "Alex Morgan", "Nina Patel"]),
    ("E-commerce Analytics", "Analytics", "A decision workspace that turns store, campaign, and customer data into actionable insights.", "completed", 91, 100, ["Alex Morgan", "Sara Rahimi", "Omar Davis"]),
]

PEOPLE = {
    "Alex Morgan": ("alex.morgan@example.local", "Product strategist"),
    "Sara Rahimi": ("sara.rahimi@example.local", "Senior backend engineer"),
    "Omar Davis": ("omar.davis@example.local", "Delivery lead"),
    "Nina Patel": ("nina.patel@example.local", "QA and research lead"),
    "Leo Martin": ("leo.martin@example.local", "Frontend engineer"),
    "Maya Chen": ("maya.chen@example.local", "AI product engineer"),
}


def seed_demo_data(db: Session) -> None:
    for name, domain, description, status, health, progress, member_names in DEMO_PROJECTS:
        project = db.scalar(select(Project).where(Project.name == name))
        if not project:
            project = Project(name=name, description=description, target_users=["Project team", "Stakeholders"], preferred_stack=["Next.js", "FastAPI", "PostgreSQL"], team_size=len(member_names), status=status)
            db.add(project)
            db.flush()
        metadata = project.workspace_metadata or ProjectWorkspaceMetadata(project_id=project.id)
        metadata.domain = domain
        metadata.health_score = health
        metadata.progress = progress
        metadata.status_description = f"{domain} workspace with a connected blueprint and delivery view."
        metadata.status_reason = "Payment integration needs attention" if status == "at_risk" else ""
        metadata.executive_summary = f"{name} is a {domain.lower()} project with a structured blueprint, visible delivery work, and shared ownership across the workspace."
        db.add(metadata)
        project.status = status
        project.team_size = len(member_names)
        for index, person_name in enumerate(member_names):
            email, title = PEOPLE[person_name]
            person = db.scalar(select(Person).where(Person.email == email))
            if not person:
                person = Person(name=person_name, email=email, title=title)
                db.add(person)
                db.flush()
            membership = db.scalar(select(ProjectMembership).where(ProjectMembership.project_id == project.id, ProjectMembership.person_id == person.id))
            if not membership:
                role = "Project Manager" if index == 0 else ("Backend Developer" if "engineer" in title else "Frontend Developer")
                membership = ProjectMembership(project_id=project.id, person_id=person.id, role_title=role, workload_percent=70 - index * 10, modules_json=["Core platform", "Delivery"])
                db.add(membership)
        db.flush()
        architecture = db.scalar(select(ArchitecturePlan).where(ArchitecturePlan.project_id == project.id))
        if not architecture or not project.features or not project.apis:
            run = GenerationRun(project_id=project.id, run_type="seed", status="queued")
            db.add(run)
            db.flush()
            PlanningOrchestrator().run(db, project, run)
            project.status = status
        if not db.scalar(select(Milestone.id).where(Milestone.project_id == project.id)):
            db.add_all([
                Milestone(project_id=project.id, title="Scope and discovery", description="Align users, workflows, and success measures.", status="done", progress=100, due_label="Complete"),
                Milestone(project_id=project.id, title="Core workflow", description="Deliver the highest-value product path.", status="in_progress", progress=min(progress, 82), due_label="This sprint"),
                Milestone(project_id=project.id, title="Release readiness", description="Validate quality, documentation, and operational readiness.", status="planned", progress=18, due_label="Next month"),
            ])
        if not db.scalar(select(ProjectRisk.id).where(ProjectRisk.project_id == project.id)):
            db.add_all([
                ProjectRisk(project_id=project.id, title="Uncovered edge cases", description="Some user journeys still need explicit acceptance criteria.", severity="medium", status="open", owner_name=member_names[0]),
                ProjectRisk(project_id=project.id, title="Delivery dependency", description="An external integration may affect the next milestone.", severity="high" if status == "at_risk" else "low", status="open" if status == "at_risk" else "monitoring", owner_name=member_names[min(1, len(member_names) - 1)]),
            ])
        if not db.scalar(select(Report.id).where(Report.project_id == project.id)):
            db.add(Report(project_id=project.id, report_type="health", title="Weekly Project Health", summary=f"{name} is currently {status.replace('_', ' ')} with a health score of {health}.", generated_by="mock-ai", status="generated", score=health, content=f"# Weekly Project Health\n\n{name} has a health score of **{health} / 100**.\n\nReview the open delivery risks before the next checkpoint."))
        if not db.scalar(select(Activity.id).where(Activity.project_id == project.id)):
            db.add_all([
                Activity(project_id=project.id, actor_name="MindStream AI", action="Blueprint analyzed", category="analysis", details="Requirements, architecture, database, and delivery tasks are available."),
                Activity(project_id=project.id, actor_name=member_names[0], action="Reviewed project direction", category="project", details="The workspace is ready for the next planning checkpoint."),
            ])
    db.commit()
