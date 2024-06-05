import pathlib
TEST_TMP_DIR = pathlib.Path(pathlib.Path(__file__).parent.resolve(), "tmp")

if not TEST_TMP_DIR.exists():
    # broad permission to allow manual removal, just in case...
    TEST_TMP_DIR.mkdir(mode=0o777, parents = True)
