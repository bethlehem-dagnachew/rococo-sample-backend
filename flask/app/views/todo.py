from flask_restx import Namespace, Resource
from flask import request
from app.helpers.response import (
    get_success_response,
    get_failure_response,
    parse_request_body,
    validate_required_fields,
)
from app.helpers.decorators import login_required
from common.app_config import config
from common.services.todo import TodoListService

todo_api = Namespace("todo", description="Todo List APIs")


class BaseTodoResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.todo_service = TodoListService(config)


@todo_api.route("")
class Todos(BaseTodoResource):
    @login_required()
    def get(self, person):
        """Get all todos for the current user with optional filtering."""
        filter_type = request.args.get("filter", "all")  
        todos = self.todo_service.get_todo_list(person.entity_id, filter_type)
        return get_success_response(todos=[todo.as_dict() for todo in todos])

    @login_required()
    @todo_api.expect(
        {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
            },
        }
    )
    def post(self, person):
        """Create a new task."""
        parsed_body = parse_request_body(request, ["title"])
        validate_required_fields(parsed_body)

        todo = self.todo_service.create_todo_list_item(
            person_id=person.entity_id,
            title=parsed_body["title"],
        )
        return get_success_response(
            todo=todo.as_dict(), 
            message="Task created successfully."
        )

    @login_required()
    def delete(self, person):
        """Delete all completed tasks."""
        self.todo_service.delete_completed_todo_list(person.entity_id)
        return get_success_response(message="All completed tasks deleted successfully.")


@todo_api.route("/<string:entity_id>")
class TodoItem(BaseTodoResource):
    """Endpoints for managing individual todos."""

    @login_required()
    def get(self, entity_id, person):
        """Get a specific todo."""
        todo = self.todo_service.get_todo_list_item(entity_id)
        return get_success_response(todo=todo.as_dict())

    @login_required()
    @todo_api.expect(
        {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "is_completed": {"type": "boolean"},
            },
        }
    )
    def patch(self, entity_id, person):
        """Update a specific task."""
        parsed_body = parse_request_body(request, ["title", "is_completed"])
        validate_required_fields({"title": parsed_body["title"]})

        updated_todo = self.todo_service.update_todo_list_item(
            entity_id=entity_id,
            title=parsed_body["title"],
            is_completed=parsed_body["is_completed"],
        )
        return get_success_response(
            todo=updated_todo.as_dict(), 
            message="Todo List updated successfully."
        )

    @login_required()
    def delete(self, entity_id, person):
        """Delete a specific task."""
        self.todo_service.delete_todo_list_item(entity_id)
        return get_success_response(message="Todo List deleted successfully.")


@todo_api.route("/<string:entity_id>/status")
class TodoStatus(BaseTodoResource):
    """Endpoints for managing todo status."""

    @login_required()
    def put(self, entity_id, person):
        """Change the completion status of a task."""
        updated_todo = self.todo_service.update_todo_list_item_status(entity_id)
        return get_success_response(
            todo=updated_todo.as_dict(),
            message=f"Todo marked as {'completed' if updated_todo.is_completed else 'active'}.",
        )


@todo_api.route("/mark-all")
class MarkAllTodos(BaseTodoResource):
    """Endpoints for bulk todo operations."""

    @login_required()
    @todo_api.expect(
        {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["completed", "active"]},
            },
            "required": ["status"]
        }
    )
    def post(self, person):
        """Mark all todos as completed or active based on the status parameter."""
        parsed_body = parse_request_body(request, ["status"])
        validate_required_fields(parsed_body)

        self.todo_service.mark_all_todo_list(person.entity_id, parsed_body["status"])
        return get_success_response(
            message=f"All todos marked as {parsed_body['status']}"
        )

