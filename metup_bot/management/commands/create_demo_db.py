import os
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

DEFAULT_FIXTURE = "demo_data.json"


class Command(BaseCommand):
    help = (
        "Back up the current SQLite database, apply migrations on a "
        "fresh one, and load demo data from a fixture."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default=DEFAULT_FIXTURE,
            help="Fixture file to load after migrate "
            "(default: %(default)s).",
        )
        parser.add_argument(
            "--no-input",
            "--noinput",
            action="store_true",
            dest="no_input",
            help="Do not prompt for confirmation.",
        )

    def handle(self, *args, **options):
        db_setting = settings.DATABASES["default"]
        engine = db_setting.get("ENGINE", "")
        if "sqlite" not in engine:
            raise CommandError(
                "create_demo_db only supports SQLite, "
                f"got engine '{engine}'."
            )

        db_path = Path(db_setting["NAME"])
        fixture = options["fixture"]

        if not options["no_input"]:
            self.stdout.write(
                f"This will back up and replace the database at {db_path}."
            )
            confirm = input("Type 'yes' to continue: ").strip().lower()
            if confirm != "yes":
                raise CommandError("Aborted.")

        connections.close_all()
        backup = self._backup(db_path)

        try:
            self.stdout.write("Applying migrations...")
            call_command("migrate", verbosity=1)
            self.stdout.write(f"Loading fixture '{fixture}'...")
            call_command("loaddata", fixture, verbosity=1)
        except Exception as exc:
            self._restore(db_path, backup)
            raise CommandError(
                f"Demo DB creation failed, restored backup: {exc}"
            ) from exc

        message = f"Demo DB ready at {db_path}."
        if backup is not None:
            message += f" Previous DB backed up at {backup}."
        self.stdout.write(self.style.SUCCESS(message))

    def _backup(self, db_path):
        if not db_path.exists():
            return None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = db_path.with_name(
            f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"
        )
        os.replace(db_path, backup)
        self.stdout.write(f"Backed up existing DB to {backup}")
        return backup

    def _restore(self, db_path, backup):
        if backup is None:
            return
        if db_path.exists():
            db_path.unlink()
        os.replace(backup, db_path)
        self.stderr.write(f"Restored previous DB from {backup}")
