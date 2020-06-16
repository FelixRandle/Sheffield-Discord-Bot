from orator.migrations import Migration


class CreateUsersTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('users') as table:
            table.big_integer('userId').primary()
            table.big_integer('guildId')
            table.foreign('guildId').references('guildId').on('guilds')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('users')
