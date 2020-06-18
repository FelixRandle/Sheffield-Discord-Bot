from orator.migrations import Migration


class RenamePollsColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('polls') as table:
            table.rename_column('messageId', 'message_id')
            table.rename_column('creatorId', 'creator_id')
            table.rename_column('endDate', 'end_date')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('polls') as table:
            table.rename_column('message_id', 'messageId')
            table.rename_column('creator_id', 'creatorId')
            table.rename_column('end_date', 'endDate')
