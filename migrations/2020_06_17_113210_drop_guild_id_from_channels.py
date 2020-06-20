from orator.migrations import Migration


class DropGuildIdFromChannels(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('channels') as table:
            table.drop_foreign('channels_guildid_foreign')
            table.drop_column('guildId')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('channels') as table:
            table.big_integer('guildId')
            table.foreign('guildId').references('guildId').on('guilds')
