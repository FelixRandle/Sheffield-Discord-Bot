from orator.migrations import Migration


class DropForeignKeys(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('users') as table:
            table.drop_foreign('users_guildid_foreign')

        with self.schema.table('channels') as table:
            table.drop_foreign('channels_creator_foreign')

        with self.schema.table('messages') as table:
            table.drop_foreign('messages_authorid_foreign')

        with self.schema.table('polls') as table:
            table.drop_foreign('polls_creatorid_foreign')

        with self.schema.table('poll_choices') as table:
            table.drop_foreign('poll_choices_poll_foreign')

        with self.schema.table('poll_responses') as table:
            table.drop_foreign('poll_responses_choice_foreign')
            table.drop_foreign('poll_responses_user_foreign')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('users') as table:
            table.foreign('guildId').references('guildId').on('guilds')

        with self.schema.table('channels') as table:
            table.foreign('creator').references('userId').on('users')

        with self.schema.table('messages') as table:
            table.foreign('authorId').references('userId').on('users')

        with self.schema.table('polls') as table:
            table.foreign('creatorId').references('userId').on('users')

        with self.schema.table('poll_choices') as table:
            table.foreign('poll').references('id').on('polls')

        with self.schema.table('poll_responses') as table:
            table.foreign('choice').references('id').on('poll_choices')
            table.foreign('user').references('userId').on('users')
