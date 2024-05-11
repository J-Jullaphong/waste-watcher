from calendar import month_name, monthrange
from datetime import date

from django.db.models import Sum, Avg, Min, Max
from django.views.generic import TemplateView
from django.views.generic.list import QuerySet

from ..models import Bin, Waste, Weather


class WasteLevelComparisonView(TemplateView):
    """
    View for comparing waste levels and weather data.

    This view fetches waste data and corresponding weather information for a specified time period
    and renders it on a template for comparison.
    """
    template_name = 'waste_level_comparison.html'

    def get_context_data(self, **kwargs) -> dict:
        """
        Get the context data for rendering the template.

        :return: Context data for rendering the template.
        """
        context = super().get_context_data(**kwargs)
        filter_type = self.request.GET.get('filter_type')
        filter_value = self.request.GET.get('filter_value')
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        day = self.request.GET.get('day')

        waste_queryset = Waste.objects.all()
        weather_queryset = Weather.objects.all()

        if year:
            waste_queryset = waste_queryset.filter(timestamp__year=year)
            weather_queryset = weather_queryset.filter(timestamp__year=year)
        if month:
            waste_queryset = waste_queryset.filter(timestamp__month=month)
            weather_queryset = weather_queryset.filter(timestamp__month=month)
        if day:
            waste_queryset = waste_queryset.filter(timestamp__day=day)
            weather_queryset = weather_queryset.filter(timestamp__day=day)

        if filter_type == 'bin_id' and filter_value and filter_value.isnumeric():
            waste_queryset = waste_queryset.filter(bin_id=filter_value)
            waste = waste_queryset.first()
            if waste:
                weather_queryset = weather_queryset.filter(
                    location=waste.bin.location)
            else:
                weather_queryset = weather_queryset.none()
        elif filter_type == 'location' and filter_value:
            waste_queryset = waste_queryset.filter(bin__location=filter_value)
            weather_queryset = weather_queryset.filter(location=filter_value)

        if day and month and year:
            (chart_data, chart_labels, temperature_data, precipitation_data,
             humidity_data, weather_data) = self.get_daily_data(
                waste_queryset, weather_queryset)
        elif month and year:
            (chart_data, chart_labels, temperature_data, precipitation_data,
             humidity_data, weather_data) = self.get_monthly_data(
                waste_queryset, weather_queryset, int(month), int(year))
        elif year:
            (chart_data, chart_labels, temperature_data, precipitation_data,
             humidity_data, weather_data) = self.get_yearly_data(
                waste_queryset, weather_queryset)
        else:
            today = date.today()
            waste_queryset = waste_queryset.filter(timestamp__contains=today)
            weather_queryset = weather_queryset.filter(
                timestamp__contains=today)
            (chart_data, chart_labels, temperature_data, precipitation_data,
             humidity_data, weather_data) = self.get_daily_data(
                waste_queryset, weather_queryset)

        context['locations'] = Bin.objects.all().values('location')
        context['bins'] = Bin.objects.all().values('bin_id')
        context['chart_data'] = chart_data
        context['chart_labels'] = chart_labels
        context['temperature_data'] = temperature_data
        context['precipitation_data'] = precipitation_data
        context['humidity_data'] = humidity_data
        context['weather_data'] = weather_data

        return context

    def get_daily_data(self, waste_queryset: QuerySet,
                       weather_queryset: QuerySet):
        """
        Get daily waste and weather data.

        :param waste_queryset: Queryset for waste data.
        :param weather_queryset: Queryset for weather data.
        :return: Data for daily waste and weather.
        """
        time = 0
        chart_data = []
        chart_labels = []
        temperature_data = []
        precipitation_data = []
        humidity_data = []
        weather_data = []
        for _ in range(6):
            chart_labels.append(f"{time:02d}:00")
            waste_level = waste_queryset.filter(timestamp__hour__gte=time,
                                                timestamp__hour__lt=time + 4) \
                .aggregate(total_waste=Sum('level'))['total_waste']
            chart_data.append(
                float(waste_level) if waste_level is not None else None)
            weather_condition = weather_queryset.filter(
                timestamp__hour__gte=time,
                timestamp__hour__lt=time + 4) \
                .aggregate(min_temp=Min("temp"),
                           max_temp=Max("temp"),
                           avg_temp=Avg("temp"),
                           min_precip=Min("precip"),
                           max_precip=Max("precip"),
                           sum_precip=Sum("precip"),
                           min_humid=Min("humid"),
                           max_humid=Max("humid"),
                           avg_humid=Avg("humid"))
            temperature_data.append(weather_condition['avg_temp'])
            precipitation_data.append(weather_condition['sum_precip'])
            humidity_data.append(weather_condition['avg_humid'])
            weather_data.append({
                "timestamp": chart_labels[-1],
                "temperature_min": weather_condition['min_temp'],
                "temperature_max": weather_condition['max_temp'],
                "temperature_avg": weather_condition['avg_temp'],
                "precipitation_min": weather_condition['min_precip'],
                "precipitation_max": weather_condition['max_precip'],
                "precipitation_total": weather_condition['sum_precip'],
                "humidity_min": weather_condition['min_humid'],
                "humidity_max": weather_condition['max_humid'],
                "humidity_avg": weather_condition['avg_humid']
            })
            time += 4
        return chart_data, chart_labels, temperature_data, precipitation_data, humidity_data, weather_data

    def get_monthly_data(self, waste_queryset: QuerySet,
                         weather_queryset: QuerySet, month: int, year: int):
        """
        Get monthly waste and weather data.

        :param waste_queryset: Queryset for waste data.
        :param weather_queryset: Queryset for weather data.
        :param month: Month for which data is to be fetched.
        :param year: Year for which data is to be fetched.
        :return: Data for monthly waste and weather.
        """
        start_date = 1
        last_date = monthrange(year, month)[1]
        chart_data = []
        chart_labels = []
        temperature_data = []
        precipitation_data = []
        humidity_data = []
        weather_data = []
        while start_date <= last_date:
            chart_labels.append(f"{year}-{month:02d}-{start_date:02d}")
            waste_level = waste_queryset.filter(timestamp__day=start_date) \
                .aggregate(total_waste=Sum('level'))['total_waste']
            chart_data.append(
                float(waste_level) if waste_level is not None else None)
            weather_condition = weather_queryset.filter(
                timestamp__day=start_date) \
                .aggregate(min_temp=Min("temp"),
                           max_temp=Max("temp"),
                           avg_temp=Avg("temp"),
                           min_precip=Min("precip"),
                           max_precip=Max("precip"),
                           sum_precip=Sum("precip"),
                           min_humid=Min("humid"),
                           max_humid=Max("humid"),
                           avg_humid=Avg("humid"))
            temperature_data.append(weather_condition['avg_temp'])
            precipitation_data.append(weather_condition['sum_precip'])
            humidity_data.append(weather_condition['avg_humid'])
            weather_data.append({
                "timestamp": chart_labels[-1],
                "temperature_min": weather_condition['min_temp'],
                "temperature_max": weather_condition['max_temp'],
                "temperature_avg": weather_condition['avg_temp'],
                "precipitation_min": weather_condition['min_precip'],
                "precipitation_max": weather_condition['max_precip'],
                "precipitation_total": weather_condition['sum_precip'],
                "humidity_min": weather_condition['min_humid'],
                "humidity_max": weather_condition['max_humid'],
                "humidity_avg": weather_condition['avg_humid']
            })
            start_date += 1
        return chart_data, chart_labels, temperature_data, precipitation_data, humidity_data, weather_data

    def get_yearly_data(self, waste_queryset: QuerySet,
                        weather_queryset: QuerySet):
        """
        Get yearly waste and weather data.

        :param waste_queryset: Queryset for waste data.
        :param weather_queryset: Queryset for weather data.
        :return: Data for yearly waste and weather.
        """
        month = 1
        chart_data = []
        chart_labels = []
        temperature_data = []
        precipitation_data = []
        humidity_data = []
        weather_data = []
        while month <= 12:
            chart_labels.append(month_name[month])
            waste_level = waste_queryset.filter(timestamp__month=month) \
                .aggregate(total_waste=Sum('level'))['total_waste']
            chart_data.append(
                float(waste_level) if waste_level is not None else None)
            weather_condition = weather_queryset.filter(timestamp__month=month) \
                .aggregate(min_temp=Min("temp"),
                           max_temp=Max("temp"),
                           avg_temp=Avg("temp"),
                           min_precip=Min("precip"),
                           max_precip=Max("precip"),
                           sum_precip=Sum("precip"),
                           min_humid=Min("humid"),
                           max_humid=Max("humid"),
                           avg_humid=Avg("humid"))
            temperature_data.append(weather_condition['avg_temp'])
            precipitation_data.append(weather_condition['sum_precip'])
            humidity_data.append(weather_condition['avg_humid'])
            weather_data.append({
                "timestamp": month_name[month],
                "temperature_min": weather_condition['min_temp'],
                "temperature_max": weather_condition['max_temp'],
                "temperature_avg": weather_condition['avg_temp'],
                "precipitation_min": weather_condition['min_precip'],
                "precipitation_max": weather_condition['max_precip'],
                "precipitation_total": weather_condition['sum_precip'],
                "humidity_min": weather_condition['min_humid'],
                "humidity_max": weather_condition['max_humid'],
                "humidity_avg": weather_condition['avg_humid']
            })
            month += 1
        return chart_data, chart_labels, temperature_data, precipitation_data, humidity_data, weather_data
