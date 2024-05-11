from django.db import models


class Weather(models.Model):
    """
    Model representing weather data.
    """
    weather_id = models.IntegerField(primary_key=True,
                                     verbose_name="Weather ID")
    timestamp = models.DateTimeField(verbose_name="Timestamp")
    location = models.CharField(max_length=100, verbose_name="Location")
    lat = models.DecimalField(max_digits=9, decimal_places=6,
                              verbose_name="Latitude")
    lon = models.DecimalField(max_digits=9, decimal_places=6,
                              verbose_name="Longitude")
    temp = models.DecimalField(max_digits=5, decimal_places=2,
                               verbose_name="Temperature")
    precip = models.DecimalField(max_digits=5, decimal_places=2,
                                 verbose_name="Precipitation")
    humid = models.DecimalField(max_digits=5, decimal_places=2,
                                verbose_name="Humidity")

    class Meta:
        managed = False
        db_table = 'weather_api'

    def __str__(self):
        """
        Return a string representation of the weather record.

        :return: A string containing weather ID, location, and timestamp.
        """
        return f"Weather ID: {self.weather_id}, Location: {self.location}, Timestamp: {self.timestamp}"
