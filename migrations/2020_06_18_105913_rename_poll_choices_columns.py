from orator.migrations import Migration


class RenamePollChoicesColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('poll_choices') as table:
            table.rename_column('poll', 'poll_id')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('poll_choices') as table:
            table.rename_column('poll_id', 'poll')
