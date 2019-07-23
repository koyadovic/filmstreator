from rest_framework import serializers


class GenreSerializer(serializers.Serializer):
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()
    name = serializers.CharField()


class PersonSerializer(serializers.Serializer):
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()
    name = serializers.CharField()


class AudiovisualRecordSerializer(serializers.Serializer):
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()
    name = serializers.CharField()
    genres = serializers.SerializerMethodField()
    year = serializers.CharField()

    directors = serializers.SerializerMethodField()
    writers = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()

    images = serializers.ListField()
    scores = serializers.SerializerMethodField()

    def get_genres(self, obj):
        for genre in obj.genres:
            yield genre.name

    def get_directors(self, obj):
        for person in obj.directors:
            yield person.name

    def get_writers(self, obj):
        for person in obj.writers:
            yield person.name

    def get_stars(self, obj):
        for person in obj.stars:
            yield person.name

    def get_scores(self, obj):
        for score in obj.scores:
            yield {
                'source_name': score['source_name'],
                'value': score['value'],
            }
