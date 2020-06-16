from orator.migrations import Migration


class CreateGuildsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('guilds') as table:
            table.big_integer('guildId').primary()
            table.big_integer('registeringId').unique()
            table.big_integer('memberId').unqiue()
            table.big_integer('welcomeMessageId').unique()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('guilds')
