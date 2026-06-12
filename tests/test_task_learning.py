import tempfile
import unittest
from pathlib import Path

import config
from core.learning import LearningEngine
from core.task_manager import TaskManager


class TaskLearningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.original_paths = {
            "tasks_file": config.settings.tasks_file,
            "preferences_file": config.settings.preferences_file,
            "usage_db_file": config.settings.usage_db_file,
        }

        object.__setattr__(config.settings, "tasks_file", root / "tasks.json")
        object.__setattr__(config.settings, "preferences_file", root / "preferences.json")
        object.__setattr__(config.settings, "usage_db_file", root / "usage.sqlite3")

    def tearDown(self) -> None:
        for key, value in self.original_paths.items():
            object.__setattr__(config.settings, key, value)
        self.tmp.cleanup()

    def test_task_lifecycle(self) -> None:
        manager = TaskManager()
        task = manager.create("demo")
        manager.complete(task.id)
        self.assertTrue(manager.list()[0].completed)

    def test_learning_preferences_and_suggestions(self) -> None:
        engine = LearningEngine()
        engine.set_preference("mode", "focus")
        self.assertEqual(engine.get_preference("mode"), "focus")
        engine.record_action("task.create")
        self.assertTrue(engine.suggestions())
