from core.tools.strings import ratio_of_containing_similar_string


class VideoQualityInStringDetector:

    qualities = {
        'Cam': ['CAMRip', 'CAM'],
        'DVD-Rip': ['DVDRip', 'DVDMux', 'DVD-Rip'],
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
        return selected_quality

    def _get_min_length(self):
        min_length = 0
        for label, possibilities in self.qualities.items():
            for possibility in possibilities:
                if len(possibility) > min_length:
                    min_length = len(possibility)
        return min_length
