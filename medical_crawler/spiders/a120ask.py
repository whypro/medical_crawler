# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from medical_crawler.items import DepartmentItem, DiseaseItem, SymptomItem


class A120askSpider(CrawlSpider):
    name = "120ask"
    allowed_domains = ["120ask.com"]
    start_urls = ('http://www.120ask.com/', )

    rules = (
        Rule(LinkExtractor(allow=(r'/jibing/\w+/$', )), callback='parse_disease', follow=True),
        Rule(LinkExtractor(allow=(r'/zhengzhuang/\w+/$', )), callback='parse_symptom', follow=True),
    )

    def parse_start_url(self, response):
        """解析【首页】"""
        _departments = response.xpath('//div[@class="left_box_bor"]/div[@class="ks_box"]')
        for _major_d in _departments:
            major_dep = DepartmentItem()
            major_dep['name'] = _major_d.xpath('strong/a/text()').extract()[0].replace('　', '')
            major_dep['children'] = []
            major_dep['parent'] = None

            for _minor_d in _major_d.xpath('ul/li/a/text()').extract():
                minor_dep = DepartmentItem()
                minor_dep['name'] = _minor_d
                minor_dep['children'] = []
                minor_dep['parent'] = major_dep['name']
                major_dep['children'].append(minor_dep['name'])

                yield minor_dep
            # end for

            # print major_dep
            yield major_dep
        # end for

    def parse_disease(self, response):
        """解析【疾病】页面"""
        disease_item = DiseaseItem()

        _name = response.xpath('//span[@class="ti"]')
        disease_item['names'] = _name.xpath('h1/a/text()').extract()
        _other_name = _name.xpath('var/text()').extract()
        if _other_name:
            begin = _other_name[0].find('：') + 1
            end = _other_name[0].rfind('）')
            disease_item['names'] += _other_name[0][begin:end].split('，')

        _related = response.xpath('//div[@id="yw4"]/div/div/div')
        disease_item['related_diseases'] = _related.xpath('ul/li/a[contains(@href, "/jibing/")]/@title').extract()
        disease_item['related_symptoms'] = _related.xpath('ul/li/a[contains(@href, "/zhengzhuang/")]/@title').extract()
        # print disease_item['related_diseases'], disease_item['related_symptoms']
        # print disease_item
        return disease_item

    def _parse_disease_cause(self, response):
        # http://tag.120ask.com/jibing/bidouyan/bingyin/
        pass

    def _parse_disease_summary(self, response):
        # http://tag.120ask.com/jibing/bidouyan/gaishu/
        pass

    def parse_symptom(self, response):
        """解析【症状】页面"""
        symptom_item = SymptomItem()
        symptom_item['name'] = response.xpath('//h3[@class="clears"]/a/b/text()').extract()[0]

        _related = response.xpath('//div[@id="yw3"]/div/div')
        symptom_item['related_diseases'] = _related.xpath('ul/li/a[contains(@href, "/jibing/")]/@title').extract()
        # symptom_item['related_symptoms'] = _related.xpath('ul/li/a[contains(@href, "/zhengzhuang/")]/@title').extract()
        # print symptom_item['related_diseases'], symptom_item['related_symptoms']
        # print symptom_item
        return symptom_item

    def parse_question(self, response):
        pass


