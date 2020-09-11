from orator.migrations import Migration


class MakeFieldsNullable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('guilds') as table:
            table.big_integer('registering_id').nullable().change()
            table.big_integer('member_id').nullable().change()
            table.big_integer('role_assignment_msg_id').nullable().change()

    def down(self):
        """
        Revert the migrations.
        """
        with self.db as db:
            db.statement(
                'ALTER TABLE guilds MODIFY registering_id bigint NOT NULL')
            db.statement(
                'ALTER TABLE guilds MODIFY member_id bigint NOT NULL')
            db.statement(
                'ALTER TABLE guilds MODIFY role_assignment_msg_id bigint '
                'NOT NULL')
