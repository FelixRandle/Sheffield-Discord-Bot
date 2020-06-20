from orator.migrations import Migration


class CreatePollsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('polls') as table:
            table.increments('id')
            table.big_integer('messageId')
            table.big_integer('channelId')
            table.big_integer('guildId')
            table.foreign('guildId').references('guildId').on('guilds')
            table.big_integer('creatorId')
            table.foreign('creatorId').references('userId').on('users')
            table.string('title', 255)
            table.datetime('endDate')
            table.boolean('ended').default(False)

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('polls')
