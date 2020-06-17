#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Class to handle all database connections."""

from orator import DatabaseManager, Model
from orator.migrations import Migrator, DatabaseMigrationRepository

import os
import sys

rollback = False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    if len(sys.argv) > 1 and sys.argv[1] in ("-r","-rollback"):
        rollback = True


SQL_USER = os.getenv("SQL_USER")
SQL_PASS = os.getenv("SQL_PASS")
SQL_DB = os.getenv("SQL_DB")
SQL_HOST = os.getenv("SQL_HOST")
SQL_PORT = os.getenv("SQL_PORT")

for var in (SQL_USER, SQL_PASS, SQL_DB, SQL_HOST, SQL_PORT):
    if var is None:
        raise Exception("Cannot find required database login information")

config = {
    'mysql': {
        'driver': 'mysql',
        'host': SQL_HOST,
        'database': SQL_DB,
        'user': SQL_USER,
        'password': SQL_PASS,
        'prefix': ''
    }
}

db = DatabaseManager(config)

repository = DatabaseMigrationRepository(db, 'migrations')
migrator = Migrator(repository, db)

if not migrator.repository_exists():
    repository.create_repository()

migrator.rollback('./migrations') if rollback else migrator.run('./migrations')

# Tells models to use db to resolve the connection to the DB
Model.set_connection_resolver(db)
