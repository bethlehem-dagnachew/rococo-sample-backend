from common.repositories import *
from enum import Enum, auto
from rococo.data.postgresql import PostgreSQLAdapter
from rococo.messaging.rabbitmq import RabbitMqConnection
from typing import Optional
from common.app_logger import logger


def get_flask_pooled_db():
    """
    Determine if a Flask app context is available and the flask app context has `pooled_db` extension available

    Returns:
        object: The pooled_db extension if available otherwise None.
    """
    try:
        # Attempt to import Flask and access the current app's context
        from flask import current_app, has_app_context

        # Check if Flask app context is available and the `pooled_db` extension is registered
        if has_app_context():
            pooled_db = current_app.extensions.get("pooled_db")
            if pooled_db:
                return pooled_db
    except (ImportError, AttributeError):
        # ImportError: Flask is not installed
        # AttributeError: `pooled_db` extension is not available
        pass

    return None


class MessageAdapterType(str, Enum):
    RABBITMQ = "rabbitmq"
    SQS = "sqs"

    def __repr__(self):
        return str(self.value)


def get_connection_resolver():
    pooled_db = get_flask_pooled_db()
    if pooled_db:
        return pooled_db.get_connection


def get_connection_closer():
    pooled_db = get_flask_pooled_db()
    if pooled_db:
        return lambda *args, **kwargs: None  # No-op; let Pooled DB handle closing of connection on request teardown.


class RepoType(Enum):

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        """Method for auto-generating Enum values"""
        return name.lower()
    
    PERSON = auto()
    ORGANIZATION = auto()
    EMAIL = auto()
    LOGIN_METHOD = auto()
    PERSON_ORGANIZATION_ROLE = auto()
    TODO = auto()


class RepositoryFactory:

    def __init__(self, config):
        self.config = config

    _repositories = {
        RepoType.PERSON: PersonRepository,
        RepoType.ORGANIZATION: OrganizationRepository,
        RepoType.EMAIL: EmailRepository,
        RepoType.LOGIN_METHOD: LoginMethodRepository,
        RepoType.PERSON_ORGANIZATION_ROLE: PersonOrganizationRoleRepository,
        RepoType.TODO: TodoListRepository
    }

    def get_db_connection(self):
        host = self.config.POSTGRES_HOST
        port = int(self.config.POSTGRES_PORT)
        user = self.config.POSTGRES_USER
        password = self.config.POSTGRES_PASSWORD
        database = self.config.POSTGRES_DB

        return PostgreSQLAdapter(host, port, user, password, database, connection_resolver=get_connection_resolver(), connection_closer=get_connection_closer())

    def _get_rabbitmq_connection(self):
        return RabbitMqConnection(
            host=self.config.RABBITMQ_HOST,
            port=int(self.config.RABBITMQ_PORT),
            username=self.config.RABBITMQ_USER,
            password=self.config.RABBITMQ_PASSWORD,
            virtual_host=self.config.RABBITMQ_VIRTUAL_HOST
        )

    def get_adapter(self):
        return self._get_rabbitmq_connection()

    def get_repository(self, repo_type: RepoType, person_id=None, message_queue_name: str = ""):
        adapter = self.get_db_connection()
        message_adapter = self.get_adapter()
        repo_class = self._repositories.get(repo_type)

        if repo_class:
            import threading
            return repo_class(adapter, message_adapter, message_queue_name, person_id)

        raise ValueError(f"No repository found with the name '{repo_type}'")
