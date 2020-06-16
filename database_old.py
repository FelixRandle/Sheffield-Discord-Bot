#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Class to handle all database connections."""

import os
from time import time

import mysql.connector as sql

# Load env if we're just running this file.
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
SQL_USER = os.getenv("SQL_USER")
SQL_PASS = os.getenv("SQL_PASS")
SQL_DB = os.getenv("SQL_DB")
SQL_HOST = os.getenv("SQL_HOST")
SQL_PORT = os.getenv("SQL_PORT")

for var in (SQL_USER, SQL_PASS, SQL_DB, SQL_HOST, SQL_PORT):
    if var is None:
        raise Exception("Cannot find required database login information")


class Database:

    def __enter__(self, *args, **kwargs):
        # Connect to the database

        self.db_config = {
            'host': SQL_HOST,
            'port': SQL_PORT,
            'database': SQL_DB,
            'user': SQL_USER,
            'password': SQL_PASS,
            'charset': 'utf8mb4',
            'use_unicode': True,
            'get_warnings': True,
            'autocommit': True,
            'raise_on_warnings': False
        }

        self.connection = sql.Connect(**self.db_config)

        self.cursor = self.connection.cursor(dictionary=True)

        return self

    def __exit__(self, exception_type, value, traceback):
        self.connection.close()


async def add_user(discord_id, bot):
    with Database() as db:
        if bot:
            return
        try:
            db.cursor.execute(f"""
                INSERT INTO USERS (
                    userID
                )
                VALUES (
                    %s
                )
            """, (discord_id, ))

            db.connection.commit()
            return db.cursor.lastrowid
        except sql.errors.IntegrityError:
            return False


async def add_guild(guild_id, registering_id, member_id):
    with Database() as db:
        try:
            db.cursor.execute(f"""
                INSERT INTO GUILDS (
                    guildID, registeringID, memberID
                )
                VALUES (
                    %s,
                    %s,
                    %s
                )
            """, (guild_id, registering_id, member_id))

            db.connection.commit()
        except sql.errors.IntegrityError:
            pass


async def get_guild_info(guild_id, field="*"):
    # We use string formatting for field since it is only created internally
    # and if we used the same method as guild_id, it would be escaped.
    with Database() as db:
        db.cursor.execute(f"""
            SELECT {field} FROM GUILDS
            WHERE guildID = %s
        """, (guild_id,))

        result = db.cursor.fetchone()

        if field != "*" and result[field]:
            return int(result[field])
        if result:
            return result
        return False


async def set_guild_info(guild_id, field, new_value):
    # We use string formatting for field since it is only created internally
    # and if we used the same method as guild_id, it would be escaped.
    with Database() as db:
        try:
            db.cursor.execute(f"""
                UPDATE GUILDS
                SET {field} = %s
                WHERE guildID = %s
            """, (new_value, guild_id))

            db.connection.commit()
        except sql.errors.IntegrityError:
            return False


async def user_create_channel(user_id, channel_id, is_voice):
    with Database() as db:
        try:
            db.cursor.execute(f"""
                INSERT INTO CHANNELS
                (channelID, voice, owner, createdDate)
                VALUES
                (%s, %s, %s, %s)
            """, (channel_id, is_voice, user_id, int(time())))
            db.connection.commit()
        except sql.errors.IntegrityError:
            return False, "UNIQUE constraint failed..."


async def user_delete_channel(user_id):
    with Database() as db:
        try:
            db.cursor.execute(f"""
                DELETE FROM CHANNELS
                WHERE owner = %s
            """, (user_id,))
            db.connection.commit()
        except sql.errors.IntegrityError:
            return False, "UNIQUE constraint failed..."


async def user_has_channel(user_id):
    with Database() as db:
        db.cursor.execute(f"""
            SELECT channelID FROM CHANNELS
            WHERE owner = %s
        """, (user_id,))

        result = db.cursor.fetchone()
        if result:
            return result['channelID']
        return False


async def get_poll_by_id(poll_id, field="*"):
    with Database() as db:
        db.cursor.execute(f"""
            SELECT {field} FROM POLLS
            WHERE ID = %s
        """, (poll_id, ))

        return db.cursor.fetchone()


async def get_poll_by_message_id(message_id, field="*"):
    with Database() as db:
        db.cursor.execute(f"""
            SELECT {field} FROM POLLS
            WHERE messageID = %s
        """, (message_id, ))

        return db.cursor.fetchone()


async def user_create_poll(user_id, message_id, channel_id,
                           guild_id, poll_title, end_date: int):
    with Database() as db:
        try:
            db.cursor.execute("""
                INSERT INTO POLLS
                (creator, messageID, channelID, guild, title, endDate)
                VALUES
                (%s, %s, %s, %s, %s, %s)
            """, (user_id, message_id, channel_id,
                  guild_id, poll_title, end_date))
            db.connection.commit()
        except sql.errors.IntegrityError:
            return False, "UNIQUE constraint failed"


async def update_poll_message_info(poll_id, message_id, channel_id):
    with Database() as db:
        try:
            db.cursor.execute("""
                UPDATE POLLS SET messageID = %s, channelID = %s
                WHERE ID = %s
            """, (message_id, channel_id, poll_id))
            db.connection.commit()
        except sql.errors.IntegrityError:
            return False, "Integrity error"


async def get_all_ongoing_polls(field="*"):
    with Database() as db:
        db.cursor.execute(f"""
            SELECT {field} FROM POLLS
            WHERE ended = FALSE
        """)

        return db.cursor.fetchall()


async def change_poll_end_date(poll_id, end_date):
    with Database() as db:
        db.cursor.execute("""
            UPDATE POLLS SET endDate = %s
            WHERE ID = %s
        """, (end_date, poll_id))


async def end_poll(poll_id):
    with Database() as db:
        db.cursor.execute("""
            UPDATE POLLS SET ended = TRUE
            WHERE ID = %s
        """, (poll_id, ))

        return db.cursor.rowcount > 0


async def delete_poll(poll_id):
    with Database() as db:
        db.cursor.execute("""
            DELETE FROM POLLS
            WHERE ID = %s
        """, (poll_id, ))
        db.connection.commit()


async def get_poll_choice(poll_id, reaction, field="*"):
    with Database() as db:
        db.cursor.execute(f"""
            SELECT {field} FROM POLL_CHOICES
            WHERE poll = %s AND reaction = %s
        """, (poll_id, reaction.encode()))

        return db.cursor.fetchone()


async def add_poll_choice(poll_id, reaction, text):
    with Database() as db:
        try:
            db.cursor.execute("""
                INSERT INTO POLL_CHOICES
                (poll, reaction, text)
                VALUES
                (%s, %s, %s)
            """, (poll_id, reaction.encode(), text.encode()))
        except sql.errors.IntegrityError:
            return False, "UNIQUE constraint failed"


async def user_has_response(user_id, poll_id, reaction):
    with Database() as db:
        choice = await get_poll_choice(poll_id, reaction, field="ID")
        if choice is None:
            return

        choice_id = choice['ID']

        db.cursor.execute("""
            SELECT ID FROM POLL_RESPONSES
            WHERE POLL_RESPONSES.user = %s AND POLL_RESPONSES.choice = %s
        """, (user_id, choice_id))

        return db.cursor.fetchone() is not None


async def user_add_response(user_id, poll_id, reaction):
    with Database() as db:
        choice = await get_poll_choice(poll_id, reaction, field="ID")
        choice_id = choice['ID']
        try:
            db.cursor.execute("""
                INSERT INTO POLL_RESPONSES
                (choice, user)
                VALUES
                (%s, %s)
            """, (choice_id, user_id))
            return True, None
        except sql.errors.IntegrityError:
            return False, "UNIQUE constraint failed"


async def user_remove_response(user_id, poll_id, reaction):
    with Database() as db:
        choice = await get_poll_choice(poll_id, reaction, field="ID")
        choice_id = choice['ID']

        db.cursor.execute("""
            DELETE FROM POLL_RESPONSES
            WHERE choice = %s AND user = %s
        """, (choice_id, user_id))

        if db.cursor.rowcount > 0:
            return True, None
        return False, "Response did not exist"


async def get_poll_choices(poll_id):
    with Database() as db:
        db.cursor.execute("""
            SELECT ID, reaction, text
            FROM POLL_CHOICES
            WHERE POLL_CHOICES.poll = %s
        """, (poll_id, ))

        results = db.cursor.fetchall()
        return results


async def get_discord_user_ids_for_choice(choice_id):
    with Database() as db:
        db.cursor.execute("""
            SELECT USERS.userID
            FROM USERS, POLL_RESPONSES
            WHERE USERS.userID = POLL_RESPONSES.user AND
            POLL_RESPONSES.choice = %s
        """, (choice_id, ))

        return db.cursor.fetchall()


async def log_message(user_id, message_id, message, date_sent):
    with Database() as db:
        try:
            db.cursor.execute(f"""
                INSERT INTO MESSAGE_LOG
                (authorID, messageID, content, dateSent)
                VALUES
                (%s, %s, %s, %s)
            """, (user_id, message_id, message, date_sent))

            db.connection.commit()
            return True
        except sql.errors.IntegrityError:
            return False


async def test_function():
    print(await user_has_channel(247428233086238720))


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_function())
    loop.close()
