from django.db import models


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class Genre(BaseModel):
    name = models.CharField(max_length=512, db_index=True)


class Person(BaseModel):
    name = models.CharField(max_length=512, db_index=True)


class AudiovisualRecord(BaseModel):
    """
    TODO
    Nos falta fuente de descarga
    """
    name = models.CharField(max_length=512)
    genres = models.ManyToManyField(Genre, related_name='audiovisual_records')
    year = models.IntegerField(default=0)

    directors = models.ManyToManyField(Person, related_name='audiovisual_records_as_director')
    writers = models.ManyToManyField(Person, related_name='audiovisual_records_as_writer')
    stars = models.ManyToManyField(Person, related_name='audiovisual_records_as_star')

    deleted = models.BooleanField(default=False, db_index=True)
    disabled = models.BooleanField(default=False, db_index=True)

    last_check = models.DateTimeField(blank=True, null=True)

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save()


class Score(BaseModel):
    audiovisual_record = models.ForeignKey(AudiovisualRecord, on_delete=models.PROTECT, related_name='scores')


class Photo(BaseModel):
    audiovisual_record = models.ForeignKey(AudiovisualRecord, on_delete=models.PROTECT, related_name='photos')
    image = models.ImageField(blank=False, null=False)
