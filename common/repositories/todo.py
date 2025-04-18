from common.repositories.base import BaseRepository
from common.models.todo import Todo


class TodoListRepository(BaseRepository):
    MODEL = Todo
