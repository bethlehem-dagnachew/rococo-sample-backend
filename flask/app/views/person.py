from flask_restx import Namespace, Resource
from flask import request
from app.helpers.response import get_success_response, parse_request_body, validate_required_fields
from app.helpers.decorators import login_required
from common.services.person import PersonService
from common.app_config import config

# Create the organization blueprint
person_api = Namespace('person', description="Person-related APIs")


@person_api.route('/me')
class Me(Resource):
    
    @login_required()
    def get(self, person):
        return get_success_response(person=person)

    @login_required()
    @person_api.expect(
        {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"}
            }
        }
    )
    def patch(self, person):
        """Update user profile information."""
        # Parse request body without requiring any fields
        parsed_body = request.get_json() or {}
        
        # At least one field should be provided
        if not any([parsed_body.get("first_name"), parsed_body.get("last_name")]):
            return get_success_response(
                message="No fields to update. Please provide first_name or last_name.",
                status_code=400
            )

        person_service = PersonService(config)
        
        # Update only the provided fields
        if "first_name" in parsed_body:
            person.first_name = parsed_body["first_name"]
        if "last_name" in parsed_body:
            person.last_name = parsed_body["last_name"]

        # Save the updated person
        updated_person = person_service.save_person(person)
        
        return get_success_response(
            person=updated_person,
            message="Profile updated successfully."
        )
