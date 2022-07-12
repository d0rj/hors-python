import json
import os
from typing import List, Union


NUMBER_SYSTEM_PATH = os.path.join(os.path.dirname(__file__), 'russian_number_system.json')

russian_number_system = json.load(open(NUMBER_SYSTEM_PATH, 'r'))

decimal_words = ['ноль', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять']


def _number_formation(number_words: List[str]) -> int:
    numbers = [
        russian_number_system[number_word] for number_word in number_words
    ]
    if len(numbers) == 4:
        return (numbers[0] * numbers[1]) + numbers[2] + numbers[3]
    if len(numbers) == 3:
        return numbers[0] + numbers[1] + numbers[2]
    if len(numbers) == 2:
        return numbers[0] + numbers[1]
    return numbers[0]


def _get_decimal_sum(decimal_digit_words: List[str]) -> float:
    decimal_number_str = [
        russian_number_system[dec_word] if dec_word in decimal_words else 0
        for dec_word in decimal_digit_words
    ]
    final_decimal_string = '0.' + ''.join(map(str,decimal_number_str))
    return float(final_decimal_string)


def _numeric_words_to_num(clean_numbers: List[str]) -> Union[int, float, None]:
    # Error if user enters million,billion, thousand or decimal point twice
    if clean_numbers.count('тысяча') > 1 or clean_numbers.count('миллион') > 1 or\
            clean_numbers.count('миллиард') > 1 or clean_numbers.count('целых') > 1 or clean_numbers.count('целая') > 1:
        raise ValueError('Redundant number word! Please enter a valid number word (eg. two million twenty three thousand and forty nine)')

    clean_decimal_numbers = []
    # separate decimal part of number (if exists)
    if clean_numbers.count('целых') == 1 or clean_numbers.count('целая') == 1:
        clean_decimal_numbers = clean_numbers[clean_numbers.index('целых') + 1:]
        clean_numbers = clean_numbers[:clean_numbers.index('целых')]

    if 'миллиард' in clean_numbers:
        billion_index = clean_numbers.index('миллиард')
    elif 'миллиарда' in clean_numbers:
        billion_index = clean_numbers.index('миллиарда')
    elif 'миллиарду' in clean_numbers:
        billion_index = clean_numbers.index('миллиарду')
    elif 'миллиардом' in clean_numbers:
        billion_index = clean_numbers.index('миллиардом')
    elif 'миллиарде' in clean_numbers:
        billion_index = clean_numbers.index('миллиарде')
    elif 'миллиардов' in clean_numbers:
        billion_index = clean_numbers.index('миллиардов')
    else:
        billion_index = -1

    if 'миллион' in clean_numbers:
        million_index = clean_numbers.index('миллион')
    elif 'миллиона' in clean_numbers:
        million_index = clean_numbers.index('миллиона')
    elif 'миллиону' in clean_numbers:
        million_index = clean_numbers.index('миллиону')
    elif 'миллионом' in clean_numbers:
        million_index = clean_numbers.index('миллионом')
    elif 'миллионе' in clean_numbers:
        million_index = clean_numbers.index('миллионе')
    elif 'миллионов' in clean_numbers:
        million_index = clean_numbers.index('миллионов')
    else:
        million_index = -1

    if 'тысяча' in clean_numbers:
        thousand_index = clean_numbers.index('тысяча')
    elif 'тысячи' in clean_numbers:
        thousand_index = clean_numbers.index('тысячи')
    elif 'тысяче' in clean_numbers:
        thousand_index = clean_numbers.index('тысяче')
    elif 'тысячу' in clean_numbers:
        thousand_index = clean_numbers.index('тысячу')
    elif 'тысячей' in clean_numbers:
        thousand_index = clean_numbers.index('тысячей')
    elif 'тысяч' in clean_numbers:
        thousand_index = clean_numbers.index('тысяч')
    else:
        thousand_index = -1

    if (thousand_index > -1 and (thousand_index < million_index or thousand_index < billion_index)) or\
            (million_index > -1 and million_index < billion_index):
        raise ValueError('Malformed number! Please enter a valid number word (eg. two million twenty three thousand and forty nine)')

    total_sum = 0

    if len(clean_numbers) > 0:
        # hack for now, better way TODO
        if len(clean_numbers) == 1:
            total_sum += russian_number_system[clean_numbers[0]]

        else:
            if billion_index > -1:
                billion_multiplier = _number_formation(clean_numbers[0:billion_index])
                total_sum += billion_multiplier * 1000000000

            if million_index > -1:
                if billion_index > -1:
                    million_multiplier = _number_formation(clean_numbers[billion_index + 1:million_index])
                else:
                    million_multiplier = _number_formation(clean_numbers[0:million_index])
                total_sum += million_multiplier * 1000000

            if thousand_index > -1:
                if million_index > -1:
                    thousand_multiplier = _number_formation(clean_numbers[million_index + 1:thousand_index])
                        
                elif billion_index > -1 and million_index == -1:
                    thousand_multiplier = _number_formation(clean_numbers[billion_index + 1:thousand_index])
                        
                elif thousand_index == 0:
                    thousand_multiplier = 1
                
                else:
                    thousand_multiplier = _number_formation(clean_numbers[0:thousand_index])
                total_sum += thousand_multiplier * 1000

            if thousand_index > -1 and thousand_index == len(clean_numbers) - 1:
                hundreds = 0
            elif thousand_index > -1 and thousand_index != len(clean_numbers) - 1:
                hundreds = _number_formation(clean_numbers[thousand_index + 1:])
            elif million_index > -1 and million_index != len(clean_numbers) - 1:
                hundreds = _number_formation(clean_numbers[million_index + 1:])
            elif billion_index > -1 and billion_index != len(clean_numbers) - 1:
                hundreds = _number_formation(clean_numbers[billion_index + 1:])
            elif thousand_index == -1 and million_index == -1 and billion_index == -1:
                hundreds = _number_formation(clean_numbers)
            else:
                hundreds = 0
            total_sum += hundreds

    if len(clean_decimal_numbers) > 0:
        decimal_sum = _get_decimal_sum(clean_decimal_numbers)
        total_sum += decimal_sum

    return total_sum


def replace_word_nums(number_sentence: str) -> Union[int, float, None]:
    if number_sentence.isdigit():
        return int(number_sentence)

    split_words = number_sentence.strip().split()

    clean_numbers = []
    result_sentence_words = []
    for word in split_words:
        if word.lower() in russian_number_system:
            clean_numbers.append(word.lower())
        else:
            if len(clean_numbers) > 0:
                number_string = str(_numeric_words_to_num(clean_numbers))
                result_sentence_words.append(number_string)
                result_sentence_words.append(word)
                clean_numbers = []
            else:
                result_sentence_words.append(word)
    if len(clean_numbers) > 0:
        result_sentence_words.append(str(_numeric_words_to_num(clean_numbers)))

    return ' '.join(result_sentence_words)


def replace_word_nums_safe(number_sentence: str) -> str:
    try:
        number_sentence = str(replace_word_nums(number_sentence))
    except ValueError:
        pass
    return number_sentence
