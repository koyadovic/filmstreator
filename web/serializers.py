from rest_framework import serializers


class GenreSerializer(serializers.Serializer):
    # created_date = serializers.DateTimeField()
    # updated_date = serializers.DateTimeField()
    name = serializers.CharField()


class PersonSerializer(serializers.Serializer):
    # created_date = serializers.DateTimeField()
    # updated_date = serializers.DateTimeField()
    name = serializers.CharField()


class AudiovisualRecordSerializer(serializers.Serializer):
    # created_date = serializers.DateTimeField()
    # updated_date = serializers.DateTimeField()
    name = serializers.CharField()
    slug = serializers.CharField()
    genres = serializers.SerializerMethodField()
    year = serializers.CharField()

    directors = serializers.SerializerMethodField()
    writers = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()

    images = serializers.ListField()
    scores = serializers.SerializerMethodField()

    def get_genres(self, obj):
        return [{'name': genre.get('name')} for genre in obj.genres]

    def get_directors(self, obj):
        return [{'name': person.get('name')} for person in obj.directors]

    def get_writers(self, obj):
        return [{'name': person.get('name')} for person in obj.writers]

    def get_stars(self, obj):
        return [{'name': person.get('name')} for person in obj.stars]

    def get_scores(self, obj):
        return [{
            'source_name': score.get('source_name'),
            'value': score.get('value'),
        } for score in obj.scores]

