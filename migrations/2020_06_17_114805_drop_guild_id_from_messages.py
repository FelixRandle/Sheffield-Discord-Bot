from orator.migrations import Migration


class DropGuildIdFromMessages(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('messages') as table:
            table.drop_foreign('messages_guildid_foreign')
            table.drop_column('guildId')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('messages') as table:
            table.big_integer('guildId')
            table.foreign('guildId').references('guildId').on('guilds')
