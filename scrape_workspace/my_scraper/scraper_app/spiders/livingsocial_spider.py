from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose

#NOTE: HtmlXPathSelector could be a problem.  It has been deprecated and we are supposed to
#be calling scrapy.Selector instead.  Maybe try this later if you can't get the class to work.

from scraper_app.items import LivingSocialDeal

class LivingSocialSpider(BaseSpider):
    """Spider for regularly updated Livingsocial.com site"""
    name = "livingsocial_spider"
    allowed_domains = ["livingsocial.com"]
    start_urls = ['http://livingsocial.com/cities/6-chicago']
    
    deals_list_xpath = '//*/figure[@class="card-ui cui-c-udc cui-c-udc-featured-list"]'

    item_fields = {
        'title': './/div[@class="cui-content c-bdr-gray-clr"]/div[@class="cui-udc-details"]/div[@class="cui-udc-title c-txt-black two-line-ellipsis"]/text()',

        'link': './/a/@href',

        'location': './/div[@class="cui-content c-bdr-gray-clr"]/div[@class="cui-udc-details"]/div[@class="cui-udc-top-row"]/div[@class="cui-udc-left-one"]/div[@class="cui-location cui-truncate c-txt-gray-dk cui-has-distance"]/span[@class="cui-location-name"]/text()',

        'original_price': './/div[@class="cui-content c-bdr-gray-clr"]/div[@class="cui-udc-details"]/div[@class="cui-udc-bottom-row"]/div[@class="cui-udc-right-one"]/div[@class="cui-price"]/s/text()',

        'price': './/div[@class="cui-content c-bdr-gray-clr"]/div[@class="cui-udc-details"]/div[@class="cui-udc-bottom-row"]/div[@class="cui-udc-right-one"]/div[@class="cui-price"]/span/text()',

        'end_date': './/span[@itemscope]/meta[@itemprop="availabilityEnds"]/@content'

    }

    def parse(self, response):
        """
        Default callback used by Scrapy to process downloaded responses

        Testing contracts:
        @url http://livingsocial.com/cities/6-chicago
        @returns items 1
        @scrapes title link

        """

        selector = HtmlXPathSelector(response)

        # iterate over deals
        for deal in selector.select(self.deals_list_xpath):
            loader = XPathItemLoader(LivingSocialDeal(), selector=deal)

            # define processors
            loader.default_input_processor = MapCompose(unicode.strip)
            loader.default_output_processor = Join()

            # iterate over fields and add xpaths to the loader
            for field, xpath in self.item_fields.iteritems():
                loader.add_xpath(field, xpath)
            yield loader.load_item()


