from typing import List, Iterable
from string import punctuation


class Helpers:

    @staticmethod
    def trim_punctuation(value: str, leave_valid_symbols: bool = True) -> str:
        # Count start punctuation
        start_offset = 0
        valid_start = '#{[{`"\''
        for c in value:
            if c in punctuation and not(leave_valid_symbols and c in valid_start):
                start_offset += 1
            else:
                break

        # Count end punctuation
        end_offset = 0
        valid_end = '!.?…)]}%"\'`'
        for c in reversed(value):
            if c in punctuation and not(leave_valid_symbols and c in valid_end):
                end_offset -= 1
            else:
                break

        return value[start_offset:end_offset]

    @staticmethod
    def swap_two(l: List, first_index: int, second_index: int) -> None:
        l[first_index], l[second_index] = l[second_index], l[first_index]


def my_pairwise(array: Iterable) -> Iterable:
    return [(x, y) for x, y in zip(array, array[1:])]


def all_increasing(array: Iterable) -> bool:
    return all(map(lambda x: x[0] < x[1], my_pairwise(array)))


def increasing_subarrays(array: Iterable) -> List[list]:
    if len(array) == 2:
        return [[array[0]], [array[1]]] if array[0] <= array[1] else [[array[1]], [array[0]]]
    result = []
    curr = []
    for idx, (i, j) in enumerate(my_pairwise(array)):
        if i > j:
            curr.append(array[idx])
        elif curr:
            result.append(curr)
            curr = []
        else:
            result.append([array[idx]])

    if curr:
        curr.append(array[idx + 1])
        result.append(curr)

    return result
