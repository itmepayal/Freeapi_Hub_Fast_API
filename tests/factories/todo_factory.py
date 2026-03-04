import factory
from faker import Faker
from app.api.v1.todos.models import Todo
from app.api.v1.todos.enums import TodoStatus, TodoPriority

fake = Faker()

class TodoFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Todo
        sqlalchemy_session_persistence = "commit"

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.text())
    status = TodoStatus.pending
    priority = TodoPriority.medium