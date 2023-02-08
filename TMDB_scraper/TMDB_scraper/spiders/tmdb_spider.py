#!/usr/bin/env python
# coding: utf-8

# In[7]:


# to run 
# scrapy crawl tmdb_spider -o movies.csv

import scrapy


import requests 
from random import randint

# I tried to get result.csv, I always got a empty csv file. 
# I do some search online and found it is a 403 Forbidden Error.
# The solution is need to requests fake user agent API, so I refer to the code of this website:
# https://scrapeops.io/docs/fake-user-agent-headers-api/integrations/python-requests/

def get_user_agent_list():
    API_KEY = '73c17bd8-df5e-4c16-9731-e27653449214'
    response = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=' + API_KEY)
    json_response = response.json()
    return json_response.get('result', [])

def get_random_user_agent(user_agent_list):
    random_index = randint(0, len(user_agent_list) - 1)
    return user_agent_list[random_index]

# Retrieve User-Agent List From ScrapeOps
user_agent_list = get_user_agent_list()

## Add Random User-Agent To Headers
headers = {'User-Agent': get_random_user_agent(user_agent_list)}



# Creating class that will inherite from scrapy.Spider
class TmdbSpider(scrapy.Spider):
    
    #define spider name
    name = 'tmdb_spider' 
    
    #the url that we would use scrapy on it.
    start_urls = ['https://www.themoviedb.org/movie/207703-kingsman-the-secret-service']

    def start_requests(self):
        '''
            Goals:
            1, Start our request
            2, Input the start url and add headers to object: scrapy.Request.
            3, Navigate to the page of the movie we want.
        '''
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers)
    
    
    def parse(self, response):
        '''
            Goals:
            1, Parse movie's page. 
            2, Find the full cast & crew link.
            3, Navigate to the full cast & crew page.
        '''
        
        # Find the Full Cast & Crew link and navigate that page.
        cast_page_link = response.css("p.new_button a::attr(href)").get()
        yield scrapy.Request(url = "https://www.themoviedb.org" + cast_page_link,
                            headers=headers,
                            callback=self.parse_full_credits)

    def parse_full_credits(self, response):
        '''
            Goals:
            1, Parse the full cast & crew page.
            2, Find all actors' links.
            3, Navigate to the actors' pages respectively.
        '''

        # Find the link of all the actors.
        actors_links = response.css("ol[class='people credits '] p[class!='character'] a::attr(href)").getall()
        for actor_link in actors_links:  
            yield scrapy.Request(url = "https://www.themoviedb.org" + actor_link,
                                headers=headers,
                                callback=self.parse_actor_page)


    def parse_actor_page(self, response):
        '''
            Goals:
            1, Parse each actor page.
            2, Collete the actor name, and all movies' name which he/she has acted in.
            3, Output dictionaries containing the actor name and the movie name.
        '''

        # Collete actor name
        name = response.css("h2.title a::text").get()
        
        # Collete all movies' name which he/she has acted in.
        movies = response.css("table.credit_group a.tooltip bdi::text").getall()
        
        # Finalizes the work of parsing
        for movie in movies:
            yield{"actor name":name,
                  "movie name":movie}

