from user.models import SoftdeskUser
from projects.models import Project, Contributor
from issues.models import Issue, Comment
from pathlib import Path
import random
import json

DATA_ROOT = Path(Path(__file__).parent, "data")

ISSUES = Path(DATA_ROOT, "issues.json")
PROJECTS = Path(DATA_ROOT, "projects.json")
USERNAMES = Path(DATA_ROOT, "users.json")
COMMENTS = Path(DATA_ROOT, "comments.json")

PASSWORD = "password"


def read_json(path: Path):
    with open(path, "rb") as reader:
        return json.loads(reader.read())


def create_users():

    SoftdeskUser.objects.all().delete()

    usernames: list = read_json(USERNAMES)

    print(f"create {len(usernames)} users...")

    for username in usernames:
        SoftdeskUser.objects.create_user(
            username=username,
            password=PASSWORD,
            age=random.choice(range(16, 60)),
            can_data_be_shared=bool(random.choice(range(2))),
            can_be_contacted=bool(random.choice(range(2))),
        )


def create_projects():

    Project.objects.all().delete()
    Contributor.objects.all().delete()

    projects: dict = read_json(PROJECTS)
    users = SoftdeskUser.objects.all()

    print(f"create {len(projects)} projects...")

    for data in projects:

        project = Project.objects.create(
            description=data["description"],
            type=data["type"],
            author=random.choice(users)
        )

        for i in range(random.randint(3, 10)):
            try:
                Contributor.objects.create(
                    project=project,
                    user=random.choice(users)
                )
            except Exception:
                pass


def create_issues():

    Issue.objects.all().delete()

    issues: dict = read_json(ISSUES)
    projects = Project.objects.all()

    print(f"create {len(issues)} issues...")

    for data in issues:

        project = random.choice(projects)
        contributors = Contributor.objects.filter(project_id=project.pk)

        Issue.objects.create(
            title=data['title'],
            tag=data['tag'],
            state=data['state'],
            description=data['description'],
            priority=data['priority'],
            project=project,
            author=random.choice(contributors).user,
            assigned_user=random.choice(contributors).user
        )


def create_comments():

    Comment.objects.all().delete()

    comments: dict = read_json(COMMENTS)
    issues = Issue.objects.all()

    print(f"create {len(comments)} comments...")

    for data in comments:

        issue = random.choice(issues)
        project = issue.project
        contributors = Contributor.objects.filter(project_id=project.pk)

        Comment.objects.create(
            description=data["description"],
            issue=issue,
            author=random.choice(contributors).user
        )


def run():
    create_users()
    create_projects()
    create_issues()
    create_comments()
