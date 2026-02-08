import unittest

from notso.engine import Document, build_index, search


class EngineTests(unittest.TestCase):
    def test_search_returns_ranked_results(self) -> None:
        documents = [
            Document(doc_id="a", text="alpha beta gamma"),
            Document(doc_id="b", text="alpha beta"),
            Document(doc_id="c", text="gamma delta"),
        ]
        index = build_index(documents)
        results = search(index, "alpha beta", top_k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].doc_id, "b")
        self.assertGreaterEqual(results[0].score, results[1].score)


if __name__ == "__main__":
    unittest.main()
