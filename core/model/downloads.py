from datetime import datetime, timezone

from core.model.audiovisual import BaseModel


class DownloadSource(BaseModel):
    last_check: datetime
    source_name: str
    link: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_check = kwargs.pop('last_check', datetime.utcnow().replace(tzinfo=timezone.utc))
        self.source_name = kwargs.pop('source_name', '')
        self.link = kwargs.pop('link', '')
