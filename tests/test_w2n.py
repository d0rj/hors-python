import unittest

from hors.utils.w2n import replace_word_nums_safe


class BaseW2N(unittest.TestCase):

    def test_no_dates(self):
        phrase = 'в день, какой неведомо, в никаком году'
        result = replace_word_nums_safe(phrase)
        self.assertEqual(phrase, result)

    def test_one_word(self):
        result = replace_word_nums_safe('встретимся пятого числа')
        self.assertEqual(result, 'встретимся 5 числа')

    def test_two_words(self):
        result = replace_word_nums_safe('встретимся двадцать второго числа')
        self.assertEqual(result, 'встретимся 22 числа')

    def test_multiple_numbers(self):
        result = replace_word_nums_safe('встретимся двадцать второго или пятого числа')
        self.assertEqual(result, 'встретимся 22 или 5 числа')


if __name__ == '__main__':
    unittest.main()
