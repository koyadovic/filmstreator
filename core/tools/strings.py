from difflib import SequenceMatcher
import re

from core.tools.exceptions import CoreException


def are_similar_strings(str1, str2):
    current_ratio = SequenceMatcher(None, str1, str2).ratio()
    return current_ratio > 0.7


def are_similar_strings_with_ratio(str1, str2):
    current_ratio = SequenceMatcher(None, str1, str2).ratio()
    return current_ratio > 0.7, current_ratio


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


POSSIBLE_SEPARATORS = [' ', '.', '-', '_', '[', ']', '(', ')', '/', '\\', '{', '}', '<', '>', '~', '+']

LANGUAGES = {
    # 'eng': ['en', 'eng', 'english'],
    'spa': ['es', 'spa', 'esp', 'spanish'],
    'jpn': ['ja', 'jpn', 'japanese'],
    'fra': ['fr', 'fra', 'french'],
    'hin': ['hi', 'hin', 'hindi'],
    'ita': ['it', 'ita', 'italian'],
    'deu': ['deu', 'de', 'ger', 'german'],
    'kor': ['kor', 'ko', 'korean'],
    'rus': ['rus', 'ru', 'russian'],
    'gre': ['gre', 'greek'],
}


def guess_language(name, default=None):
    name = name.lower()
    for lang, possibilities in LANGUAGES.items():
        for possibility in possibilities:
            if possibility in name:
                idx = name.index(possibility)
                try:
                    if (
                            name[idx - 1] in POSSIBLE_SEPARATORS and
                            name[idx + len(possibility)] in POSSIBLE_SEPARATORS
                    ):
                        return lang
                except IndexError:
                    continue
    return 'eng' if default is None else default


class VideoQualityInStringDetector:
    """
    Algorithm will sort by 'possibility' length
    """
    qualities = [
        {'possibility': 'BluRay', 'tag': 'BluRayRip'},
        {'possibility': 'brip', 'tag': 'BluRayRip'},
        {'possibility': 'brrip', 'tag': 'BluRayRip'},
        {'possibility': 'Blu-ray', 'tag': 'BluRayRip'},
        {'possibility': 'bdmv', 'tag': 'BluRayRip'},
        {'possibility': 'bdr', 'tag': 'BluRayRip'},
        {'possibility': 'HC', 'tag': 'HDRip'},
        {'possibility': 'HDR', 'tag': 'HDRip'},
        {'possibility': 'R5.AC3.5.1.HQ', 'tag': 'R5'},
        {'possibility': 'untouched rip', 'tag': 'DVDRip'},
        {'possibility': 'lossless rip', 'tag': 'DVDRip'},
        {'possibility': 'DVDSCREENER', 'tag': 'DVDScreener'},
        {'possibility': 'WORKPRINT', 'tag': 'WP'},
        {'possibility': 'BluRayScr', 'tag': 'BluRayScreener'},
        {'possibility': 'WEB-DLRip', 'tag': 'WEBDL'},
        {'possibility': 'WEB DL Rip', 'tag': 'WEBDL'},
        {'possibility': 'WEBDL', 'tag': 'WEBDL'},
        {'possibility': 'WEB-DL', 'tag': 'WEBDL'},
        {'possibility': 'WEB DL', 'tag': 'WEBDL'},
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
        {'possibility': 'DVD SCR', 'tag': 'DVDScreener'},
        {'possibility': 'DVDRip', 'tag': 'DVDRip'},
        {'possibility': 'DVD Rip', 'tag': 'DVDRip'},
        {'possibility': 'DVD-R', 'tag': 'DVDRip'},
        {'possibility': 'DVD-5', 'tag': 'DVDRip'},
        {'possibility': 'DVD-9', 'tag': 'DVDRip'},
        {'possibility': 'DVD5', 'tag': 'DVDRip'},
        {'possibility': 'DVD9', 'tag': 'DVDRip'},
        {'possibility': 'DVDMux', 'tag': 'DVDRip'},
        {'possibility': 'DVDR', 'tag': 'DVDRip'},
        {'possibility': 'SATRip', 'tag': 'HDTV'},
        {'possibility': 'DTHRip', 'tag': 'HDTV'},
        {'possibility': 'DVBRip', 'tag': 'HDTV'},
        {'possibility': 'DTVRip', 'tag': 'HDTV'},
        {'possibility': 'VODRip', 'tag': 'VODRip'},
        {'possibility': 'WEBRip', 'tag': 'WEBRip'},
        {'possibility': 'WEBCAP', 'tag': 'WEBCap'},
        {'possibility': 'BRSCR', 'tag': 'BluRayScreener'},
        {'possibility': 'DSRip', 'tag': 'HDTV'},
        {'possibility': 'TVRip', 'tag': 'HDTV'},
        {'possibility': 'WEBDL', 'tag': 'WEBDL'},
        {'possibility': 'HDRip', 'tag': 'HDRip'},
        {'possibility': 'bdrip', 'tag': 'BluRayRip'},
        {'possibility': 'HDTS', 'tag': 'TS'},
        {'possibility': 'HDTC', 'tag': 'Telecine'},
        {'possibility': 'HDTV', 'tag': 'HDTV'},
        {'possibility': 'PDTV', 'tag': 'HDTV'},
        {'possibility': 'VODR', 'tag': 'VODRip'},
        {'possibility': 'CAM', 'tag': 'Cam'},
        {'possibility': 'HDCAM', 'tag': 'Cam'},
        {'possibility': 'HD CAM', 'tag': 'Cam'},
        {'possibility': 'newcam', 'tag': 'Cam'},
        {'possibility': 'new cam', 'tag': 'Cam'},
        {'possibility': 'PPV', 'tag': 'PPVRip'},
        {'possibility': 'SCR', 'tag': 'Screener'},
        {'possibility': 'DSR', 'tag': 'HDTV'},
        {'possibility': 'WEB', 'tag': 'WEBRip'},
        {'possibility': 'TS', 'tag': 'TS'},
        {'possibility': 'PDVD', 'tag': 'TS'},
        {'possibility': 't-s rip', 'tag': 'TS'},
        {'possibility': 'WP', 'tag': 'WP'},
        {'possibility': 'TC', 'tag': 'Telecine'},
        {'possibility': 'R5', 'tag': 'R5'},
        {'possibility': '1080p', 'tag': 'HDTV'},
        {'possibility': 'HD 1080p', 'tag': 'HDTV'},
        {'possibility': 'HD 720p', 'tag': 'HDTV'},
        {'possibility': '720p', 'tag': 'HDTV'},
        {'possibility': 'soundtrack', 'tag': 'Audio'},
        {'possibility': 'mp3', 'tag': 'Audio'},
        {'possibility': 'ogg', 'tag': 'Audio'},
        {'possibility': 'flac', 'tag': 'Audio'},
        {'possibility': 'UHDrip', 'tag': 'UHDrip'},
        {'possibility': 'UHD rip', 'tag': 'UHDrip'},
        {'possibility': 'UltraHD', 'tag': 'UHDrip'},
    ]

    our_qualities = sorted(set([e['tag'] for e in qualities]))

    def __init__(self, string):
        self._string = string.lower()
        self._quality_ratio = 0.0
        self.sorted_qualities = sorted(self.qualities, key=lambda e: len(e.get('possibility')), reverse=True)

    @property
    def quality(self):
        sorted_qualities = self.sorted_qualities
        string = self._string.lower()
        tags = []
        for quality in sorted_qualities:
            possibility = quality['possibility'].lower()
            tag = quality['tag']

            possibility_length = len(possibility)

            selected_idx = 0
            max_idx_ratio = 0.0
            for idx in range(len(string) - possibility_length + 1):
                ratio = ratio_of_containing_similar_string(string[idx:idx+possibility_length], possibility)
                if ratio > max_idx_ratio:
                    max_idx_ratio = ratio
                    selected_idx = idx

            possible_similar_text = string[selected_idx:selected_idx + possibility_length]
            similar, ratio = are_similar_strings_with_ratio(possible_similar_text, possibility)
            if ratio < 0.8:
                continue

            accepted = string[selected_idx - 1] in POSSIBLE_SEPARATORS
            try:
                accepted = accepted or string[selected_idx + possibility_length] not in POSSIBLE_SEPARATORS
            except IndexError:
                if not accepted:
                    continue
            if not accepted:
                continue

            if ratio == 1.0:
                return tag

            t = {
                'tag': tag,
                'ratio': ratio
            }
            tags.append(t)

        tags.sort(key=lambda t: t['ratio'], reverse=True)
        try:
            return tags[0]['tag']
        except IndexError:
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
