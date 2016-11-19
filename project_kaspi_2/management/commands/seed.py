from django.core.management.base import BaseCommand
import requests
import sys
import time
import json
import threading

from project_kaspi_2.models import Venue

class Command(BaseCommand):
	
	url = "http://catalog.api.2gis.ru/geo/search"
	params = {
		'version': '1.3',
		'key': 'ruczoy1743'
	}

	success_count = 0
	error_no_results = 0
	error_connection_count = 0
	error_decode_count = 0

	start_time = 0
	
	def handle(self, *args, **options):
		Venue.objects.all().delete()
		data = []
		with open('data.json') as f:
			i = 0
			for line in f:
				i += 1
				data.append(json.loads(line))
				if(i == 250): break
		threads = []

		for item in data:
			query = unicode(item['district']) + unicode(item['street']) + unicode(item['house'])
			threads.append(threading.Thread(target=self.parseUrl, args=(query, item)))

		self.runThreads(threads)
		self.printResults()



	def printResults(self):
		print 'Success points: ' + str(self.success_count)
		print 'No results: ' + str(self.error_no_results)
		print 'Can\'t connect to Page: ' + str(self.error_connection_count)
		print 'Can\'t decode JSON:' + str(self.error_decode_count)



	def runThreads(self, threads, thread_limit=40):
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
			r = requests.get(self.url, params=params).json()
			if(r['response_code'] == "200"):
				self.saveVenue(r['result'][0], address)
				self.success_count += 1
			else:
				self.error_no_results += 1
		except requests.exceptions.ConnectionError:
			self.error_connection_count += 1
		except ValueError:
			self.error_decode_count += 1



	def saveVenue(self, point, address):
		

		rec_id = address['rec_id']
		post_index = address['post_index']
		region = address['region']
		locality = address['locality']
		house = address['house']
		district = address['district']
		street = address['street']
		point_str = point['centroid']

		try:
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
			self.success_venue_count += 1
		except:
			self.error_venue_exist += 1
		