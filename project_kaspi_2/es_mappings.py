# -*- coding: utf-8 -*-

es_mappings = {
	"Venue" : {
		"properties" : {
			"region" : {
				"type" : "string",
				"analyzer": "new_analyzer",
                "search_analyzer": "new_search_analyzer"
			},
			"locality" : {
				"type" : "string",
				"analyzer": "new_analyzer",
                "search_analyzer": "new_search_analyzer"
			},
			"district" : {
				"type" : "string",
				"analyzer": "new_analyzer",
                "search_analyzer": "new_search_analyzer"
			},
            "street" : {
                "type" : "string",
                "analyzer": "new_analyzer",
                "search_analyzer": "new_search_analyzer"
            },
            "house" : {
                "type" : "string",
                "analyzer": "new_analyzer",
                "search_analyzer": "new_search_analyzer"
            }
		}
	}
}

es_ind_settings = {
    "settings": {
        "analysis" : {
            "analyzer" : {
                "new_analyzer" : {
                    "type" : "custom",
                    "tokenizer" : "standard",
                    "filter" : ["my_stopwords", "asciifolding", "lowercase", "worddelimiter", "ngram_filter"]
                },
                "new_search_analyzer" : {
                    "type" : "custom",
                    "tokenizer" : "keyword",
                    "filter" : ["my_stopwords", "asciifolding", "lowercase", "worddelimiter"]
                }
            },
            "filter" : {
                "my_stopwords" : {
                    "type" : "stop",
                    "ignore_case" : True,
                    "stopwords" : ["микрорайон","область","город","городе","район","улица","дом"]
                },
                "snowball" : {#dostaet koren slov
                    "type" : "snowball",
                    "language" : "Russian"
                },
                "stemmer" : {
                    "type" : "stemmer",
                    "language" : "russian"
                },
                "worddelimiter" : {#izbavlyaetsya ot tochek i prochih
                    "type" : "word_delimiter"
                },
                "ngram_filter": {
                    "type": "edge_ngram",
                    "min_gram": 3,
                    "max_gram": 20
                }
            }
        }
    }
}

model_es_indices = {
    "Venue": {
        'index_name': "project_kaspi_2",
        "type": "venue"
    }
}

