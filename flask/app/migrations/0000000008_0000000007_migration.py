revision = "0000000008"
down_revision = "0000000007"

def upgrade(migration):
    # Add position column to todo table
    migration.add_column(
        "todo",
        "position",
        "integer DEFAULT 0"
    )
    
    # Add position column to todo_audit table
    migration.add_column(
        "todo_audit",
        "position",
        "integer DEFAULT 0"
    )
    
    # Add index for better query performance
    migration.add_index("todo", "todo_position_ind", "position")
    
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
    # Drop the position index
    migration.drop_index("todo", "todo_position_ind")
    
    # Drop the position column from todo_audit table
    migration.drop_column("todo_audit", "position")
    
    # Drop the position column from todo table
    migration.drop_column("todo", "position")

    migration.update_version_table(version=down_revision) 