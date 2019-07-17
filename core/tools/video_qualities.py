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
        max_ratio = 0.0
        selected_quality = ''
        for label, possibilities in self.qualities.items():
            for possibility in possibilities:
                possibility = possibility.lower()
                for word in self._string.split(' '):
                    ratio = ratio_of_containing_similar_string(word, possibility)
                    if ratio > max_ratio:
                        max_ratio = ratio
                        selected_quality = label
        return selected_quality

    @property
    def quality2(self):
        max_ratio = 0.0
        selected_quality = ''
        for label, possibilities in self.qualities.items():
            for possibility in possibilities:
                possibility = possibility.lower()
                ratio = ratio_of_containing_similar_string(self._string, possibility)
                if ratio > max_ratio:
                    max_ratio = ratio
                    selected_quality = label
        return selected_quality
