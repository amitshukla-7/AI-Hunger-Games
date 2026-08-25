import os
import pytest

# Ensure tests don't inadvertently write to the real db before fixtures run
os.environ["AIHG_DB_PATH"] = "dummy_path_to_prevent_accidental_writes.db"

import db

@pytest.fixture(autouse=True)
def isolated_db(tmp_path):
    db_file = str(tmp_path / "test_hunger_games.db")
    os.environ["AIHG_DB_PATH"] = db_file
    db.DB_PATH = db_file
    db.init_db()
    yield
