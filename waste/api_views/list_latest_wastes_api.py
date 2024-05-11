from datetime import date

from django.db.models import Avg, Min, Max, Sum, QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Bin, Waste, Weather


class ListLatestWastesAPI(APIView):
    """
    API endpoint for retrieving aggregated waste data along with corresponding weather information for the latest date.

    This endpoint fetches data from the 'Waste' and 'Weather' models, aggregates it, and serializes it to be returned as a response.
    """

    def get_weather_data(self, latest_date: date) -> QuerySet:
        """
        Retrieve aggregated weather data for the latest date.

        :params latest_date: The latest date for which weather data is available.

        :returns: Aggregated weather data including minimum, maximum, and average temperature, precipitation, and humidity.
        """
        return Weather.objects.filter(timestamp__date=latest_date) \
            .values("location") \
            .annotate(
            min_temp=Min("temp"),
            max_temp=Max("temp"),
            avg_temp=Avg("temp"),
            min_precip=Min("precip"),
            max_precip=Max("precip"),
            sum_precip=Sum("precip"),
            min_humid=Min("humid"),
            max_humid=Max("humid"),
            avg_humid=Avg("humid"),
        )

    def get_waste_data(self, latest_date: date) -> QuerySet:
        """
        Retrieve aggregated waste data for the latest date.

        :params latest_date: The latest date for which waste data is available.

        :returns: Aggregated waste data including the total waste level for each bin.
        """
        return Waste.objects.filter(timestamp__date=latest_date) \
            .values('bin__bin_id') \
            .annotate(total_waste=Sum('level'))

    def get(self, *args, **kwargs) -> Response:
        """
        Retrieve the queryset for the API endpoint.

        :returns: A list of dictionaries containing aggregated waste data and corresponding weather information for each bin for the latest date.
        """
        latest_date = Waste.objects.latest('timestamp').timestamp.date()
        weathers = self.get_weather_data(latest_date)
        total_waste_by_bin = self.get_waste_data(latest_date)
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
        return Response(data,
                        status=status.HTTP_200_OK)
