from django.db.models import Sum
from django.views.generic import TemplateView

from ..models import Bin, Waste, Weather


class LatestWasteView(TemplateView):
    """
    View for displaying the latest waste data along with weather information.

    This view fetches the latest waste data and corresponding weather information
    for a specified bin or location and renders it on a template.
    """
    template_name = 'latest_waste.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the template.

        :return: Context data for rendering the template.
        """
        context = super().get_context_data(**kwargs)
        filter_type = self.request.GET.get('filter_type')
        filter_value = self.request.GET.get('filter_value')

        chart_data = []
        chart_labels = []
        temperature_data = []
        precipitation_data = []
        humidity_data = []

        if filter_type == 'bin_id' and filter_value.isnumeric():
            wastes = Waste.objects.filter(bin=filter_value)
            waste = wastes.order_by('-timestamp').first()
            if waste:
                waste_date = waste.timestamp.date()
                wastes = wastes.filter(timestamp__date=waste_date)

                chart_data = [data.level for data in wastes]
                chart_labels = [data.timestamp.strftime("%H:%M") for data in
                                wastes]

                weathers = Weather.objects.filter(location=waste.bin.location)
                latest_weather = weathers.order_by('-timestamp').first()
            else:
                latest_weather = None
        elif filter_type == 'location' and filter_value:
            waste = Waste.objects.filter(bin__location=filter_value).order_by(
                '-timestamp').first()
            latest_weather = Weather.objects.filter(
                location=filter_value).order_by('-timestamp').first()
            if waste:
                waste_date = waste.timestamp.date()
                wastes = Waste.objects.filter(bin__location=filter_value,
                                              timestamp__date=waste_date)
                wastes = wastes.values("timestamp__hour").annotate(
                    total_level=Sum("level"))

                chart_data = [data['total_level'] for data in wastes]
                chart_labels = [f"{data['timestamp__hour']:02d}:00" for data in
                                wastes]

                weathers = Weather.objects.filter(location=filter_value)
        else:
            waste = Waste.objects.order_by('-timestamp').first()
            if waste:
                waste_date = waste.timestamp.date()
                wastes = Waste.objects.filter(timestamp__date=waste_date)
                wastes = wastes.values("timestamp__hour").annotate(
                    total_level=Sum("level"))

                chart_data = [data['total_level'] for data in wastes]
                chart_labels = [f"{data['timestamp__hour']:02d}:00" for data in
                                wastes]

                weathers = Weather.objects.filter(location=waste.bin.location)
                latest_weather = weathers.order_by('-timestamp').first()
            else:
                weathers = []
                latest_weather = None

        for weather in weathers:
            temperature_data.append(float(weather.temp))
            precipitation_data.append(float(weather.precip))
            humidity_data.append(float(weather.humid))

        context['locations'] = Bin.objects.all().values('location')
        context['bins'] = Bin.objects.all().values('bin_id')
        context['waste'] = waste
        context['latest_weather'] = latest_weather

        context['chart_data'] = chart_data
        context['chart_labels'] = chart_labels
        context['temperature_data'] = temperature_data
        context['precipitation_data'] = precipitation_data
        context['humidity_data'] = humidity_data

        return context
