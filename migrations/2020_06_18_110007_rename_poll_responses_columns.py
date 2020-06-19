from orator.migrations import Migration


class RenamePollResponsesColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE poll_responses RENAME COLUMN choice TO choice_id')
            db.statement(
                'ALTER TABLE poll_responses RENAME COLUMN user TO user_id')

    def down(self):
        """
        Revert the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE poll_responses RENAME COLUMN choice_id TO choice')
            db.statement(
                'ALTER TABLE poll_responses RENAME COLUMN user_id TO user')
