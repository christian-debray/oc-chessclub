"""Base classes for our models.
"""

from typing import TypeVar, Generic, Generator, Hashable
from abc import ABC, abstractmethod
from _collections_abc import Sequence, Mapping

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

if __name__ == "__main__":
    #
    # The code below illustrates how the Repository abstract classes may be used:
    #

    from dataclasses import dataclass
    @dataclass
    class Toto(EntityABC):
        prop1: int
        prop2: str
        _id: Hashable = None

        def id(self):
            return self._id

        def set_id(self, id: Hashable):
            self._id = id

    class TotoRepository(GenericRepository[Toto]):
        """Our implementation of a repository
        """
        def __init__(self):
            self._data = {}
            self._entities: dict[Hashable, Toto] = {}
            self._next_id = 1
        
        def _consume_next_id(self):
            consumed_id = self._next_id
            self._next_id += 1
            return consumed_id
    
        def toto_encoder(self, entity: Toto) -> dict:
            return {
                'id': entity.id(),
                'prop1': entity.prop1,
                'prop2': entity.prop2
            }
        
        def toto_decoder(self, toto_data: dict) -> Toto:
            if toto_data:
                return Toto(toto_data.get('id'), toto_data.get('prop1'), toto_data.get('prop2'))

        def add(self, entity: Toto):
            id = entity.id() or self._consume_next_id()
            if id in self._data:
                raise Exception('Duplicate key')
            if entity.id() != id:
                entity.set_id(id)
            self._data[id] = self.toto_encoder(entity)
            self._entities[id] = entity
        
        def delete(self, key: Hashable = None, **conditions: Hashable):
            if key is not None:
                del self._data[key]
                del self._entities[key]
            elif len(conditions):
                for item in self.list(**conditions):
                    self.delete(item.id())

        def find_by_id(self, id) -> Toto:
            if id not in self._entities:
                entity = self.toto_decoder(self._data.get(id))
                if entity is not None:
                    self._entities[id] = entity
            return self._entities.get(id)

        def find_many(self, **filters) -> Sequence[Toto]:
            if len(filters) == 0:
                return self.list_all()
            else:
                print('filering...')
                return list(filter(generic_entity_filter_func(**filters), self.list_all()))

        def list_all(self) -> list[Toto]:
            """lists all entities
            """
            return [self.find_by_id(ent_id) for ent_id in self._data.keys()]

        def update(self, entity: Toto):
            if not entity.id() or entity.id() not in self._data:
                return self.add(entity)
            self._data[entity.id()] = self.toto_encoder(entity)
            if entity.id() not in self._entities:
                self._entities[entity.id()] = entity
    
    toto_repo = TotoRepository()

    chars = "abcdefghijklmnopqrstuvwxyz"
    for a in range(len(chars)):
        toto_repo.add(Toto(prop1 = a + 100, prop2 = chars[a%26]))
    
    print("All items:")
    for item in toto_repo.find_many():
        print(item)

    print("\nFilter even ranks:")
    for item in toto_repo.find_many(where = (lambda x : x.prop1%2 == 0)):
        print("(even)", item)

    print("\nFilter even ranks among abcdefgh:")
    for item in toto_repo.find_many(prop2 = lambda x : x in 'abcdefgh', where = (lambda x : x.prop1%2 == 0)):
        print("(even8)", item)

    my_toto = toto_repo.find_by_id(20)

    if my_toto:
        print("\nfound #20: ", my_toto)
    else:
        print("\nnot found: ", 20)

    my_toto = toto_repo.find_by_id(42)
    if my_toto:
        print("found #42: ", my_toto)
    else:
        print("\nnot found: #42")

