from rest_framework.serializers import ModelSerializer

from .models import Query, Sponsor

class QuerySerializer(ModelSerializer):
    class Meta:
        model = Query
        fields = '__all__'

class SponsorSerializer(ModelSerializer):
    class Meta:
        model = Sponsor
        exclude = ['id',]
