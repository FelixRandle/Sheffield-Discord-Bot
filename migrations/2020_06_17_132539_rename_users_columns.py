from orator.migrations import Migration


class RenameUsersColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('users') as table:
            table.rename_column('userId', 'id')
            table.rename_column('guildId', 'guild_id')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('users') as table:
            table.rename_column('id', 'userId')
            table.rename_column('guild_id', 'guildId')
