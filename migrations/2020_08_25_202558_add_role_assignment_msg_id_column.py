from orator.migrations import Migration


class AddRoleAssignmentMsgIdColumn(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('guilds') as table:
            table.big_integer('role_assignment_msg_id').unique()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('guilds') as table:
            table.drop_unique('role_assignment_msg_id_unique')
            table.drop_column('role_assignment_msg_id')
