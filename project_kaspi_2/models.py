from django.contrib.gis.db import models
from django.contrib.gis import geos

class Venue(models.Model):
	rec_id = models.IntegerField()
	post_index = models.CharField(max_length=128, blank=True, null=True)
	region = models.CharField(max_length=128, blank=True, null=True)
	locality = models.CharField(max_length=128, blank=True, null=True)
	district = models.CharField(max_length=128, blank=True, null=True)
	street = models.CharField(max_length=128, blank=True, null=True)
	house = models.CharField(max_length=128, blank=True, null=True)

	point_str = models.CharField(max_length=64, blank=True, null=True)
	point = models.PointField(blank=True, null=True)

	def save(self, *args, **options):
		if(self.point_str):
			point = self.point_str
			point = point.replace('POINT(','')
			point = point.replace(')','')
			point = point.split(' ')
			self.point = geos.Point(float(point[0]), float(point[1]))
		return super(Venue, self).save(*args, **options)