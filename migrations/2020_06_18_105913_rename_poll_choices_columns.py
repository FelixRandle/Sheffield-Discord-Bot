from orator.migrations import Migration


class RenamePollChoicesColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE poll_choices RENAME COLUMN poll TO poll_id')

    def down(self):
        """
        Revert the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE poll_choices RENAME COLUMN poll_id TO poll')
