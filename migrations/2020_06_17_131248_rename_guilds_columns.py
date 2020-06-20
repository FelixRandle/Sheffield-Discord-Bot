from orator.migrations import Migration


class RenameGuildsColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('guilds') as table:
            table.rename_column('guildId', 'id')
            table.rename_column('registeringId', 'registering_id')
            table.rename_column('memberId', 'member_id')
            table.rename_column('welcomeMessageId', 'welcome_message_id')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('guilds') as table:
            table.rename_column('id', 'guildId')
            table.rename_column('registering_id', 'registeringId')
            table.rename_column('member_id', 'memberId')
            table.rename_column('welcome_message_id', 'welcomeMessageId')
