from orator.migrations import Migration


class AddApprovedCompfessionId(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('compfessions') as table:
            table.big_integer('approved_id').nullable()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('compfessions') as table:
            table.drop_column('approved_id')
