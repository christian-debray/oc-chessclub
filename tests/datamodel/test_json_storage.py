import unittest
import pathlib
import tests
from app.adapters.json_storage import JSONRepository, JSONStorage
import json

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

if __name__ == "__main__":
    unittest.main()