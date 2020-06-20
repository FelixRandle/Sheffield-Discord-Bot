from orator.migrations import Migration


class CreateChannelsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('channels') as table:
            table.big_integer('channelId').primary()
            table.boolean('voice')
            table.big_integer('creator')
            table.foreign('creator').references('userId').on('users')
            table.big_integer('guildId')
            table.foreign('guildId').references('guildId').on('guilds')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('channels')
