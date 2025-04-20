revision = "0000000007"
down_revision = "0000000006"

def upgrade(migration):
    # Update positions for existing todos
    migration.alter_table(
        "todo",
        """
        UPDATE todo t
        SET position = subquery.new_position
        FROM (
            SELECT entity_id, 
                   ROW_NUMBER() OVER (ORDER BY created_on) - 1 as new_position
            FROM todo
            WHERE active = true
        ) AS subquery
        WHERE t.entity_id = subquery.entity_id
        """
    )

    # Update audit table to match
    migration.alter_table(
        "todo_audit",
        """
        UPDATE todo_audit t
        SET position = subquery.new_position
        FROM (
            SELECT entity_id, 
                   ROW_NUMBER() OVER (ORDER BY created_on) - 1 as new_position
            FROM todo
            WHERE active = true
        ) AS subquery
        WHERE t.entity_id = subquery.entity_id
        """
    )

    migration.update_version_table(version=revision)

def downgrade(migration):
    # Reset positions to 0 in both tables
    migration.alter_table("todo", 'UPDATE todo SET position = 0')
    migration.alter_table("todo_audit", 'UPDATE todo_audit SET position = 0')
    
    migration.update_version_table(version=down_revision) 