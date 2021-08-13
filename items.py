import datetime
import scrapy
import re
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags

def get_url(url):
    return 'https://www.wildberries.ru' + url


def get_start_date(date):
    find_date = re.search('date\W+\d+\s\w+\s\d+|date\W+\d+\s\w+', date)
    try:
        bad_date = (find_date.group(0).replace('"', '').split(':')[1])
    except:
        bad_date = 0
    if bad_date != 0:
        reform_date = bad_date.split()
        days = reform_date[0]
        if len(days) == 1:
            good_days = '0' + days
        else:
            good_days = days
        month = reform_date[1]
        if month == 'января':
            month = '01'
        elif month == 'февраля':
            month = '02'
        elif month == 'марта':
            month = '03'
        elif month == 'апреля':
            month = '04'
        elif month == 'мая':
            month = '05'
        elif month == 'июня':
            month = '06'
        elif month == 'июля':
            month = '07'
        elif month == 'августа':
            month = '08'
        elif month == 'сентября':
            month = '09'
        elif month == 'октября':
            month = '10'
        elif month == 'ноября':
            month = '11'
        elif month == 'декабря':
            month = '12'
        if len(reform_date) == 3:
            year = reform_date[2]
        else:
            year = '2021'

        good_date = good_days + '.' + month + '.' + year
    else:
        day = str(datetime.date.today().day)
        month = str(datetime.date.today().month)
        year = str(datetime.date.today().year)
        good_date = day + '.' + month + '.' + year
    return good_date


def get_order_count(html):
    order = re.search(r'ordersCount\D\S\d+', html)
    sold = (int(order.group(0).split(':')[1]))
    return sold

def get_rating(html):
    find_rating = re.search(r'rating\D\S\d+', html)
    rating = (int(find_rating.group(0).split(':')[1]))
    return rating


class WbprojectItem(scrapy.Item):
    article = scrapy.Field(output_processor = TakeFirst())
    name = scrapy.Field(output_processor = TakeFirst())
    seller = scrapy.Field(output_processor = TakeFirst())
    brand = scrapy.Field(output_processor = TakeFirst())
    url = scrapy.Field(input_processor = MapCompose(get_url), output_processor = TakeFirst())
    img = scrapy.Field(output_processor = TakeFirst())
    sold = scrapy.Field(output_processor = TakeFirst())
    price = scrapy.Field(output_processor = TakeFirst())
    discount_price = scrapy.Field(output_processor = TakeFirst())
    date_start_sale = scrapy.Field(input_processor = MapCompose(get_start_date), output_processor = TakeFirst())
    rating = scrapy.Field(output_processor = TakeFirst())
