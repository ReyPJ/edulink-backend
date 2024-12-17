from rest_framework import serializers
from .models import NoteBook, NoteBookPages


class NoteBookPagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteBookPages
        fields = '__all__'


class NoteBookSerializer(serializers.ModelSerializer):
    pages = NoteBookPagesSerializer(many=True, read_only=True)

    class Meta:
        models = NoteBook
        fields = '__all__'
