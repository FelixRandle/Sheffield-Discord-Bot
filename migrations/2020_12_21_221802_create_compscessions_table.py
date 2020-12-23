from orator.migrations import Migration


class CreateCompscessionsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('compscessions') as table:
            table.increments('id')
            table.string('confession')
            table.boolean('approved').default(False)
            table.big_integer('approved_by').nullable()
            table.foreign('approved_by').references('id').on('users')
            table.timestamp('created_at')
            table.timestamp('updated_at')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('compscessions')
