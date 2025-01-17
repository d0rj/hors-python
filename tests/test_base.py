import unittest
from datetime import datetime

from hors import process_phrase
from hors.models.parser_models import DateTimeTokenType


class BaseHorsTests(unittest.TestCase):

    def test_no_dates(self):
        result = process_phrase('в день, какой неведомо, в никаком году')
        self.assertEqual(0, len(result.dates))

    def test_january(self):
        starting_point = datetime(2019, 10, 13)
        result = process_phrase('десятого января событие', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(10, date.date_from.day)
        self.assertEqual(1, date.date_from.month)
        self.assertEqual(2020, date.date_from.year)

    def test_time_period_before_day(self):
        starting_point = datetime(2019, 10, 13)
        result = process_phrase('с пяти до семи вечера в понедельник будет событие', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(17, date.date_from.hour)
        self.assertEqual(19, date.date_to.hour)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(14, date.date_to.day)

    def test_time_period_simple(self):
        starting_point = datetime(2019, 10, 13)
        result = process_phrase('с десяти до тринадцати событие', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(10, date.date_from.hour)
        self.assertEqual(13, date.date_to.hour)

    def test_daytime(self):
        starting_point = datetime(2019, 10, 14)
        result = process_phrase('Завтра в час обед и продлится он час с небольшим', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(13, date.date_from.hour)

    def test_nighttime(self):
        starting_point = datetime(2020, 1, 1)
        result = process_phrase(
            'Завтра в два ночи полнолуние, а затем в три часа ночи новолуние и наконец в двенадцати часов ночи игра.',
            starting_point)
        self.assertEqual(3, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(2, date.date_from.hour)

        date = result.dates[1]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(3, date.date_from.hour)

        date = result.dates[2]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(0, date.date_from.hour)
        self.assertEqual(1, date.date_from.day)

    def test_long_period(self):
        starting_point = datetime(2019, 10, 14)
        result = process_phrase(
            'С вечера следующей среды до четверти десяти утра понедельника в декабре можно будет наблюдать снег',
            starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(23, date.date_from.day)
        self.assertEqual(10, date.date_from.month)
        self.assertEqual(2, date.date_to.day)
        self.assertEqual(12, date.date_to.month)
        self.assertEqual(9, date.date_to.hour)
        self.assertEqual(15, date.date_to.minute)

    def test_collapse_complex(self):
        starting_point = datetime(2019, 10, 13)
        result = process_phrase('В понедельник в девять и десять вечера', starting_point)
        self.assertEqual(2, len(result.dates))

        date = result.dates[0]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(21, date.date_from.hour)

        date = result.dates[1]
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(22, date.date_from.hour)

        result = process_phrase('В понедельник в десять и девять вечера', starting_point)
        self.assertEqual(2, len(result.dates))

        date = result.dates[0]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(22, date.date_from.hour)

        date = result.dates[1]
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(21, date.date_from.hour)

    def test_multiple_simple(self):
        starting_point = datetime(2019, 10, 13)
        result = process_phrase(
            'Позавчера в шесть тридцать состоялось совещание, а завтра днём будет хорошая погода.',
            starting_point)
        self.assertEqual(2, len(result.dates))

        date = result.dates[0]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(11, date.date_from.day)
        self.assertEqual(6, date.date_from.hour)
        self.assertEqual(30, date.date_from.minute)

        date = result.dates[1]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(True, date.has_time)

    def test_collapse_direction(self):
        starting_point = datetime(2019, 10, 15)
        strings = [
            'В следующем месяце с понедельника буду ходить в спортзал!',
            'С понедельника в следующем месяце буду ходить в спортзал!',
        ]
        for s in strings:
            result = process_phrase(s, starting_point)
            self.assertEqual(1, len(result.dates))

            date = result.dates[0]
            self.assertEqual(2019, date.date_from.year)
            self.assertEqual(4, date.date_from.day)
            self.assertEqual(11, date.date_from.month)

    def test_weekday(self):
        starting_point = datetime(2019, 10, 13)
        result = process_phrase('В следующем месяце во вторник состоится событие', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(5, date.date_from.day)
        self.assertEqual(11, date.date_from.month)

        result = process_phrase('Через месяц во вторник состоится событие', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(12, date.date_from.day)
        self.assertEqual(11, date.date_from.month)

    def test_time_after_day(self):
        starting_point = datetime(2019, 10, 8)
        result = process_phrase('в четверг шестнадцать ноль ноль будет событие', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(True, date.has_time)
        self.assertEqual(16, date.date_from.hour)
        self.assertEqual(10, date.date_from.day)

    def test_time_period(self):
        starting_point = datetime(2019, 9, 7)
        result = process_phrase('В следующий четверг с девяти утра до шести вечера важный экзамен!', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(True, date.has_time)
        self.assertEqual(9, date.date_from.hour)
        self.assertEqual(12, date.date_from.day)
        self.assertEqual(9, date.date_from.month)
        self.assertEqual(18, date.date_to.hour)
        self.assertEqual(12, date.date_to.day)
        self.assertEqual(9, date.date_to.month)
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(2019, date.date_to.year)

    def test_complex_period(self):
        starting_point = datetime(2019, 7, 7)
        result = process_phrase('хакатон с двенадцати часов восемнадцатого сентября до двенадцати часов двадцатого сентября', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(True, date.has_time)
        self.assertEqual(12, date.date_from.hour)
        self.assertEqual(18, date.date_from.day)
        self.assertEqual(9, date.date_from.month)
        self.assertEqual(12, date.date_to.hour)
        self.assertEqual(20, date.date_to.day)
        self.assertEqual(9, date.date_to.month)
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(2019, date.date_to.year)

    def test_time_before_day(self):
        starting_point = datetime(2019, 9, 7)
        result = process_phrase('В двенадцать часов двенадцатого сентября будет встреча', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(True, date.has_time)
        self.assertEqual(12, date.date_from.hour)
        self.assertEqual(12, date.date_from.day)
        self.assertEqual(9, date.date_from.month)

    def test_time_hour_of_day(self):
        starting_point = datetime(2019, 9, 7)
        result = process_phrase('двадцать четвёртого сентября в час дня', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(True, date.has_time)
        self.assertEqual(13, date.date_from.hour)
        self.assertEqual(24, date.date_from.day)
        self.assertEqual(9, date.date_from.month)
        self.assertEqual(2019, date.date_from.year)

    def test_fix_period(self):
        starting_point = datetime(2019, 9, 7)
        result = process_phrase('на выходных будет хорошо', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(15, date.date_to.day)

    def test_dates_period(self):
        starting_point = datetime(2019, 8, 6)
        strings = [
            'с одиннадцатого по пятнадцатое сентября будет командировка',
            'от одиннадцатого по пятнадцатое сентября будет командировка',
            'с одиннадцатого до пятнадцатого сентября будет командировка',
        ]
        for s in strings:
            result = process_phrase(s, starting_point)
            self.assertEqual(1, len(result.dates))

            date = result.dates[0]
            self.assertEqual(DateTimeTokenType.PERIOD, date.type)
            self.assertEqual(11, date.date_from.day)
            self.assertEqual(15, date.date_to.day)
            self.assertEqual(9, date.date_from.month)
            self.assertEqual(9, date.date_to.month)

        starting_point = datetime(2019, 9, 6)
        result = process_phrase('с одиннадцатого до пятнадцатого числа будет командировка', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(11, date.date_from.day)
        self.assertEqual(15, date.date_to.day)
        self.assertEqual(9, date.date_from.month)
        self.assertEqual(9, date.date_to.month)

    def test_days_of_week(self):
        starting_point = datetime(2019, 9, 6)
        result = process_phrase('во вторник встреча с заказчиком', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(10, date.date_from.day)

    def test_holidays(self):
        starting_point = datetime(2019, 9, 2)
        result = process_phrase('в эти выходные еду на дачу', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(7, date.date_from.day)
        self.assertEqual(8, date.date_to.day)

    def test_holiday(self):
        starting_point = datetime(2019, 9, 2)
        result = process_phrase('пойду гулять в следующий выходной', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(14, date.date_to.day)

    def test_from_to_reversed(self):
        starting_point = datetime(2019, 10, 13)
        result = process_phrase('с двух до пяти', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        date_from = date.date_from
        date_to = date.date_to
        self.assertEqual(14, date_from.hour)
        self.assertEqual(17, date_to.hour)
        self.assertEqual(13, date_from.day)
        self.assertEqual(13, date_to.day)

    def test_infinite_parsing(self):
        starting_point = datetime(2022, 8, 1)
        _ = process_phrase('двадцать пятого', starting_point)
        self.assertTrue(True)

    def test_just_number(self):
        starting_point = datetime(2022, 8, 1)
        result = process_phrase('пять', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(5, date_from.hour)
        self.assertEqual(1, date_from.day)
        self.assertEqual(8, date_from.month)

    def test_just_number_lower0(self):
        starting_point = datetime(2022, 8, 1)
        result = process_phrase('минус три', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(15, date_from.hour)
        self.assertEqual(1, date_from.day)
        self.assertEqual(8, date_from.month)

    def test_just_number_0(self):
        starting_point = datetime(2022, 8, 1)
        result = process_phrase('ноль', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(12, date_from.hour)
        self.assertEqual(1, date_from.day)
        self.assertEqual(8, date_from.month)

    def test_just_number_24(self):
        starting_point = datetime(2022, 8, 1)
        result = process_phrase('двадцать четыре', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(24, date_from.day)
        self.assertEqual(8, date_from.month)

    def test_just_number_over24(self):
        starting_point = datetime(2022, 8, 1)
        result = process_phrase('двадцать пятого', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(25, date_from.day)
        self.assertEqual(8, date_from.month)

    def test_just_number_31(self):
        starting_point = datetime(2022, 8, 1)
        result = process_phrase('тридцать первого', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(31, date_from.day)
        self.assertEqual(8, date_from.month)

    def test_just_number_over31(self):
        starting_point = datetime(2022, 8, 1)
        result = process_phrase('тридцать четыре', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(31, date_from.day)
        self.assertEqual(8, date_from.month)

    def test_number_after_time(self):
        starting_point = datetime(2022, 8, 1, 17)
        result = process_phrase('в пятнадцать', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(15, date_from.hour)
        self.assertEqual(2, date_from.day)
        self.assertEqual(8, date_from.month)

        result = process_phrase('в три', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(15, date_from.hour)
        self.assertEqual(2, date_from.day)
        self.assertEqual(8, date_from.month)

    def test_number_after_time_december(self):
        starting_point = datetime(2022, 12, 31, 17)
        result = process_phrase('в пятнадцать', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(15, date_from.hour)
        self.assertEqual(1, date_from.day)
        self.assertEqual(1, date_from.month)
        self.assertEqual(2023, date_from.year)

    def test_number_after_date(self):
        starting_point = datetime(2022, 8, 29)
        result = process_phrase('двадцать четвёртого', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(24, date_from.day)
        self.assertEqual(9, date_from.month)

    def test_number_after_date_december(self):
        starting_point = datetime(2022, 12, 29)
        result = process_phrase('двадцать четвёртого', starting_point)

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        date_from = date.date_from
        self.assertEqual(24, date_from.day)
        self.assertEqual(1, date_from.month)
        self.assertEqual(2023, date_from.year)


if __name__ == '__main__':
    unittest.main()
