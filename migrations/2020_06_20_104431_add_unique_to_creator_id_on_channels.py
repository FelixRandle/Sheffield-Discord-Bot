from orator.migrations import Migration


class AddUniqueToCreatorIdOnChannels(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('channels') as table:
            table.big_integer('creator_id').unique().change()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('channels') as table:
            table.drop_unique('channels_creator_id_unique')
