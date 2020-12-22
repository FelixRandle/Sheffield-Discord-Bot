from orator.migrations import Migration


class RenameCompscessionsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        self.schema.rename("compscessions", "compfessions")

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.rename("compfessions", "compscessions")
