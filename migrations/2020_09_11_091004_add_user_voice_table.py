from orator.migrations import Migration


class AddUserVoiceTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('voice') as table:
            table.big_integer('user_id')
            table.foreign('user_id').references('id').on('users')
            table.big_integer('guild_id')
            table.foreign('guild_id').references('id').on('guilds')
            table.integer('time').default(0)

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('voice')
