from rest_framework import generics

from ..models import Bin
from ..serializers import BinSerializer


class ListBinsAPI(generics.ListAPIView):
    """
    API endpoint for retrieving a list of all bins.

    This endpoint returns a list of all bins available in the system.
    """
    serializer_class = BinSerializer
    queryset = Bin.objects.all()
