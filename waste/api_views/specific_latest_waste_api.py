from datetime import date

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Bin, Waste, Weather


class SpecificLatestWasteAPI(APIView):
    """
    API endpoint for retrieving waste data for a specific bin or location for the latest date
    along with corresponding weather information.

    This endpoint allows querying waste data for a specific bin or location for the latest date,
    fetching associated weather data for each waste record, and returning the aggregated data as a response.
    """

    def get_weather_data(self, weather_data: QuerySet,
                         latest_date: date) -> QuerySet:
        """
        Retrieve weather data for the specified location and latest date.

        :param weather_data: The queryset containing weather data.
        :param location: The location for which weather data is requested.
        :param latest_date: The latest date.

        :return: Weather data queryset filtered by location and latest date.
        """
        return weather_data.filter(timestamp__date=latest_date)

    def get_waste_data(self, waste_data: QuerySet,
                       latest_date: date) -> QuerySet:
        """
        Retrieve waste data for the specified bin or location and latest date.

        :param waste_data: The queryset containing waste data.
        :param location: The location for which waste data is requested.
        :param latest_date: The latest date.

        :return: Waste data queryset filtered by bin or location and latest date, ordered by timestamp.
        """
        return waste_data.filter(timestamp__date=latest_date).order_by(
            "-timestamp")

    def get(self, *args, **kwargs) -> Response:
        """
        Retrieve waste and weather data for the specified bin or location for the latest date.

        :return: Response containing waste and weather data for the specified bin or location and latest date.
        """
        try:
            kwargs = {"bin": "", "location": ""} | kwargs
            bin_id = self.kwargs.get("bin")
            location = self.kwargs.get("location")
            if bin_id:
                bin = Bin.objects.get(bin_id=bin_id)
                weather_queryset = Weather.objects.filter(
                    location=bin.location)
                waste_queryset = Waste.objects.filter(bin=bin)
                latest_date = waste_queryset.latest(
                    'timestamp').timestamp.date()
            elif location:
                bin = Bin.objects.get(location=location)
                weather_queryset = Weather.objects.filter(location=location)
                waste_queryset = Waste.objects.filter(bin__location=location)
                latest_date = waste_queryset.latest(
                    'timestamp').timestamp.date()
            weathers = self.get_weather_data(weather_queryset, latest_date)
            wastes = self.get_waste_data(waste_queryset, latest_date)
            if bin_id:
                data = {"bin": bin_id}
            elif location:
                data = {"location": location}
            data["date"] = latest_date
            data["records"] = []
            for waste in wastes:
                weather_data = weathers.filter(
                    timestamp=waste.timestamp).first()
                record = {
                    "datetime": waste.timestamp,
                    "level": waste.level,
                    "temp": weather_data.temp if weather_data else 0,
                    "precip": weather_data.precip if weather_data else 0,
                    "humid": weather_data.humid if weather_data else 0
                }
                data["records"].append(record)
        except Bin.DoesNotExist:
            if bin_id:
                return Response({"Error": "Invalid Bin ID"},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"Error": "Invalid Location"},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)
