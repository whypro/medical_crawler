# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from medical_crawler.items import DepartmentItem, DiseaseItem, SymptomItem, QuestionItem


class A120askSpider(CrawlSpider):
    name = "120ask"
    allowed_domains = ["120ask.com"]
    start_urls = ('http://www.120ask.com/', )

    rules = (
        Rule(LinkExtractor(allow=(r'/jibing/\w+/$', )), callback='parse_disease', follow=True),
        Rule(LinkExtractor(allow=(r'/zhengzhuang/\w+/$', )), callback='parse_symptom', follow=True),
        Rule(LinkExtractor(allow=(r'/question/\d+\.htm$', )), callback='parse_question', follow=True),
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
        disease_item['url'] = response.url

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
        symptom_item['url'] = response.url
        symptom_item['name'] = response.xpath('//h3[@class="clears"]/a/b/text()').extract()[0]

        _related = response.xpath('//div[@id="yw3"]/div/div')
        symptom_item['related_diseases'] = _related.xpath('ul/li/a[contains(@href, "/jibing/")]/@title').extract()
        # symptom_item['related_symptoms'] = _related.xpath('ul/li/a[contains(@href, "/zhengzhuang/")]/@title').extract()
        # print symptom_item['related_diseases'], symptom_item['related_symptoms']
        # print symptom_item
        return symptom_item

    def parse_question(self, response):
        """解析【问答】页面"""
        question_item = QuestionItem()
        question_item['url'] = response.url
        question_item['qid'] = response.url.split('/')[-1].split('.')[0]
        question_item['title'] = response.xpath('//div[@class="b_askti"]/h1/text()').extract()[0]
        question_item['tags'] = response.xpath('//div[@class="b_route t10"]/a/text()').extract()[1:]
        question_item['tags'] += response.xpath('//div[@class="b_route t10"]/a/span/text()').extract()
        _content = response.xpath(u'//div[@class="b_askcont"]/p[@class="crazy_new"]')
        question_item['description'] = '\n'.join([d.strip() for d in _content.xpath('span[text()="健康咨询描述："]/parent::p/text()').extract()]).strip()
        question_item['requirement'] = '\n'.join([r.strip() for r in _content.xpath('span[text()="需要医生帮助提供远程诊断："]/parent::p/text()').extract()]).strip()

        patient = dict()
        _patient_info = response.xpath(u'//div[@class="b_askab1"]/span')
        _username = response.xpath('//div[@class="b_answerarea"]/span/a[contains(@href, "/user/")]/text()').extract()
        patient['username'] = _username[0] if _username else None
        _age = _patient_info.xpath('font[@itemprop="age"]/text()').extract()
        patient['age'] = _age[0] if _age else None
        _gender = _patient_info.xpath('font[@itemprop="gender"]/text()').extract()
        patient['gender'] = _gender[0] if _gender else None
        _location = _patient_info.xpath('font[@itemprop="location"]/text()').extract()
        patient['location'] = _location[0] if _location else None
        _date = _patient_info.xpath('font[@itemprop="post_time"]/text()').extract()
        question_item['date'] = _date[0] if _date else None
        question_item['patient'] = patient

        question_item['answers'] = []

        for _answer in response.xpath(u'//div[@class="b_answerli"]'):
            _answer_content = _answer.xpath('div[@class="b_answercont clears"]/div[@class="b_anscontc"]')
            answer = dict()
            answer['content'] = '\n'.join([c.strip() for c in _answer_content.xpath('div[@itemprop="content"]/div/p/text()').extract()]).strip()
            _date = _answer_content.xpath('span/font[@itemprop="reply_time"]/text()').extract()
            answer['date'] = _date[0] if _date else None
            _answer_title = _answer.xpath('div[@class="b_answertop clears"]/div[@class="b_answertl"]')
            doctor = dict()
            doctor['name'] = _answer_title.xpath('span/a/font/text()').extract()[0]
            _username = _answer_title.xpath('span/a/@href').extract()
            doctor['username'] = _username[0].split('/')[-1] if _username else None
            answer['doctor'] = doctor

            answer['addition'] = []

            for _addition in _answer.xpath('//div[@class="b_ansaddbox"]/div[@class="b_ansaddli"]'):
                addition = dict()
                addition['type'] = '回答' if _addition.xpath('span/@class').extract()[0] == 'b_docaddti' else '追问'
                addition['content'] = _addition.xpath('p/text()').extract()[0]
                addition['date'] = _addition.xpath('span/span/text()').extract()[0]
                # print addition['content']
                answer['addition'].append(addition)

            question_item['answers'].append(answer)

        # print question_item['description']
        # print question_item['requirement']

        # print question_item
        yield question_item




