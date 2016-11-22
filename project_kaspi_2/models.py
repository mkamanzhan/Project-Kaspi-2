from django.contrib.gis.db import models
from django.contrib.gis import geos
from project_kaspi_2.es_mappings import es_mappings, es_ind_settings, model_es_indices
from django.conf import settings
import json


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
			self.point = geos.Point(float(point[1]), float(point[0]))
		return super(Venue, self).save(*args, **options)
	
	def es_repr(self):
		data = {}
		mapping = es_mappings[self.__class__.__name__]
		data['_id'] = self.pk
		for field_name in mapping['properties'].keys():
			data[field_name] = self.field_es_repr(field_name)
		return data	
	
	def field_es_repr(self, field_name):
		mapping = es_mappings[self.__class__.__name__]
		config = mapping['properties'][field_name]
		field_es_value = getattr(self, field_name)
		return field_es_value
	
	@classmethod
	def get_es_index(cls):
		return model_es_indices[cls.__name__]['index_name']
	
	@classmethod
	def get_es_type(cls):
		return model_es_indices[cls.__name__]['type']
	
	@classmethod
	def es_search(cls, term, srch_fields=['region','area','locality','district','street','house']):
		es = settings.ES_CLIENT
		query = cls.gen_query(term, srch_fields)
		recs = []
		res = es.search(index=cls.get_es_index(), doc_type=cls.get_es_type(), body=query)
		if res['hits']['total'] > 0:
			print 'found %s' % res['hits']['total']
			ids = [c['_id'] for c in res['hits']['hits']]
			clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(ids)])
			ordering = 'CASE %s END' % clauses
			recs = cls.objects.filter(id__in=ids).extra(select={'ordering': ordering}, order_by=('ordering',))
		return recs

	@classmethod
	def gen_query(cls, term, srch_fields):
		query = {
			"query": {
                "filtered": {
                    "query": {
                        "bool": {
                            "should": [
                            	{ "multi_match": {
                                    "type": "cross_fields",
                                    "fields": ["street", "house"],
                                    "fuzziness": "AUTO",
                                    "query": term,
                                    "boost": 10
                                } },
                                { "multi_match": {
                                    "type": "cross_fields",
                                    "fields": ["district"],
                                    "fuzziness": "AUTO",
                                    "query": term,
                                    "boost": 5
                                } },
                                { "multi_match": {
                                    "type": "cross_fields",
                                    "fields": ["region","locality"],
                                    "query": term
                                } }
                            ]
                        }
                    }
                }
            },
            "size": 50
		}
		return json.dumps(query)

