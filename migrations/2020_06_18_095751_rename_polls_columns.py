from orator.migrations import Migration


class RenamePollsColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE polls RENAME COLUMN messageId TO message_id')
            db.statement(
                'ALTER TABLE polls RENAME COLUMN creatorId TO creator_id')
            db.statement(
                'ALTER TABLE polls RENAME COLUMN endDate TO end_date')

    def down(self):
        """
        Revert the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE polls RENAME COLUMN message_id TO messageId')
            db.statement(
                'ALTER TABLE polls RENAME COLUMN creator_id TO creatorId')
            db.statement(
                'ALTER TABLE polls RENAME COLUMN end_date TO endDate')
