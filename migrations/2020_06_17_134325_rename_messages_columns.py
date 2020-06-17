from orator.migrations import Migration


class RenameMessagesColumns(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('messages') as table:
            table.rename_column('messageId', 'id')
            table.rename_column('authorId', 'author_id')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('messages') as table:
            table.rename_column('id', 'messageId')
            table.rename_column('author_id', 'authorId')
