from django.db.models import Avg, Min, Max, Sum, QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Bin, Waste, Weather


class ListPeriodWastesAPI(APIView):
    """
    API endpoint for retrieving aggregated waste data along with corresponding weather information for a specified date.

    This endpoint fetches data from the 'Waste' and 'Weather' models, aggregates it based on the provided date parameters,
    and serializes it to be returned as a response.
    """

    def get_weather_data(self, year: str, month: str, day: str) -> QuerySet:
        """
        Retrieve aggregated weather data for the specified date.

        :param year: The year of the date.
        :param month: The month of the date.
        :param day: The day of the date.

        :return: Aggregated weather data including minimum, maximum, and average temperature, precipitation, and humidity.
        """
        weather_data = Weather.objects.all()
        if year:
            weather_data = weather_data.filter(timestamp__year=year)
        if month:
            weather_data = weather_data.filter(timestamp__month=month)
        if day:
            weather_data = weather_data.filter(timestamp__day=day)
        return weather_data.values("location") \
            .annotate(
            min_temp=Min("temp"),
            max_temp=Max("temp"),
            avg_temp=Avg("temp"),
            min_precip=Min("precip"),
            max_precip=Max("precip"),
            sum_precip=Sum("precip"),
            min_humid=Min("humid"),
            max_humid=Max("humid"),
            avg_humid=Avg("humid"))

    def get_waste_data(self, year: str, month: str, day: str) -> QuerySet:
        """
        Retrieve aggregated waste data for the specified date.

        :param year: The year of the date.
        :param month: The month of the date.
        :param day: The day of the date.

        :return: Aggregated waste data including the total waste level for each bin.
        """
        waste_data = Waste.objects.all()
        if year:
            waste_data = waste_data.filter(timestamp__year=year)
        if month:
            waste_data = waste_data.filter(timestamp__month=month)
        if day:
            waste_data = waste_data.filter(timestamp__day=day)
        return waste_data.values('bin__bin_id') \
            .annotate(total_waste=Sum('level'))

    def get(self, *args, **kwargs) -> Response:
        """
        Retrieve the queryset for the API endpoint.

        :return: A list of dictionaries containing aggregated waste data and corresponding weather information for each bin.
        """
        kwargs = {"year": "", "month": "", "day": ""} | kwargs
        year = str(kwargs["year"])
        month = str(kwargs["month"])
        day = str(kwargs["day"])
        weathers = self.get_weather_data(year, month, day)
        total_waste_by_bin = self.get_waste_data(year, month, day)
        data = []
        for bin in total_waste_by_bin:
            bin_location = Bin.objects.get(bin_id=bin['bin__bin_id']).location
            weather_data = weathers.get(location=bin_location)
            data.append({
                "bin": bin['bin__bin_id'],
                "total_waste": bin['total_waste'],
                "min_temp": weather_data['min_temp'],
                "max_temp": weather_data['max_temp'],
                "avg_temp": weather_data['avg_temp'],
                "min_precip": weather_data['min_precip'],
                "max_precip": weather_data['max_precip'],
                "sum_precip": weather_data['sum_precip'],
                "min_humid": weather_data['min_humid'],
                "max_humid": weather_data['max_humid'],
                "avg_humid": weather_data['avg_humid']
            })
        return Response(data, status=status.HTTP_200_OK)
