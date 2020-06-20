from orator.migrations import Migration


class RemakeForeignKeys(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('users') as table:
            table.foreign('guild_id').references('id').on('guilds')

        with self.schema.table('channels') as table:
            table.foreign('creator_id').references('id').on('users')

        with self.schema.table('messages') as table:
            table.foreign('author_id').references('id').on('users')

        with self.schema.table('polls') as table:
            table.foreign('creator_id').references('id').on('users')

        with self.schema.table('poll_choices') as table:
            table.foreign('poll_id').references('id').on('polls')

        with self.schema.table('poll_responses') as table:
            table.foreign('choice_id').references('id').on('poll_choices')
            table.foreign('user_id').references('id').on('users')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('users') as table:
            table.drop_foreign('users_guild_id_foreign')

        with self.schema.table('channels') as table:
            table.drop_foreign('channels_creator_id_foreign')

        with self.schema.table('messages') as table:
            table.drop_foreign('messages_author_id_foreign')

        with self.schema.table('polls') as table:
            table.drop_foreign('polls_creator_id_foreign')

        with self.schema.table('poll_choices') as table:
            table.drop_foreign('poll_choices_poll_id_foreign')

        with self.schema.table('poll_responses') as table:
            table.drop_foreign('poll_responses_choice_id_foreign')
            table.drop_foreign('poll_responses_user_id_foreign')
