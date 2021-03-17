from orator.migrations import Migration


class AddGuildIdToCompfessions(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('compfessions') as table:
            table.big_integer('guild_id').nullable()
            table.foreign('guild_id').references('id').on('guilds')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('compfessions') as table:
            table.drop_foreign('compfessions_guild_id_foreign')
            table.drop_column('guild_id')
