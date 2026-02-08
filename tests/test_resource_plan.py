import unittest

from notso.core.models import Document
from notso.engine import build_index, search_with_limits
from notso.resource_plan import ResourceGuard, ResourceLimits, plan_term_blocks


class ResourcePlanTests(unittest.TestCase):
    def test_plan_term_blocks_orders_by_idf(self) -> None:
        terms = ["alpha", "beta", "alpha", "gamma"]
        idf_lookup = {"alpha": 1.0, "beta": 3.0, "gamma": 2.0}
        limits = ResourceLimits(max_query_terms=2, term_block_size=1)

        blocks = plan_term_blocks(terms, idf_lookup, limits)

        self.assertEqual(blocks, [["beta"], ["gamma"]])

    def test_resource_guard_stops_on_time(self) -> None:
        ticks = [100.0, 100.2]

        def fake_clock() -> float:
            return ticks.pop(0)

        limits = ResourceLimits(max_seconds=0.1)
        guard = ResourceGuard(limits, clock=fake_clock)
        guard.start()

        reason = guard.checkpoint(docs_processed=0, terms_processed=0)
        self.assertIsNotNone(reason)
        self.assertEqual(reason.reason, "max_seconds")

    def test_search_with_limits_stops_on_doc_budget(self) -> None:
        documents = [
            Document(doc_id="a", title="A", content="alpha beta gamma", metadata={}),
            Document(doc_id="b", title="B", content="alpha beta", metadata={}),
        ]
        index = build_index(documents)
        limits = ResourceLimits(max_documents=1)

        results, reason = search_with_limits(index, "alpha beta", top_k=5, limits=limits)

        self.assertIsNotNone(reason)
        self.assertEqual(reason.reason, "max_documents")
        self.assertLessEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
