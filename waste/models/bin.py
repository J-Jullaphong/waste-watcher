from django.db import models


class Bin(models.Model):
    """
    Model representing a waste bin.
    """
    bin_id = models.IntegerField(primary_key=True, verbose_name="Bin ID")
    name = models.CharField(max_length=100, verbose_name="Bin Name")
    location = models.CharField(max_length=100, verbose_name="Location")
    lat = models.DecimalField(max_digits=9, decimal_places=6,
                              verbose_name="Latitude")
    lon = models.DecimalField(max_digits=9, decimal_places=6,
                              verbose_name="Longitude")
    waste_type = models.CharField(max_length=50, verbose_name="Waste Type")
    capacity = models.DecimalField(max_digits=10, decimal_places=2,
                                   verbose_name="Bin Capacity")
    collect_freq = models.CharField(max_length=50,
                                    verbose_name="Collection Frequency")

    class Meta:
        managed = False
        db_table = 'bin'

    def __str__(self):
        """
        Return a string representation of the bin.

        :return: The name of the bin.
        """
        return self.name
