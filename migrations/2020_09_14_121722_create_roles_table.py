from orator.migrations import Migration


class CreateRolesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('roles') as table:
            table.increments('id')
            table.string('name')
            table.big_integer('guild_id')
            table.foreign('guild_id').references('id').on('guilds')
            table.big_integer('role_id')
            table.big_integer('created_by')
            table.foreign('created_by').references('id').on('users')
            table.boolean('is_locked').default(False)

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('roles')
