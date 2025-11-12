from rest_framework import serializers


class SujetoSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()


class ObjetoSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance
