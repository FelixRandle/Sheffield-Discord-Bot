from orator.migrations import Migration


class RenamePollResponseColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('poll_responses') as table:
            table.rename_column('choice', 'choice_id')
            table.rename_column('user', 'user_id')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('poll_responses') as table:
            table.rename_column('choice_id', 'choice')
            table.rename_column('user_id', 'user')
