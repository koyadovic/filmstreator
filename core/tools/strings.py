from difflib import SequenceMatcher
import re

from core.tools.exceptions import CoreException


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
    """
    Algorithm will sort by 'possibility' length
    """
    qualities = [
        {'possibility': 'R5.AC3.5.1.HQ', 'tag': 'R5'},
        {'possibility': 'untouched rip', 'tag': 'DVDR'},
        {'possibility': 'lossless rip', 'tag': 'DVDR'},
        {'possibility': 'DVDSCREENER', 'tag': 'DVDScreener'},
        {'possibility': 'WORKPRINT', 'tag': 'WP'},
        {'possibility': 'BluRayScr', 'tag': 'BluRayScreener'},
        {'possibility': 'WEB-DLRip', 'tag': 'WEBDL'},
        {'possibility': 'TELESYNC', 'tag': 'TS'},
        {'possibility': 'TELECINE', 'tag': 'Telecine'},
        {'possibility': 'SCREENER', 'tag': 'Screener'},
        {'possibility': 'DVD-Full', 'tag': 'DVDR'},
        {'possibility': 'Full-Rip', 'tag': 'DVDR'},
        {'possibility': 'R5.LINE', 'tag': 'R5'},
        {'possibility': 'DVD-Rip', 'tag': 'DVDRip'},
        {'possibility': 'ISOrip', 'tag': 'DVDR'},
        {'possibility': 'HDTVRip', 'tag': 'HDTV'},
        {'possibility': 'WEBRip', 'tag': 'WEBRip'},
        {'possibility': 'WEB-Rip', 'tag': 'WEBRip'},
        {'possibility': 'WEB-Cap', 'tag': 'WEBCap'},
        {'possibility': 'WEBCap', 'tag': 'WEBCap'},
        {'possibility': 'CAMRip', 'tag': 'Cam'},
        {'possibility': 'PPVRip', 'tag': 'PPVRip'},
        {'possibility': 'DVDSCR', 'tag': 'DVDScreener'},
        {'possibility': 'DVDRip', 'tag': 'DVDRip'},
        {'possibility': 'DVDMux', 'tag': 'DVDRip'},
        {'possibility': 'SATRip', 'tag': 'HDTV'},
        {'possibility': 'DTHRip', 'tag': 'HDTV'},
        {'possibility': 'DVBRip', 'tag': 'HDTV'},
        {'possibility': 'DTVRip', 'tag': 'HDTV'},
        {'possibility': 'VODRip', 'tag': 'VODRip'},
        {'possibility': 'WEBDL', 'tag': 'WEBDL'},
        {'possibility': 'WEB-DL', 'tag': 'WEBDL'},
        {'possibility': 'WEBRip', 'tag': 'WEBRip'},
        {'possibility': 'WEBCAP', 'tag': 'WEBCap'},
        {'possibility': 'BluRay', 'tag': 'BluRayRip'},
        {'possibility': 'BRSCR', 'tag': 'BluRayScreener'},
        {'possibility': 'DVD-5', 'tag': 'DVDR'},
        {'possibility': 'DVD-9', 'tag': 'DVDR'},
        {'possibility': 'DSRip', 'tag': 'HDTV'},
        {'possibility': 'TVRip', 'tag': 'HDTV'},
        {'possibility': 'WEBDL', 'tag': 'WEBDL'},
        {'possibility': 'HDRip', 'tag': 'HC-HDRip'},
        {'possibility': 'bdrip', 'tag': 'BluRayRip'},
        {'possibility': 'HDTS', 'tag': 'TS'},
        {'possibility': 'PDVD', 'tag': 'TS'},
        {'possibility': 'HDTC', 'tag': 'Telecine'},
        {'possibility': 'DVDR', 'tag': 'DVDR'},
        {'possibility': 'HDTV', 'tag': 'HDTV'},
        {'possibility': 'PDTV', 'tag': 'HDTV'},
        {'possibility': 'VODR', 'tag': 'VODRip'},
        {'possibility': 'brip', 'tag': 'BluRayRip'},
        {'possibility': 'brrip', 'tag': 'BluRayRip'},
        {'possibility': 'bdmv', 'tag': 'BluRayRip'},
        {'possibility': ' CAM ', 'tag': 'Cam'},
        {'possibility': ' PPV ', 'tag': 'PPVRip'},
        {'possibility': ' SCR ', 'tag': 'Screener'},
        {'possibility': ' DSR ', 'tag': 'HDTV'},
        {'possibility': ' WEB ', 'tag': 'WEBRip'},
        {'possibility': ' bdr ', 'tag': 'BluRayRip'},
        {'possibility': ' TS ', 'tag': 'TS'},
        {'possibility': ' WP ', 'tag': 'WP'},
        {'possibility': ' TC ', 'tag': 'Telecine'},
        {'possibility': ' R5 ', 'tag': 'R5'},
        {'possibility': '1080p', 'tag': 'HDTV'},
        {'possibility': '720p', 'tag': 'HDTV'},
        {'possibility': 'soundtrack', 'tag': 'Audio'},
        {'possibility': 'audio', 'tag': 'Audio'},
        {'possibility': 'mp3', 'tag': 'Audio'},
        {'possibility': ' HC ', 'tag': 'HC-HDRip'}
    ]

    our_qualities = sorted(set([e['tag'] for e in qualities]))

    def __init__(self, string):
        self._string = string.lower()
        self._quality_ratio = 0.0

    @property
    def quality(self):
        sorted_qualities = sorted(self.qualities, key=lambda e: len(e.get('possibility')), reverse=True)
        for cut_ratio in [1.0 - (i * 0.05) for i in range(0, 6)]:
            for element in sorted_qualities:
                possibility = element.get('possibility').lower()
                tag = element.get('tag')
                ratio = ratio_of_containing_similar_string(
                    self._string, possibility, min_length=len(possibility)
                )
                if ratio > cut_ratio:
                    self._quality_ratio = ratio
                    return tag
        return 'Unknown'

    def _expanded_possibility(self, possibility):
        if len(possibility) >= 4:
            return [possibility]
        for char in [' ', '.', '_', '-']:
            yield char + possibility + char

    class InsufficientLengthPossibility(CoreException):
        pass


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
