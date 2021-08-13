import scrapy
from wbproject.items import WbprojectItem
from scrapy.loader import ItemLoader


http = 'https://www.wildberries.ru'

class WbSpider(scrapy.Spider):
    name = "rel"
    custom_settings = {'ROTATING_PROXY_LIST_PATH': 'D:/BigProject/wildberries/proxy_http.txt'}

    start_urls = [
        'https://www.wildberries.ru/catalog/aksessuary/religioznye'
    ]

    def parse(self, response, **kwargs):
        for product in response.css('.dtList-inner'):
            url = product.css('a.ref_goods_n_p::attr(href)').get()
            name = str(product.css('.goods-name::text').get()).replace('/', '')
            brand = str(product.css('.brand-name::text').get())
            discount_price = product.css('.lower-price::text').get().replace('\xa0', '').replace('₽', '').strip()
            article = url.split('/')[2]
            link = f'https://wbx-content-v2.wbstatic.net/sellers/{article}.json'

            yield response.follow(link, callback=self.parse_seller, meta={'url': url,
                                                                          'name': name,
                                                                          'brand': brand,
                                                                          'price': discount_price,
                                                                          'article': article,
                                                                          })

        flag_np = response.css('a.pagination-next::attr(href)').get()
        if flag_np is not None:
            next_page = http + flag_np
            yield response.follow(next_page, callback=self.parse)
        else:
            pass

    def parse_seller(self, response):
        url = response.meta['url']
        name = response.meta['name']
        discount_price = response.meta['price']
        brand = response.meta['brand']
        article = response.meta['article']
        seller = response.css('p::text').get().split(',')[2].split(':')[1].replace('\\', '').replace('"', '')

        link = f'https://napi.wildberries.ru/api/catalog/{article}/detail.aspx?_app-type=sitemobile&targetUrl=ST.'

        yield response.follow(link, callback=self.parse_product, meta={'url': url,
                                                                       'name': name,
                                                                       'brand': brand,
                                                                       'discount_price': discount_price,
                                                                       'article': article,
                                                                       'seller': seller,
                                                                       })

    def parse_product(self, response):
        # это все сюда'https://napi.wildberries.ru/api/catalog/13503778/detail.aspx?_app-type=sitemobile&targetUrl=ST.'
        url = response.meta['url']
        name = response.meta['name']
        discount_price = response.meta['discount_price']
        brand = response.meta['brand']
        article = response.meta['article']
        seller = response.meta['seller']
        sold = int(response.css('p::text').re_first(f'{article},"ordersCount\D\S\d+').split(':')[1])
        rating = int(response.css('p::text').re_first('rating\D\S\d+').split(':')[1])
        img = response.css('p::text').re_first('previewUrl\D+\d+\D\d+\D\w+').split(':')[1].replace('"//', '')
        price = response.css('p::text').re_first('rawMinPrice"\D+\d+').split(':')[1].replace('"', '')
        item_id = int(response.css('p::text').re_first('feedback\D\S\d+').split('/')[1])
        brandId = int(response.css('p::text').re_first('brandId\D\S\d+').split(':')[1])

        link_to_feedback = f'https://napi.wildberries.ru/api/product/feedback/{item_id}?brandId={brandId}&page=1&order=Asc&field=Date&withPhoto=False&_app-type=sitemobile'

        yield response.follow(link_to_feedback, callback=self.parse_feedback, meta={
            'rating': rating,
            'sold': sold,
            'url': url,
            'discount_price': discount_price,
            'name': name,
            'article': article,
            'brand': brand,
            'img': img,
            'seller': seller,
            'price': price
        })

    def parse_feedback(self, response):
        for product in response.css('body'):
            l = ItemLoader(item=WbprojectItem(), selector=product)
            # начало продаж тут https://napi.wildberries.ru/api/product/feedback/25416776?brandId=147796&page=1&order=Asc&field=Date&withPhoto=False&_app-type=sitemobile
            url = response.meta['url']
            img = response.meta['img']
            sold = response.meta['sold']
            rating = response.meta['rating']
            price = response.meta['price']
            discount_price = response.meta['discount_price']
            name = response.meta['name']
            brand = response.meta['brand']
            article = response.meta['article']
            seller = response.meta['seller']

            l.add_value('img', img)
            l.add_value('seller', seller)
            l.add_value('url', url)
            l.add_css('date_start_sale', 'p')
            l.add_value('discount_price', discount_price)
            l.add_value('sold', sold)
            l.add_value('rating', rating)
            l.add_value('price', price)
            l.add_value('brand', brand)
            l.add_value('name', name)
            l.add_value('article', article)

            yield l.load_item()
