import json
from _collections_abc import MutableMapping
from typing import Any, Iterator
from typing import Hashable, Sequence
from app.models.model_baseclasses import EntityABC, EntityType, GenericRepository, generic_entity_filter_func

class JSONStorage(MutableMapping):
    """A Dict-like object linked to a JSON file.

    The object is not automatically synced with a file, so you have to manually call write_store()
    to commit all changes to the external JSON file.
    """
    def __init__(self, json_file, encoder: json.JSONEncoder = None, decoder: json.JSONDecoder = None):
        self._store = {}
        self._file = json_file
        self.encoder = encoder
        self.decoder = decoder
        self.load_store()

    def load_store(self):
        """(re)-loads this storage from the linked JSON file
        """
        with open(self._file, "r", encoding='utf8') as json_file:
            json_str = json_file.read()
            self._store = json.loads(json_str, cls=self.decoder) if len(json_str) else {}

    def write_store(self):
        """Dumps this storage to its linked JSON file.
        """
        with open(self._file, "w", encoding="utf8") as json_file:
            json.dump(self._store, json_file, cls=self.encoder, indent=1, ensure_ascii=False)
    
    def __getitem__(self, key: Any) -> Any:
        return self._store.__getitem__(key)
    
    def __setitem__(self, key: Any, value: Any) -> None:
        self._store.__setitem__(key, value)
    
    def __delitem__(self, key: Any) -> None:
        self._store.__delitem__(key)
    
    def __iter__(self) -> Iterator:
        return self._store.__iter__()

    def __len__(self) -> int:
        return self._store.__len__()

class JSONRepository(GenericRepository[EntityType]):
    """Generic implementation of a Repository that retrieves and writes data from a JSON file.
    """
    def __init__(self, file, encoder, decoder):
        self._changes = []
        self._store = JSONStorage(json_file= file, encoder = encoder, decoder= decoder)

    def commit_changes(self):
        if len(self._changes):
            self._store.write_store()
            self._changes = []

    def add(self, entity: EntityType):
        if not entity.id():
            raise KeyError('Missing Entity ID')
        if entity.id() in self._store:
            raise KeyError('Duplicate Entity ID')
        self._store[entity.id()] = entity
        self._changes.append(('add', entity.id()))
    
    def update(self, entity: EntityType):
        if not entity.id() in self._store:
            self.add(entity)
        else:
            self._changes.append('update', entity.id())

    def delete(self, key: Hashable = None, **conditions):
        if key is not None:
            del self._store[key]
            self._changes.append('delete', key)
        elif len(conditions) > 0:
            for item in self.find_many(**conditions):
                self.delete(item.id())

    def find_by_id(self, id: Hashable) -> EntityType:
        return self._store.get(id)

    def list_all(self) -> Sequence[EntityType]:
        return list(self._store.values())

    def find_many(self, **filters) -> Sequence[EntityType]:
        if not len(filters):
            return self.list_all()
        return list(generic_entity_filter_func(**filters), self._store.values())
