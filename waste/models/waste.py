from django.db import models

from .bin import Bin


class Waste(models.Model):
    """
    Model representing waste data.
    """
    waste_id = models.IntegerField(primary_key=True, verbose_name="Waste ID")
    bin = models.ForeignKey(Bin, on_delete=models.CASCADE,
                            verbose_name="Associated Bin", db_column="bin_id")
    timestamp = models.DateTimeField(verbose_name="Timestamp")
    level = models.DecimalField(max_digits=6, decimal_places=2,
                                verbose_name="Waste Level")

    class Meta:
        managed = False
        db_table = 'waste'

    def __str__(self):
        """
        Return a string representation of the waste record.

        :return: A string containing waste ID, associated bin name, and timestamp.
        """
        return f"Waste ID: {self.waste_id}, Bin: {self.bin.name}, Timestamp: {self.timestamp}"
