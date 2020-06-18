from orator.migrations import Migration


class DropGuildIdFromPolls(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('polls') as table:
            table.drop_foreign('polls_guildid_foreign')
            table.drop_column('guildId')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('polls') as table:
            table.big_integer('guildId')
            table.foreign('guildId').references('guildId').on('guilds')
