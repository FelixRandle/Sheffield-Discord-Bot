"""Class to handle all database connections."""

import os
import mysql.connector

SQL_USER = os.getenv("SQL_USER")
SQL_PASS = os.getenv("SQL_PASS")

if SQL_USER is None or SQL_PASS is None:
    raise("Cannot find required database login information")


class Database:

    def __init__(self, *args, **kwargs):
        # Connect to the database
        dbconfig = {
            'host': '178.62.38.210',
            'port': 3306,
            'database': 'sheffieldcompsci',
            'user': SQL_USER,
            'password': SQL_PASS,
            'charset': 'utf8',
            'use_unicode': True,
            'get_warnings': True,
            'autocommit': True
        }

        self.db = mysql.connector.Connect(**dbconfig)

        self.cursor = self.db.cursor()

        self.create_tables()

    def create_tables(self):
        queryList = [
            """
            CREATE TABLE IF NOT EXISTS
            USERS (
                ID INT NOT NULL AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                discordID VARCHAR(255) UNIQUE NOT NULL,
                PRIMARY KEY (ID)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS
            EVENTS (
                ID INT NOT NULL AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                description VARCHAR(1024) NOT NULL,
                date DATETIME NOT NULL,
                creator INT NOT NULL,

                PRIMARY KEY (ID),
                FOREIGN KEY (creator)
                    REFERENCES USERS(ID)
            )
            """
        ]

        for query in queryList:
            try:
                self.cursor.execute(query)
            except mysql.connector.errors.ProgrammingError:
                print(f"Query \n'{query}'\n raised an error, ensure that the "
                      "syntax is correct.")

    def add_user(self, member):
        if member.bot:
            print("Cannot add bot to database")
            return
        print(member.name, member.id)
        self.cursor.execute(f"""
            INSERT INTO USERS (
                name, discordID
            )
            VALUES (
                \"{member.name}\",
                {member.id}
            )
        """)

        self.db.commit()


if __name__ == "__main__":
    db = Database()
