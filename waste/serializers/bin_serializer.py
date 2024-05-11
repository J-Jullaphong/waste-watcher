from rest_framework import serializers

from ..models import Bin


class BinSerializer(serializers.ModelSerializer):
    """
    Serializer for the Bin model.
    """

    class Meta:
        model = Bin
        fields = "__all__"
