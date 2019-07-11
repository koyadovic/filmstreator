from datetime import datetime

from core.model.audiovisual import BaseModel, AudiovisualRecord


class SourceDownload(BaseModel):
    audiovisual_record: AudiovisualRecord
    source_name: str
    link: str
    last_check: datetime
