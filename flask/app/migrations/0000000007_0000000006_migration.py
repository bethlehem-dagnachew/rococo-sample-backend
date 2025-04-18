revision = "0000000007"
down_revision = "0000000006"

def upgrade(migration):
    # Update existing records with sequential positions
    migration.execute_sql("""
        WITH numbered_todos AS (
            SELECT entity_id, ROW_NUMBER() OVER (ORDER BY created_on) - 1 as new_position
            FROM todo
            WHERE active = true
        )
        UPDATE todo
        SET position = numbered_todos.new_position
        FROM numbered_todos
        WHERE todo.entity_id = numbered_todos.entity_id
    """)

    migration.update_version_table(version=revision)

def downgrade(migration):
    # Reset positions to 0
    migration.execute_sql("""
        UPDATE todo SET position = 0;
        UPDATE todo_audit SET position = 0;
    """)

    migration.update_version_table(version=down_revision) 