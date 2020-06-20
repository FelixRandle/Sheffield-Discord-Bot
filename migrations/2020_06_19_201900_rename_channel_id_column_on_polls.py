from orator.migrations import Migration


class RenameChannelIdColumnOnPolls(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE polls RENAME COLUMN channelId TO channel_id')

    def down(self):
        """
        Revert the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE polls RENAME COLUMN channel_id TO channelId')
