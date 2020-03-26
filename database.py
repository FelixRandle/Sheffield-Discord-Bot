"""Class to handle all database connections."""

import os
import mysql.connector as sql

SQL_USER = os.getenv("SQL_USER")
SQL_PASS = os.getenv("SQL_PASS")

if SQL_USER is None or SQL_PASS is None:
    raise Exception("Cannot find required database login information")


class Database:

    def __init__(self, *args, **kwargs):
        # Connect to the database
        db_config = {
            'host': '209.97.130.228',
            'port': 3306,
            'database': 'sheffieldcompsci',
            'user': SQL_USER,
            'password': SQL_PASS,
            'charset': 'utf8',
            'use_unicode': True,
            'get_warnings': True,
            'autocommit': True
        }

        self.db = sql.Connect(**db_config)

        self.cursor = self.db.cursor(dictionary=True)

        self.create_tables()

    def create_tables(self):
        query_list = (
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
            """,
            """
            CREATE TABLE IF NOT EXISTS
            GUILDS (
                ID INT NOT NULL AUTO_INCREMENT,
                guildID VARCHAR(255) NOT NULL UNIQUE,
                registeringID VARCHAR(255) UNIQUE,
                memberID VARCHAR(255) UNIQUE,
                welcomeMessageID VARCHAR(255) UNIQUE,
                
                PRIMARY KEY(ID)
            )
            """
        )

        for query in query_list:
            try:
                self.cursor.execute(query)
            except sql.errors.ProgrammingError:
                print(f"Query \n'{query}'\n raised an error, ensure that the "
                      "syntax is correct.")

    def add_user(self, member):
        if member.bot:
            print("Cannot add bot to database")
            return
        try:
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
        except sql.errors.IntegrityError:
            print(f"Cannot add user {member.name} : {member.id}, "
                  "duplicate entry.")

    def add_guild(self, id, registering_id, member_id):
        try:
            self.cursor.execute(f"""
                INSERT INTO GUILDS (
                    guildID, registeringID, memberID
                )
                VALUES (
                    {id},
                    \"{registering_id}\",
                    \"{member_id}\"
                )
            """)

            self.db.commit()
        except sql.errors.IntegrityError:
            print(f"Cannot add guild {id}"
                  "duplicate entry.")

    async def get_guild_info(self, guild_id, field="*"):
        # We use string formatting for field since it is only created internally
        # and if we used the same method as guild_id, it would be escaped.
        self.cursor.execute(f"""
            SELECT {field} FROM GUILDS
            WHERE guildID = %s
        """, (guild_id, ))

        result = self.cursor.fetchone()

        if field != "*" and result[field]:
            return int(result[field])
        elif result:
            return result
        else:
            return False

    async def set_guild_info(self, guild_id, field, new_value):
        # We use string formatting for field since it is only created internally
        # and if we used the same method as guild_id, it would be escaped.
        try:
            self.cursor.execute(f"""
                UPDATE GUILDS
                SET {field} = %s
                WHERE guildID = %s
            """, (new_value, guild_id))

            self.db.commit()
        except sql.errors.IntegrityError:
            return False


if __name__ == "__main__":
    db = Database()
