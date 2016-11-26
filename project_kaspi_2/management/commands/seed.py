# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import requests
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import time
import json
import threading
from elasticsearch.client import IndicesClient
from project_kaspi_2.models import Venue
from django.conf import settings
from elasticsearch.helpers import bulk
from django.contrib.gis import geos
from project_kaspi_2.es_mappings import es_mappings, es_ind_settings, model_es_indices

class Command(BaseCommand):
	'''
	url = "http://catalog.api.2gis.ru/geo/search"
	params = {
		'version': '1.3',
		'key': 'ruczoy1743',	
	}
	'''
	url = "https://catalog.api.2gis.ru/2.0/geo/search"
	params = {
		'page': 1,
		'page_size': 12,
		'region_id': 67,
		'key': 'ruczoy1743',
		'fields': 'items.geometry.centroid'
	}

	es_index_name = 'project_kaspi_2'
	success_count = 0
	error_no_results = 0
	error_connection_count = 0
	error_decode_count = 0

	start_time = 0
	
	def handle(self, *args, **options):
		start_time = time.time()
		Venue.objects.all().delete()
		data = []
		with open('data.json') as f:
			#i = 0
			for line in f:
				#i += 1
				data.append(json.loads(line))
				#if(i == 3000): break
		threads = []

		for item in data:
			text = ''
			if (item['district'] and item['street']):
				text = unicode(item['district']) + ", "+unicode(item['street'])
			elif (item['district']): text = unicode(item['district'])
			elif (item['street']): text = unicode(item['street'])

			query = text + ", "+ item['house']
			query = query.replace('УЛИЦА ','ул ')
			query = query.replace('ГОРОД ','г ')
			query = query.replace('дом ','д ')
			query = query.replace('МИКРОРАЙОН ','мкр ')
			query = query.replace('РАЙОН В ГОРОДЕ ',' ')
			threads.append(threading.Thread(target=self.parseUrl, args=(query, item)))

		self.runThreads(threads)
		self.printResults()

		self.recreate_index()
		self.push_db_to_index()
		print '\nTotal execution time: {:.3f}'.format(time.time() - start_time) + 'sec'

	def printResults(self):
		print 'Success points: ' + str(self.success_count)
		print 'No results: ' + str(self.error_no_results)
		print 'Can\'t connect: ' + str(self.error_connection_count)
		print 'Can\'t decode JSON:' + str(self.error_decode_count)



	def runThreads(self, threads, thread_limit=50):
		process = 0.0
		length = len(threads)
		for i in range(length):
			if(i%thread_limit==0):
				for thread in threads[i-thread_limit:i]:
					thread.start()
					print '{:.3f}'.format(process/length*100) + '%'
					sys.stdout.write("\033[F")
				for thread in threads[i-thread_limit:i]:
					thread.join()
					process += 1
					print '{:.3f}'.format(process/length*100) + '%'
					sys.stdout.write("\033[F")
					
			elif(i == length-1):
				for thread in threads[(i/thread_limit)*thread_limit:i+1]:
					thread.start()
					print '{:.3f}'.format(process/length*100) + '%'
					sys.stdout.write("\033[F")
				for thread in threads[(i/thread_limit)*thread_limit:i+1]:
					thread.join()
					process += 1
					print '{:.3f}'.format(process/length*100) + '%'
					sys.stdout.write("\033[F")



	def parseUrl(self, query, address):
		params = self.params
		params['q'] = query
		try:
			r = requests.get(self.url, params=params, timeout=5).json()
			if(r['meta']['code'] == 200):
				self.saveVenue(r['result']['items'][0]['geometry'], address)
				self.success_count += 1
			else:
				self.error_no_results += 1
		except ValueError:
			self.error_decode_count += 1
		except:
			self.error_connection_count += 1



	def saveVenue(self, point, address):
		

		rec_id = address['rec_id']
		post_index = address['post_index']
		region = address['region']
		locality = address['locality']
		house = address['house']
		district = address['district']
		street = address['street']
		point_str = point['centroid']

		
		Venue(
			rec_id = rec_id,
			post_index = post_index,
			region = region,
			locality = locality,
			house = house,
			district = district,
			street = street,
			point_str = point_str
		).save()
		
	
	def recreate_index(self):
		indices_client = IndicesClient(client = settings.ES_CLIENT)
		index_name = self.es_index_name
		if indices_client.exists(index_name):
			indices_client.delete(index = index_name)
		indices_client.create(index = index_name, body = es_ind_settings)
		model_name = 'Venue'
		indices_client.put_mapping(
			doc_type=model_es_indices[model_name]['type'],
			body=es_mappings[model_name],
			index=index_name
			)

	def push_db_to_index(self):
		data = [self.convert_for_bulk(venue, 'create') for venue in Venue.objects.all()]
		bulk(client=settings.ES_CLIENT, actions=data, stats_only=True)
	
	def convert_for_bulk(self, django_object, action = None):
		data = django_object.es_repr()
		metadata = {
			'_op_type': action,
			'_index': model_es_indices[django_object.__class__.__name__]['index_name'],
			'_type': model_es_indices[django_object.__class__.__name__]['type']
		}
		data.update(**metadata)
		return data