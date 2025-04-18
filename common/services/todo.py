from common.repositories.factory import RepositoryFactory, RepoType
from common.models.todo import Todo

class TodoListService:
   
    def __init__(self, config):
        self.config = config
        self.repository_factory = RepositoryFactory(config)
        self.todo_repo = self.repository_factory.get_repository(RepoType.TODO)
    
    def get_todo_list_item(self, entity_id):
        """Get a todo item by its ID."""
        return self.todo_repo.get_one({"entity_id": entity_id})
        
    def get_todo_list(self, person_id, filter_type="all"):
        """Get todo list with optional filtering."""
        filters = {"person_id": person_id, "active": True}
        if filter_type in ["completed", "active"]:
            filters["is_completed"] = (filter_type == "completed")
        todos = self.todo_repo.get_many(filters)
        return sorted(todos, key=lambda x: x.position)

    def create_todo_list_item(self, person_id, title):
        """Create a new todo item."""
        todos = self.get_todo_list(person_id, "all")
        todos = sorted(todos, key=lambda x: x.position)
        
        for todo in todos:
            todo.position += 1
            self.todo_repo.save(todo)
        
        todo = Todo(
            person_id=person_id, 
            title=title,
            position=0  
        )
        todo.prepare_for_save(changed_by_id=person_id)
        return self.todo_repo.save(todo)

    def update_todo_list_item(self, entity_id, title, is_completed, position=None):
        """Update a todo item."""
        todo = self.get_todo_list_item(entity_id)
        todo.title = title
        todo.is_completed = is_completed
        if position is not None:
            todo.position = position
        return self.todo_repo.save(todo)

    def update_todo_list_item_status(self, entity_id):
        """Update completion status of a todo item."""
        todo = self.get_todo_list_item(entity_id)
        todo.is_completed = not todo.is_completed
        return self.todo_repo.save(todo)

    def mark_all_todo_list(self, person_id, status):
        """Mark all todo items as completed or active."""
        todos = self.get_todo_list(person_id, "active" if status == "completed" else "completed")
        for todo in todos:
            todo.is_completed = (status == "completed")
            self.todo_repo.save(todo)
            
    def delete_todo_list_item(self, todo_id):
        """Delete a todo item."""
        todo = self.get_todo_list_item(todo_id)
        self.todo_repo.delete(todo)

    def delete_completed_todo_list(self, person_id):
        """Delete all completed todo items."""
        completed_todos = self.get_todo_list(person_id, "completed")
        for todo in completed_todos:
            self.todo_repo.delete(todo)