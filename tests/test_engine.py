import unittest

from notso.core.models import Document
from notso.engine import build_index, search


class EngineTests(unittest.TestCase):
    def test_search_returns_ranked_results(self) -> None:
        documents = [
            Document(doc_id="a", title="A", content="alpha beta gamma", metadata={}),
            Document(doc_id="b", title="B", content="alpha beta", metadata={}),
            Document(doc_id="c", title="C", content="gamma delta", metadata={}),
        ]
        index = build_index(documents)
        results = search(index, "alpha beta", top_k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].doc_id, "b")
        self.assertGreaterEqual(results[0].score, results[1].score)


if __name__ == "__main__":
    unittest.main()
