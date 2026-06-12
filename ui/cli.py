from __future__ import annotations

import json
from pathlib import Path

import click

from core.email_handler import EmailHandler
from core.file_manager import FileManager
from core.learning import LearningEngine
from core.task_manager import TaskManager


fm = FileManager()
tasks = TaskManager()
email = EmailHandler()
learning = LearningEngine()


@click.group()
def cli() -> None:
    """Rias local desktop assistant CLI."""


@cli.group()
def files() -> None:
    """File and folder operations."""


@files.command("list")
@click.argument("folder")
def files_list(folder: str) -> None:
    for item in fm.list_items(folder):
        click.echo(item)


@files.command("organize")
@click.argument("folder")
@click.option("--mode", default="type", type=click.Choice(["type", "date"]))
def files_organize(folder: str, mode: str) -> None:
    result = fm.organize(folder, mode=mode)
    learning.record_action("files.organize", mode)
    click.echo(json.dumps(result, indent=2))


@files.command("search")
@click.argument("folder")
@click.argument("query")
@click.option("--content", is_flag=True, default=False)
def files_search(folder: str, query: str, content: bool) -> None:
    for item in fm.search(folder, query, include_content=content):
        click.echo(item)


@files.command("analyze")
@click.argument("folder")
def files_analyze(folder: str) -> None:
    click.echo(json.dumps(fm.analyze(folder), indent=2))


@files.command("clean")
@click.argument("folder")
def files_clean(folder: str) -> None:
    count = fm.clean_empty_dirs(folder)
    click.echo(f"Removed {count} empty folders")


@cli.group()
def task() -> None:
    """Task management."""


@task.command("create")
@click.argument("title")
@click.option("--command", default="")
@click.option("--due-at", default=None)
@click.option("--recurring", default=None, help="Cron expression or label")
def task_create(title: str, command: str, due_at: str | None, recurring: str | None) -> None:
    created = tasks.create(title=title, command=command, due_at=due_at, recurring=recurring)
    learning.record_action("task.create")
    click.echo(created.id)


@task.command("list")
@click.option("--pending-only", is_flag=True, default=False)
def task_list(pending_only: bool) -> None:
    for t in tasks.list(show_completed=not pending_only):
        click.echo(f"{t.id} | {t.title} | completed={t.completed} | recurring={t.recurring}")


@task.command("complete")
@click.argument("task_id")
def task_complete(task_id: str) -> None:
    tasks.complete(task_id)
    learning.record_action("task.complete")
    click.echo("done")


@task.command("delete")
@click.argument("task_id")
def task_delete(task_id: str) -> None:
    tasks.delete(task_id)
    learning.record_action("task.delete")
    click.echo("deleted")


@cli.group()
def email_cmd() -> None:
    """Email compose/send/templates."""


@email_cmd.command("template-save")
@click.argument("name")
@click.argument("subject")
@click.argument("body")
def template_save(name: str, subject: str, body: str) -> None:
    email.save_template(name, subject, body)
    learning.record_action("email.template_save")
    click.echo("saved")


@email_cmd.command("template-list")
def template_list() -> None:
    click.echo(json.dumps(email.list_templates(), indent=2))


@email_cmd.command("send")
@click.argument("to_email")
@click.argument("subject")
@click.argument("body")
def send_email(to_email: str, subject: str, body: str) -> None:
    email.send(to_email, subject, body)
    learning.record_action("email.send")
    click.echo("sent")


@email_cmd.command("send-template")
@click.argument("template_name")
@click.argument("to_email")
@click.option("--var", "variables", multiple=True, help="key=value replacements")
def send_template(template_name: str, to_email: str, variables: tuple[str, ...]) -> None:
    data = {}
    for raw in variables:
        if "=" not in raw:
            raise click.BadParameter("--var must be in key=value format")
        key, value = raw.split("=", 1)
        data[key] = value
    email.send_from_template(template_name, to_email, **data)
    learning.record_action("email.send_template")
    click.echo("sent")


@cli.group()
def prefs() -> None:
    """Learning/preferences."""


@prefs.command("set")
@click.argument("key")
@click.argument("value")
def prefs_set(key: str, value: str) -> None:
    learning.set_preference(key, value)
    learning.record_action("prefs.set")
    click.echo("ok")


@prefs.command("get")
@click.argument("key")
def prefs_get(key: str) -> None:
    click.echo(learning.get_preference(key, ""))


@prefs.command("suggest")
def prefs_suggest() -> None:
    for suggestion in learning.suggestions():
        click.echo(f"- {suggestion}")
