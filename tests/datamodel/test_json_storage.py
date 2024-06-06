from typing import Hashable
import unittest
import pathlib
import tests
from app.adapters.json_storage import JSONRepository, JSONStorage
import json
from dataclasses import dataclass
from app.models.model_baseclasses import EntityABC
from datetime import date

class TestJSONStorage(unittest.TestCase):
    """Test the JSONStorage.
    
    Writes to the tests/tmp directory.
    Should clean up the files created and written during the tests.
    """
    def setUp(self) -> None:
        self.json_file = pathlib.Path(tests.TEST_TMP_DIR, "test_json_storage.json")
        self.json_file.touch(mode=0o666)
        self.initial_test_data = {
            'test_int': 12345678,
            'test_float': 12.345678,
            'test_str': "The quick brown fox\njumped over\n\tthe lazy dog",
            'test_list': list(range(12)),
            'test_dict': {'greeting': "hello", 'person': "Tom"}
        }
        with open(self.json_file, "w") as f:
            json.dump(self.initial_test_data, f)
        self.store = JSONStorage(self.json_file)
    
    def tearDown(self) -> None:
        self.json_file.unlink(missing_ok= True)

    def test_dict_methods(self):
        self.assertEqual(self.store.get('test_int'), self.initial_test_data['test_int'])
        for k in self.store:
            self.assertIn(k, self.store)
            self.assertEqual(self.initial_test_data[k], self.store.get(k))
        del self.store['test_int']

    def test_load_store(self):
        for k, v in self.initial_test_data.items():
            self.assertIn(k, self.store)
            self.assertEqual(v, self.store[k])

    def test_write_store(self):
        self.store['test_int'] = 12
        self.store['test_str'] = "foo bar"
        self.store['another_test_str'] = "done"
        del self.store['test_float']
        self.store.write_store()
        with open(self.json_file, "r") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['test_int'], 12)
        self.assertEqual(data['test_str'], "foo bar")
        self.assertEqual(data['another_test_str'], "done")
        self.assertNotIn('test_float', data)

@dataclass
class DummyEntity(EntityABC):
    """Entity class to conduct our tests
    """
    _id: int
    name: str
    weight: float
    coords: tuple[float, float]
    created: date

    def id(self):
        return self._id
    
    def set_id(self, id: Hashable):
        self._id = id

class DummyJSONEncoder(json.JSONEncoder):
    """Encode DummyEntity object to JSON
    """
    def default(self, o: DummyEntity):
        if isinstance(o, DummyEntity):
            return {
                'dummy_id' : o.id(),
                'name' : o.name,
                'weight': o.weight,
                'coords': list(o.coords),
                'created': o.created.isoformat()
            }
        else:
            return super().default(o)

class DummyJSONDecoder(json.JSONDecoder):
    """Decode DummyEntity object from JSON
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.obj_hook, *args, **kwargs)

    def obj_hook(self, dct):
        if 'dummy_id' not in dct:
            return dct
        return DummyEntity(
            _id= dct['dummy_id'],
            name= dct['name'],
            weight= dct['weight'],
            coords= tuple(dct['coords']),
            created= date.fromisoformat(dct['created'])
        )

class TestJSONRepository(unittest.TestCase):
    """Test the JSONRepository
    """
    def setUp(self) -> None:
        self.dummy_list = [
            DummyEntity(_id=12, name="Tom", weight=67.76, coords=(50.234, 12.1134552), created= date(2024, 5, 12)),
            DummyEntity(_id=13, name="Léna", weight=57.76, coords=(40.345, 13.567977), created= date(2024, 4, 13)),
            DummyEntity(_id=14, name="Möîça'grà", weight=672.76, coords=(30.234, 45.1134552), created= date(2024, 3, 14)),
            DummyEntity(_id=15, name="Toto", weight=85.0, coords=(30.234, 45.1134552), created= date(2024, 2, 15)),
            DummyEntity(_id=16, name="Machin", weight=34.13, coords=(20.23, 12.134), created= date(2024, 1, 16)),
            DummyEntity(_id=17, name="Myia", weight=3.76, coords=(55.12, 12.1552), created= date(2023, 12, 17))
        ]
        self.test_file = pathlib.Path(tests.TEST_TMP_DIR, "dummy_entities.json")
        self.test_file.touch(mode=0o666)
        self.repo = JSONRepository(self.test_file, encoder = DummyJSONEncoder, decoder= DummyJSONDecoder)
    
    def tearDown(self) -> None:
        self.test_file.unlink(missing_ok= True)

    def test_add(self):
        for entity in self.dummy_list:
            self.repo.add(entity)
            #
            # Out of unit test scope:
            # JSONRepository._store is part of the implementation, not the interface...
            # But how could I possibly test this method
            # without looking inside the repo's storage ?
            #
            self.assertIn(str(entity.id()), self.repo._store)
        self.assertEqual(len(self.repo._store), len(self.dummy_list))

    def test_find_by_id(self):
        self.test_add()
        dummy = self.repo.find_by_id(self.dummy_list[0].id())
        self.assertIsNotNone(dummy)
        self.assertEqual(dummy, self.dummy_list[0])

    def test_commit_changes(self):
        self.test_add()
        self.repo.commit_changes()
        with open(self.test_file, "r") as fh:
            data = json.load(fh, cls= DummyJSONDecoder)
        self.assertEqual(len(data), len(self.dummy_list))
        self.assertIsInstance(data, dict)
        for k, v in data.items():
            self.assertIsInstance(v, DummyEntity)
            self.assertIn(v, self.dummy_list)
            self.assertEqual(int(k), v.id())

    def test_update(self):
        dummy = self.dummy_list[0]
        self.repo.add(dummy)
        dummy.weight = 42.42
        self.repo.update(dummy)
        self.repo.commit_changes()
        other_repo = JSONRepository(self.test_file, encoder= DummyJSONEncoder, decoder=DummyJSONDecoder)
        dummy_duplicate = other_repo.find_by_id(dummy.id())
        self.assertEqual(dummy_duplicate, dummy)

    def test_delete(self):
        self.test_add()
        self.repo.delete(self.dummy_list[0].id())
        self.assertIsNone(self.repo.find_by_id(self.dummy_list[0].id()))
        self.repo.commit_changes()
        other_repo = JSONRepository(self.test_file, encoder= DummyJSONEncoder, decoder=DummyJSONDecoder)
        self.assertIsNone(other_repo.find_by_id(self.dummy_list[0].id()))

    def test_find_by(self):
        self.test_add()
        self.assertIsNotNone(self.repo.find_by_id(self.dummy_list[0].id()))
        # test there are no implicit conversions when checking the id:
        id_str = f"0{self.dummy_list[0].id()}"
        self.assertIsNone(self.repo.find_by_id(id_str))
        self.assertEqual(12.0, self.dummy_list[0].id())
        self.assertIsNone(self.repo.find_by_id(12.0))

    def test_find_many(self):
        dummy_list = [
            DummyEntity(_id=12, name="Tom", weight=67.76, coords=(50.234, 12.1134552), created= date(2024, 5, 12)),
            DummyEntity(_id=13, name="Léna", weight=57.76, coords=(40.345, 13.567977), created= date(2024, 4, 13)),
            DummyEntity(_id=14, name="Möîça'grà", weight=672.76, coords=(30.234, 45.1134552), created= date(2024, 3, 14)),
            DummyEntity(_id=15, name="Toto", weight=85.0, coords=(30.234, 45.1134552), created= date(2024, 2, 15)),
            DummyEntity(_id=16, name="Machin", weight=34.13, coords=(20.23, 12.134), created= date(2024, 1, 16)),
            DummyEntity(_id=17, name="Myia", weight=3.76, coords=(55.12, 12.1552), created= date(2023, 12, 17))
        ]
        for d in dummy_list:
            self.repo.add(d)
        filtered_by_properties = self.repo.find_many(
            coords= lambda x_coords: 12 == round(x_coords[1]),
            created= lambda x_created: x_created.year >= 2024
            )
        
        self.assertListEqual(filtered_by_properties, [self.dummy_list[0], self.dummy_list[4]])
        filtered_by_func = self.repo.find_many(
            where = lambda x: round(x.coords[1]) == 12 and x.created.year >= 2024
        )
        self.assertListEqual(filtered_by_func, [self.dummy_list[0], self.dummy_list[4]])
        self.assertListEqual(self.repo.find_many(weight= 3.1416), [])
