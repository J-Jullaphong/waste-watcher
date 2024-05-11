from rest_framework import generics

from ..models import Bin
from ..serializers import BinSerializer


class SpecificBinAPI(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific bin.

    This endpoint allows retrieving details of a specific bin by its ID.
    """
    serializer_class = BinSerializer
    queryset = Bin.objects.all()
