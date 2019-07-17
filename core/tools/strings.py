from difflib import SequenceMatcher
import re


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


class VideoQualityInStringDetector:

    qualities = {
        'Cam': ['CAMRip', 'CAM'],
        'TeleSync': ['TS', 'HDTS', 'TELESYNC', 'PDVD', 'PreDVDRip'],
        'WorkPrint': ['WP', 'WORKPRINT'],
        'Telecine': ['TC', 'HDTC', 'TELECINE'],
        'PPVRip': ['PPV', 'PPVRip'],
        'Screener': ['SCR', 'SCREENER', 'BDSCR'],
        'DVDScreener': ['DVDSCREENER'],
        'R5': ['R5', 'R5.LINE', 'R5.AC3.5.1.HQ'],
        'DVDRip': ['DVDRip', 'DVDMux', 'DVD-Rip'],
        'DVDR': ['DVDR', 'DVD-Full', 'Full-Rip', 'ISO rip', 'lossless rip', 'untouced rip', 'DVD-5', 'DVD-9'],
        'HDTV/PDTV/DSRip': ['DSR', 'DSRip', 'SATRip', 'DTHRip', 'DVBRip', 'HDTV', 'PDTV', 'DTVRip', 'TVRip', 'HDTVRip'],
        'VODRip': ['VODRip', 'VODR'],
        'WEBDL': ['WEBDL', 'WEB DL', 'WEB-DL', 'HDRip', 'WEB-DLRip'],
        'WEBRip': ['WEBRip', 'WEB Rip', 'WEB-Rip', 'WEB'],
        'WEBCap': ['WEB-Cap', 'WEBCAP', 'WEB Cap'],
        'HC-HDRip': ['HC', 'HDRip'],
        'BluRayRip': ['BluRay', 'bdrip', 'brip', 'bdmv', 'bdr'],
    }

    def __init__(self, string):
        self._string = string.lower()

    @property
    def quality(self):
        min_length = self._get_min_length()
        max_ratio = 0.0
        selected_quality = ''
        for label, possibilities in self.qualities.items():
            for possibility in possibilities:
                possibility = possibility.lower()
                ratio = ratio_of_containing_similar_string(self._string, possibility, min_length=min_length)
                if ratio > max_ratio:
                    max_ratio = ratio
                    selected_quality = label
        if max_ratio < 0.5:
            return 'Unknown'
        return selected_quality

    def _get_min_length(self):
        min_length = 0
        for label, possibilities in self.qualities.items():
            for possibility in possibilities:
                if len(possibility) > min_length:
                    min_length = len(possibility)
        return min_length


class RemoveAudiovisualRecordNameFromString:

    def __init__(self, audiovisual_record_name: str):
        self._audiovisual_record_name = audiovisual_record_name

    def replace_name_from_string(self, string):
        lowercased_name = self._audiovisual_record_name.lower()
        lowercased_string = string.lower()
        to_remove = []
        for word_name in lowercased_name.split(' '):
            length = len(word_name)
            idx = 0
            max_ratio = 0.0
            max_ratio_idx = 0
            while len(lowercased_string[idx:idx + length]) >= length:
                possible_similar_word = lowercased_string[idx:idx + length]
                ratio = SequenceMatcher(None, possible_similar_word, word_name).ratio()
                if ratio > max_ratio:
                    max_ratio = ratio
                    max_ratio_idx = idx
                idx += 1
            if max_ratio > 0.7:
                to_remove_word = string[max_ratio_idx:max_ratio_idx + length]
                to_remove.append(to_remove_word)
        for to_remove_word in to_remove:
            string = string.replace(to_remove_word, '')
        string = re.sub(r' +', ' ', string)
        string = string.strip()
        string = re.sub(r'(^\W+|\W+$)', '', string)
        return string
