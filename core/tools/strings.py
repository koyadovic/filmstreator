from difflib import SequenceMatcher


def are_similar_strings(str1, str2):
    current_ratio = SequenceMatcher(None, str1, str2).ratio()
    return current_ratio > 0.7
