"""Regression coverage for decisions and the first employee question."""
import json
import unittest

from app.fx import StubFX
from app.llm import StubLLM
from app.pipeline import Pipeline
from app.publisher import NullPublisher
from app.store import Store
from simulation.replay import LEVELS, ROOT, process_case


class SimulationRegression(unittest.TestCase):
    def test_scenarios_and_one_reply(self):
        for level in LEVELS:
            expenses = json.loads((ROOT / f"{level}.json").read_text(encoding="utf-8"))
            keys = json.loads((ROOT / f"{level}-key.json").read_text(encoding="utf-8"))
            self.assertEqual([e["id"] for e in expenses], [k["id"] for k in keys])
            pipe = Pipeline(llm=StubLLM(), fx=StubFX(), publisher=NullPublisher(), store=Store(), write_logs=False)
            self.addCleanup(pipe.store.db.close)
            for expense, key in zip(expenses, keys):
                with self.subTest(level=level, expense=expense["id"]):
                    row = process_case(pipe, expense, key)
                    self.assertEqual(row["issues"], [])
                    self.assertLessEqual(len(row["steps"]), 2)
                    for step in row["steps"]:
                        p = step["payload"]
                        fields = (p.get("question") or {}).get("fields", [])
                        names = [f["name"] for f in fields]
                        self.assertEqual(len(names), len(set(names)))
                        stored = pipe.store.history(expense["id"])[p["decision_version"] - 1]["payload"]
                        self.assertEqual(stored, {k:v for k,v in p.items() if not k.startswith("_post_")})


if __name__ == "__main__":
    unittest.main()
