#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for database connection configuration

This file can be passed as the config file to the Orator CLI, e.g.
`orator migrate -c database.py`
"""

import os

from dotenv import load_dotenv
from orator import DatabaseManager

load_dotenv()

SQL_USER = os.getenv("SQL_USER")
SQL_PASS = os.getenv("SQL_PASS")
SQL_DB = os.getenv("SQL_DB")
SQL_HOST = os.getenv("SQL_HOST")
SQL_PORT = os.getenv("SQL_PORT")

for var in (SQL_USER, SQL_PASS, SQL_DB, SQL_HOST, SQL_PORT):
    if var is None:
        raise Exception("Cannot find required database login information")

DATABASES = {
    'mysql': {
        'driver': 'mysql',
        'host': SQL_HOST,
        'database': SQL_DB,
        'user': SQL_USER,
        'password': SQL_PASS,
        'charset': 'utf8mb4',
        'prefix': '',
    }
}

db = DatabaseManager(DATABASES)
