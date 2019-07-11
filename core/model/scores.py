from core.model.audiovisual import BaseModel, AudiovisualRecord


class Score(BaseModel):
    audiovisual_record: AudiovisualRecord
    value: float
