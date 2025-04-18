revision = "0000000006"
down_revision = "0000000005"

def upgrade(migration):
    # Create the todo table
    migration.create_table(
        "todo",
        """
            "entity_id" varchar(32) NOT NULL,
            "version" varchar(32) NOT NULL,
            "previous_version" varchar(32) DEFAULT '00000000000000000000000000000000',
            "active" boolean DEFAULT true,
            "changed_by_id" varchar(32) DEFAULT NULL,
            "changed_on" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            "person_id" varchar(32) NOT NULL,
            "title" varchar(255) NOT NULL,
            "is_completed" boolean DEFAULT false,
            "created_on" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            "position" integer DEFAULT 0,
            PRIMARY KEY ("entity_id")
        """
    )
    
    # Add indexes for better query performance
    migration.add_index("todo", "todo_person_id_ind", "person_id")
    migration.add_index("todo", "todo_is_completed_ind", "is_completed")
    migration.add_index("todo", "todo_position_ind", "position")
    
    # Create the todo_audit table for tracking changes
    migration.create_table(
        "todo_audit",
        """
            "entity_id" varchar(32) NOT NULL,
            "version" varchar(32) NOT NULL,
            "previous_version" varchar(32) DEFAULT '00000000000000000000000000000000',
            "active" boolean DEFAULT true,
            "changed_by_id" varchar(32) DEFAULT NULL,
            "changed_on" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            "person_id" varchar(32) NOT NULL,
            "title" varchar(255) NOT NULL,
            "is_completed" boolean DEFAULT false,
            "created_on" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            "position" integer DEFAULT 0,
            PRIMARY KEY ("entity_id", "version")
        """
    )

    migration.update_version_table(version=revision)

def downgrade(migration):
    # Drop the audit table first (due to foreign key constraints)
    migration.drop_table(table_name="todo_audit")
    # Drop the main todo table
    migration.drop_table(table_name="todo")

    migration.update_version_table(version=down_revision) 