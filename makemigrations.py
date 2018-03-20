import os
import sys

import django
from django.apps import apps
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError


APP_NAME = "djpaypal"

DEFAULT_SETTINGS = dict(
	DATABASES={
		"default": {
			"ENGINE": "django.db.backends.sqlite3",
			"NAME": ":memory:"
		}
	},
	DEBUG=True,
	INSTALLED_APPS=[
		"django.contrib.auth",
		"django.contrib.contenttypes",
		"django.contrib.sessions",
		"django.contrib.sites",
		APP_NAME,
	],
	SITE_ID=1,
	TIME_ZONE="UTC",
)


def check_migrations():
	from django.db.migrations.autodetector import MigrationAutodetector
	from django.db.migrations.executor import MigrationExecutor
	from django.db.migrations.state import ProjectState

	changed = set()

	print("Checking {} migrations...".format(APP_NAME))
	for db in settings.DATABASES.keys():
		try:
			executor = MigrationExecutor(connections[db])
		except OperationalError as e:
			sys.exit(
				"Unable to check migrations due to database: {}".format(e)
			)

		autodetector = MigrationAutodetector(
			executor.loader.project_state(),
			ProjectState.from_apps(apps),
		)

		changed.update(
			autodetector.changes(graph=executor.loader.graph).keys()
		)

	if changed and APP_NAME in changed:
		sys.exit(
			"A migration file is missing. Please run "
			"`python makemigrations.py` to generate it."
		)
	else:
		print("All migration files present.")


def run(*args):
	"""
	Check and/or create Django migrations.

	If --check is present in the arguments then migrations are checked only.
	"""
	if not settings.configured:
		settings.configure(**DEFAULT_SETTINGS)

	django.setup()

	parent = os.path.dirname(os.path.abspath(__file__))
	sys.path.insert(0, parent)

	if "--check" in args:
		check_migrations()
	else:
		django.core.management.call_command("makemigrations", APP_NAME, *args)


if __name__ == "__main__":
	run(*sys.argv[1:])
