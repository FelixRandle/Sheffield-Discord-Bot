from orator.migrations import Migration


class MakeWelcomeMessageIdOnGuildsNullable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('guilds') as table:
            table.big_integer('welcome_message_id').nullable().change()

    def down(self):
        """
        Revert the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE guilds MODIFY welcome_message_id bigint NOT NULL')
