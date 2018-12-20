# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZjzfcgItem(scrapy.Item):

    date_id = scrapy.Field()
    # tender_code = scrapy.Field()
    prjct_name = scrapy.Field()
    prjct_code = scrapy.Field()

    prjct_desc = scrapy.Field()
    prvnce_name = scrapy.Field()
    latn_name = scrapy.Field()
    county_name = scrapy.Field()
    release_time = scrapy.Field()
    begin_time = scrapy.Field()
    end_time = scrapy.Field()
    tender_unit = scrapy.Field()
    contactor = scrapy.Field()
    contact_phone = scrapy.Field()
    purchase_money = scrapy.Field()
    agent_unit = scrapy.Field()
    agent_contactor = scrapy.Field()
    agent_phone = scrapy.Field()
    bidder_req = scrapy.Field()
    tender_note = scrapy.Field()
    open_note = scrapy.Field()
    inter_name = scrapy.Field()
    website = scrapy.Field()
    crawler_time = scrapy.Field()
    tender_detail = scrapy.Field()

