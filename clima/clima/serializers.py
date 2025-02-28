from rest_framework import serializers
from .models import Clima
from .models import Cidade

class CidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidade
        fields = '__all__'

class ClimaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clima
        fields = '__all__'
