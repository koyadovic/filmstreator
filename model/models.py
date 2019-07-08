from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=512, db_index=True)


class AudiovisualRecord(models.Model):
    name = models.CharField(max_length=512)
    genres = models.ManyToManyField(Genre, related_name='audiovisual_records')

    deleted = models.BooleanField(default=False, db_index=True)
    disabled = models.BooleanField(default=False, db_index=True)

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save()


class Score(models.Model):
    audiovisual_record = models.ForeignKey(AudiovisualRecord, on_delete=models.PROTECT, related_name='scores')
