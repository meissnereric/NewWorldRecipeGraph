import scrapy
from bs4 import BeautifulSoup
import json
import requests


class RecipeSpider(scrapy.Spider):
    name = 'recipes'
    base_url = 'https://nwdb.info/'
    recipe_base = 'https://nwdb.info/db/recipes/page/'
    allowed_domains = ['nwdb.info']
    start_urls = ['https://nwdb.info/db/recipes/page/1']
 #   url = start_urls[0]
 #   recipe_list = []

    def parse(self, response):
        """
        This function takes in a search page, requests all the recipes on it,
        returns the json blobs of those recipes, then loads the next webpage in
        the pagination.
        """
        print("Processing new search page:"+response.url)
        #Extract data using css selectors

        sel = scrapy.Selector(response)

        yield from self.page_recipes(sel, response)

        yield from self.load_next_page(sel, response)

    def load_next_page(self, sel, response):
        page_list=[]
        for href in sel.xpath("//a[@class='page-link']/@href").extract():
            page_list.append(href)
        print("Pagination list: ", page_list)
        if page_list[-1] == page_list[-2]:
            # you're done!
            next_page = None
            print("We're finished! All the pages! Final page: ", page_list[-2])
        else:
            next_page = next_page = response.urljoin(page_list[-2])
            print("Next page: ", page_list[-2])
            yield scrapy.Request(next_page, callback=self.parse)


    def page_recipes(self, sel, response):
    # return the json objects of all the recipes on a search page
            recipe_url_list = []
            recipe_list = []
            for href in sel.xpath("//a/@href").extract():
                if '/db/recipe/' in href:
                    recipe_url_list.append(href)

            for i, rec in enumerate(recipe_url_list):
                recipe_json = scrapy.Request(response.urljoin(rec), callback=self.parse_recipe)
                yield recipe_json
                # only will go once, return then babe
                # if i >= 1:
                #     return

    def parse_recipe(self, response):
    # returns the json object of a single recipe on the page
        self.logger.info("Visited %s", response.url)
        recipe = response.xpath('//script[@type="application/json"]').extract()[0]
        soup = BeautifulSoup(recipe, 'html.parser')
        res = soup.find('script')
        json_recipe = json.loads(res.contents[0])

        scraped_info = {
            'recipe': json_recipe['body'],
        }

        yield scraped_info
