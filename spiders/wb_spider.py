import scrapy
import time
from wbproject.items import WbprojectItem
from scrapy.loader import ItemLoader

http = 'https://www.wildberries.ru'

class WbSpider(scrapy.Spider):
    name = "wb"


    start_urls = [
        'https://www.wildberries.ru/catalog/aksessuary/veera'
    ]



    def parse(self, response, **kwargs):
        for product in response.css('div.dtList-inner'):
            link_to_product = product.css('a.ref_goods_n_p::attr(href)').get()
            yield response.follow(link_to_product, callback=self.parse_product)

            # next_page = response.css('a.pagination-next::attr(href)').get()
            # if next_page is not None:
            #     yield response.follow(next_page, callback=self.parse)
            # else:
            #     pass


    def parse_product(self, response, **kwargs):

        items = {
        'name' : response.css('div.same-part-kt__header-wrap h1.same-part-kt__header span::text').get().strip(),
        'article': response.css('.same-part-kt .same-part-kt__article span:last-of-type::text').get(),
        'rating': response.css('p.same-part-kt__rating span::text').get(),
        'final_price': int(response.css('span.price-block__final-price::text').get().strip().replace('\xa0', '').replace('₽','')),
        'old_price': int(response.css('del.price-block__old-price::text').get().strip().replace('\xa0','').replace('₽','')),#!!!!
        'url': response.request.url
            }
        yield items





