from core.fetchers.download_sources.base import AbstractDownloadSource
import re


# class LimeTorrentsSource(AbstractDownloadSource):
#     source_name = 'LimeTorrents'
#     base_url = 'https://www.limetorrents.info'
#     language = 'eng'
#     anchors_xpath = '//div[@class="tt-name"]/a'
#
#     def relative_search_string(self) -> str:
#         audiovisual_name = self.audiovisual_record.name.lower()
#         audiovisual_year = self.audiovisual_record.year
#         name = f'{audiovisual_name} {audiovisual_year}'
#         name = re.sub(r'[!\|@\"#\$~%½&½&¬\/{\(\[\)\]}?\\¿\'¡]', '%20', name).replace(' ', '-').replace('=', '-')
#         url = f'/search/all/{name}/seeds/1/'
#         return url
