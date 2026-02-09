from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex


class Point(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    location = models.PointField(srid=4326, geography=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "geo_points"
        indexes = [GistIndex(fields=["location"])]

    @property
    def latitude(self) -> float:
        return float(self.location.y)

    @property
    def longitude(self) -> float:
        return float(self.location.x)
