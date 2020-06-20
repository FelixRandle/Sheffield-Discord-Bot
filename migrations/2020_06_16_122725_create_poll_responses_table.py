from orator.migrations import Migration


class CreatePollResponsesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('poll_responses') as table:
            table.increments('id')
            table.big_integer('user')
            table.foreign('user').references('userId').on('users')
            table.integer('choice').unsigned()
            table.foreign('choice').references('id').on('poll_choices')

            table.unique(['user', 'choice'])

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('poll_responses')
