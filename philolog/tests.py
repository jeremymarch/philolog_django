from django.test import TestCase

from .models import Word
from .views import query_words

# to run tests: python manage.py test


class PhilologTests(TestCase):
    def setUp(self):
        lex = "greatscott"
        definition = "test def"

        lemma = "λ"
        for i in range(0, 500):
            w = Word.objects.create(
                word_id=i,
                lexicon=lex,
                word=lemma,
                sort_key=lemma,
                definition=definition,
            )
            w.save()

        lemma = "ν"
        for i in range(500, 1000):
            w = Word.objects.create(
                word_id=i,
                lexicon=lex,
                word=lemma,
                sort_key=lemma,
                definition=definition,
            )
            w.save()

    def test_query_words(self):
        """Test that the correct number of words are returned and the correct word_id is selected."""

        lex = "greatscott"
        page = 0
        page_size = 100

        word_prefix = "μ"
        selected_id, words = query_words(word_prefix, lex, page, page_size)
        self.assertEqual(
            len(words), 200, "There must be 100 words above and 100 words below prefix"
        )
        self.assertEqual(selected_id, 500)

        word_prefix = "λ"
        selected_id, words = query_words(word_prefix, lex, page, page_size)
        self.assertEqual(len(words), 100, "There must be 100 words below prefix")
        self.assertEqual(selected_id, 0)

        word_prefix = "ν"
        selected_id, words = query_words(word_prefix, lex, page, page_size)
        self.assertEqual(
            len(words), 200, "There must be 100 words above and 100 words below prefix"
        )
        self.assertEqual(selected_id, 500)

        word_prefix = "ξ"
        selected_id, words = query_words(word_prefix, lex, page, page_size)
        self.assertEqual(len(words), 100, "There must be 100 words above prefix")
        self.assertEqual(selected_id, 500)
