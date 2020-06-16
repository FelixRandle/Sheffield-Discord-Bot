from orator.migrations import Migration


class CreateMessagesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('messages') as table:
            table.big_integer('messageId').primary()
            table.big_integer('authorId')
            table.foreign('authorId').references('userId').on('users')
            table.big_integer('guildId')
            table.foreign('guildId').references('guildId').on('guilds')
            table.long_text('content').nullable()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('messages')
