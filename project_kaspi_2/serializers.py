from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from project_kaspi_2.models import Venue

class VenueGeoSerializer(GeoFeatureModelSerializer):
	class Meta:
		model = Venue
		geo_field = "point"
