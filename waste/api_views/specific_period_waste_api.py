from django.db.models import QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Bin, Waste, Weather


class SpecificPeriodWasteAPI(APIView):
    """
    API endpoint for retrieving waste data for a specific bin or location and period 
    along with corresponding weather information.

    This endpoint allows querying waste data for a specific bin or location and time period, 
    fetching associated weather data for each waste record, and returning the aggregated data as a response.
    """

    def get_weather_data(self, weather_data: QuerySet, year: str, month: str,
                         day: str) -> QuerySet:
        """
        Retrieve weather data for the specified location and period.

        :param weather_data: The queryset containing weather data.
        :param year: The year of the period.
        :param month: The month of the period.
        :param day: The day of the period.

        :return: Weather data queryset filtered by location and period.
        """
        if year:
            weather_data = weather_data.filter(timestamp__year=year)
        if month:
            weather_data = weather_data.filter(timestamp__month=month)
        if day:
            weather_data = weather_data.filter(timestamp__day=day)
        return weather_data

    def get_waste_data(self, waste_data: QuerySet, year: str, month: str,
                       day: str) -> QuerySet:
        """
        Retrieve waste data for the specified bin or location and period.

        :param waste_data: The queryset containing waste data.
        :param year: The year of the period.
        :param month: The month of the period.
        :param day: The day of the period.

        :return: Waste data queryset filtered by bin or location and period, ordered by timestamp.
        """
        if year:
            waste_data = waste_data.filter(timestamp__year=year)
        if month:
            waste_data = waste_data.filter(timestamp__month=month)
        if day:
            waste_data = waste_data.filter(timestamp__day=day)
        return waste_data.order_by("-timestamp")

    def get(self, *args, **kwargs) -> Response:
        """
        Retrieve waste and weather data for the specified bin or location and period.

        :return: Response containing waste and weather data for the specified bin or location and period.
        """
        try:
            kwargs = {"year": "", "month": "", "day": "", "bin": "",
                      "location": ""} | kwargs
            year = str(kwargs["year"])
            month = str(kwargs["month"])
            day = str(kwargs["day"])
            bin_id = kwargs["bin"]
            location = kwargs["location"]
            if bin_id:
                bin = Bin.objects.get(bin_id=bin_id)
                weather_queryset = Weather.objects.filter(
                    location=bin.location)
                waste_queryset = Waste.objects.filter(bin=bin)
            elif location:
                bin = Bin.objects.get(location=location)
                weather_queryset = Weather.objects.filter(location=location)
                waste_queryset = Waste.objects.filter(bin__location=location)
            weathers = self.get_weather_data(weather_queryset, year, month,
                                             day)
            wastes = self.get_waste_data(waste_queryset, year, month, day)

            if bin_id:
                data = {"bin": bin_id}
            elif location:
                data = {"location": location}
            if year:
                data["year"] = int(year)
            if month:
                data["month"] = int(month)
            if day:
                data["day"] = int(day)
            data["records"] = []

            for waste in wastes:
                weather_data = weathers.filter(
                    timestamp=waste.timestamp).first()
                record = {"datetime": waste.timestamp}

                if location:
                    record["bin"] = waste.bin.bin_id

                record["level"] = waste.level
                record["temp"] = weather_data.temp if weather_data else 0
                record["precip"] = weather_data.precip if weather_data else 0
                record["humid"] = weather_data.humid if weather_data else 0
                data["records"].append(record)
        except Bin.DoesNotExist:
            if bin_id:
                return Response({"Error": "Invalid Bin ID"},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"Error": "Invalid Location"},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)
