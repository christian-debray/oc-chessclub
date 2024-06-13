import json
from _collections_abc import MutableMapping
from typing import Any, Iterator
from typing import Hashable, Sequence
from app.models.model_baseclasses import EntityABC, EntityType, GenericRepository, generic_entity_filter_func
from pathlib import Path

class JSONStorage(MutableMapping):
    """A Dict-like object linked to a JSON file.

    The object is not automatically synced with a file, so you have to manually call write_store()
    to commit all changes to the external JSON file.
    """
    def __init__(self, json_file, encoder: json.JSONEncoder = None, decoder: json.JSONDecoder = None):
        self._store = {}
        self._file = Path(json_file).resolve()
        self.encoder = encoder
        self.decoder = decoder
        if self._file.exists():
            self.load_store()
        else:
            # check now we have proper access to the file:
            self._file.touch(mode= 0o777)
            self._file.unlink()

    def load_store(self):
        """(re)-loads this storage from the linked JSON file
        """
        with open(self._file, "r", encoding='utf8') as json_file:
            json_str = json_file.read()
            self._store = json.loads(json_str, cls=self.decoder) if len(json_str) else {}

    def write_store(self):
        """Dumps this storage to its linked JSON file.
        """
        if not self._file.exists():
            self._file.touch(mode= 0o777)
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

    The data is stored as a dictionnary to the JSON file.
    The JSON data is indexed by the entity ids, converted as strings.

    WARNING: For now, we don't support concurrent access of the data in the file...
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
        if str(entity.id()) in self._store:
            raise KeyError('Duplicate Entity ID')
        self._store[str(entity.id())] = entity
        self._changes.append(('add', str(entity.id())))
    
    def update(self, entity: EntityType):
        if not str(entity.id()) in self._store:
            self.add(entity)
        else:
            self._store[entity.id()] = entity
            self._changes.append(('update', str(entity.id())))

    def delete(self, key: Hashable = None, **conditions):
        if key is not None:
            del self._store[str(key)]
            self._changes.append(('delete', str(key)))
        elif len(conditions) > 0:
            for item in self.find_many(**conditions):
                self.delete(item.id())

    def find_by_id(self, id: Hashable) -> EntityType:
        return self._store.get(str(id))

    def list_all(self) -> Sequence[EntityType]:
        return list(self._store.values())

    def find_many(self, **filters) -> Sequence[EntityType]:
        if not len(filters):
            return self.list_all()
        return list(filter(generic_entity_filter_func(**filters), self._store.values()))
