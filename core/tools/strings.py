from difflib import SequenceMatcher


def are_similar_strings(str1, str2):
    current_ratio = SequenceMatcher(None, str1, str2).ratio()
    return current_ratio > 0.7


def ratio_of_containing_similar_string(container_string, text_string, min_length=None):
    idx = 0
    length = len(text_string)
    if min_length is not None and length < min_length:
        length = min_length
    max_ratio = 0.0
    while len(container_string[idx:idx + length]) >= length:
        possible_similar_string = container_string[idx:idx + length]
        ratio = SequenceMatcher(None, possible_similar_string, text_string).ratio()
        if ratio > max_ratio:
            max_ratio = ratio
        idx += 1
    return max_ratio
