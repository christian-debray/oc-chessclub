"""Base classes for our models.
"""

from typing import TypeVar, Hashable
from abc import ABC, abstractmethod
from _collections_abc import Sequence


class EntityABC(ABC):
    """Interface for all entities handled by our app.
    Entities are unique and have a unique identifier.
    """

    @abstractmethod
    def id(self) -> Hashable:
        pass

    @abstractmethod
    def set_id(self, id: Hashable):
        pass


EntityType = TypeVar('EntityType', bound=EntityABC)


class GenericRepository[EntityType](ABC):
    """Base repository class.

    A repository:
      - encapsulates all CRUD operations
      - acts as an interface between domain and data model

    This base class provides the interface to
    """

    @abstractmethod
    def add(self, entity: EntityType):
        """Add a new entity to this repository and stores the new entity to the underlying storage
        """
        pass

    @abstractmethod
    def update(self, entity: EntityType):
        """Updates an existing entity in the data storage.
        """
        pass

    @abstractmethod
    def delete(self, key: Hashable = None, **conditions: Hashable):
        """Removes (deletes) one or several entities from this repository and its underlying storage.
        """
        pass

    @abstractmethod
    def find_by_id(self, id) -> EntityType:
        pass

    @abstractmethod
    def find_many(self, **filters) -> Sequence[EntityType]:
        """Returns a list of entities.
        Filtering and ordering rules are provided by optional kwargs.
        """
        pass


def generic_entity_filter_func(**filters) -> bool:
    """Utility function to generate filters when searching for entities.

    allows you to filter sequences like so:

        given a list of items: data_list: list[ItemClass]

        ex1 - item property, equity:
            filter(
                generic_entity_filter_func(prop1 = 42),
                data_list)

        ex2 - item property, range:
            filter(
                generic_entity_filter_func(prop1 = lambda x: x > 5 and x < 20),
                data_list)

        ex3 - predicate on whole item:
            filter(
                generic_entity_filter_func(
                    where= lambda t: t.id() != 42 and t.prop1 > 5 and t.prop2 in 'abcdefgh'),
                data_list)
    """
    def filter_func(item):
        def eval_predicate(predicate, value) -> bool:
            """helper : apply predicate to value,
            or test equality with value if predicate is not callable.
            """
            if callable(predicate):
                return predicate(value)
            else:
                return predicate == value

        keep = True
        for field, predicate_or_value in filters.items():
            if not keep:
                break
            if hasattr(item, field):
                #
                # ex1 - equity: find_many(prop1 = 42)
                # ex2 - range: find_many(prop1 = lambda x: x > 5 and x < 20)
                #
                keep = keep and eval_predicate(predicate_or_value, getattr(item, field))
            elif callable(predicate_or_value):
                #
                # ex3 - find_many(where= lambda t: t.id() != 42 and t.prop1 > 5 and t.prop2 in 'abcdefgh')
                #
                keep = keep and predicate_or_value(item)
            else:
                keep = False
        return keep
    return filter_func
