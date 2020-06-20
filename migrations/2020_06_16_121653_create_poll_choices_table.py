from orator.migrations import Migration


class CreatePollChoicesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('poll_choices') as table:
            table.increments('id')
            table.integer('poll').unsigned()
            table.foreign('poll').references('id').on('polls')
            table.string('reaction', 255)
            table.string('text', 255)

            table.unique(['poll', 'reaction'])

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('poll_choices')
