# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from medical_crawler.items import DepartmentItem, DiseaseItem


class A120askSpider(CrawlSpider):
    name = "120ask"
    allowed_domains = ["120ask.com"]
    start_urls = ('http://www.120ask.com/', )

    rules = (
        Rule(LinkExtractor(allow=(r'/jibing/\w+/', )), callback='parse_disease'),
    )

    # def start_requests(self):
    #     pass
    #     url = 'http://tag.120ask.com/jibing/'
    #     yield Request(url, callback=self.parse_disease)
    #
    def parse_start_url(self, response):
        _departments = response.xpath('//div[@class="left_box_bor"]/div[@class="ks_box"]')
        for _major_d in _departments:
            major_dep = DepartmentItem()
            major_dep['name'] = _major_d.xpath('strong/a/text()').extract()[0].replace('　', '')
            major_dep['children'] = []

            for _minor_d in _major_d.xpath('ul/li/a/text()').extract():
                minor_dep = DepartmentItem()
                minor_dep['name'] = _minor_d
                major_dep['children'].append(minor_dep)

                yield minor_dep

        print major_dep
        yield major_dep

    def parse_disease(self, response):
        disease_item = DiseaseItem()

        _name = response.xpath('//span[@class="ti"]')
        disease_item['names'] = _name.xpath('h1/a/text()').extract()
        _other_name = _name.xpath('var/text()').extract()
        if _other_name:
            begin = _other_name[0].find('：') + 1
            end = _other_name[0].rfind('）')
            disease_item['names'] += _other_name[0][begin:end].split('，')

        _related = response.xpath('//div[@id="yw4"]/div/div/div')
        disease_item['related_diseases'] = _related[0].xpath('ul/li/a/text()').extract()
        disease_item['related_symptoms'] = _related[1].xpath('ul/li/a/text()').extract()

        print disease_item
        return disease_item

    def _parse_disease_cause(self, response):
        # http://tag.120ask.com/jibing/bidouyan/bingyin/
        pass

    def _parse_disease_summary(self, response):
        # http://tag.120ask.com/jibing/bidouyan/gaishu/
        pass

    def parse_symptom(self, response):
        pass

    def parse_question(self, response):
        pass


