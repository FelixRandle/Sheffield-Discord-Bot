from orator.migrations import Migration


class RenameChannelsColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('channels') as table:
            table.rename_column('channelId', 'id')
            table.rename_column('creator', 'creator_id')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('channels') as table:
            table.rename_column('id', 'channelId')
            table.rename_column('creator_id', 'creator')
