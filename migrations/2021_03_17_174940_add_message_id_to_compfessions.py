from orator.migrations import Migration


class AddMessageIdToCompfessions(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('compfessions') as table:
            table.big_integer('message_id').nullable()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('compfessions') as table:
            table.drop_column('message_id')
