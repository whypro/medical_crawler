# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from urlparse import urljoin
from HTMLParser import HTMLParser

from scrapy.http.request import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ..items import DepartmentItem, DiseaseItem, SymptomItem, QuestionItem, DiseaseDetailItem, SymptomDetailItem, DiseaseQuestionItem, SymptomQuestionItem
from ..items import ExaminationItem, MedicationItem, SurgeryItem

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class A120askSpider(CrawlSpider):
    name = "120ask"
    allowed_domains = ["120ask.com"]
    start_urls = (
        'http://www.120ask.com/', 
        'http://tag.120ask.com/jibing/', 'http://tag.120ask.com/zhengzhuang/', 
        'http://tag.120ask.com/jiancha/', 'http://tag.120ask.com/shoushu/',
        'http://yp.120ask.com/',
    )

    rules = (
        ##Rule(LinkExtractor(allow=(r'tag\.120ask\.com/jibing/\w+/$', )), callback='parse_disease', follow=True),
        ##Rule(LinkExtractor(allow=(r'tag\.120ask\.com/zhengzhuang/\w+/$', )), callback='parse_symptom', follow=True),
        # Rule(LinkExtractor(allow=(r'/question/\d+\.htm$', )), callback='parse_question', follow=True),
        Rule(LinkExtractor(allow=(r'/shoushu/\d+\.html$', )), callback='parse_surgery', follow=True),
        # Rule(LinkExtractor(allow=(r'tag\.120ask\.com/jiancha/\d+$', )), callback='parse_examination', follow=True),
        # Rule(LinkExtractor(allow=(r'yp\.120ask\.com/detail/\d+\.html$', )), callback='parse_medication', follow=True),
    )

    _detail_url_map = {
        'gaishu': 'summary',
        'bingyin': 'cause',
        'zhengzhuang': 'symptom',
        'jiancha': 'examination',
        'jianbie': 'identification',
        'bingfa': 'complication',
        'yufang': 'prevention',
        'zhiliao': 'treat',
        'yinshi': 'diet',
        'huanjie': 'relief',
    }

    _surgery_detail_url_map = {
        'shiying': 'symptom',
        'bingfa': 'complication',
        'jinji': 'contraindications',
        'buzhou': 'process',
        'zhunbei': 'before',
        'huli': 'after',
        'zhuyi': 'precautions',
        'baojia': 'cost',
    }

    def __init__(self):
        super(A120askSpider, self).__init__()
        self._disease_key_gen = None
        self._symptom_key_gen = None

    def parse_start_url(self, response):
        """解析【首页】"""

        _departments = response.xpath('//div[@class="sick_LI"]/strong')

        for _major_d in _departments:
            major_dep = DepartmentItem()
            major_dep['name'] = _major_d.xpath('a/text()').extract()[0].replace('　', '')
            print major_dep['name']
            major_dep['children'] = []
            major_dep['parent'] = None

            for _minor_d in _major_d.xpath('../following-sibling::div[@class="sick_Lihide"]/ul/li/b/a/text()').extract():
                minor_dep = DepartmentItem()
                minor_dep['name'] = _minor_d
                print minor_dep['name']
                minor_dep['children'] = []
                minor_dep['parent'] = major_dep['name']
                major_dep['children'].append(minor_dep['name'])

                yield minor_dep
            # end for
            print 

            # print major_dep
            yield major_dep
        # end for

    def parse_disease(self, response):
        """解析【疾病】页面"""
        disease_item = DiseaseItem()
        disease_item['url'] = response.url

        _name = response.xpath('//div[@class="p_lbox1"]/div[@class="p_lboxti"]/h3')
        disease_item['name'] = _name.xpath('text()').extract()[0]
        _other_name = _name.xpath('var/text()').extract()
        if _other_name:
            begin = _other_name[0].find('：') + 1
            end = _other_name[0].rfind('）')
            disease_item['aliases'] = re.split('，|,', _other_name[0][begin:end])

        _related = response.xpath('//div[@id="yw4"]/div/div/div')
        disease_item['related_diseases'] = _related.xpath('ul/li/a[contains(@href, "/jibing/")]/@title').extract()
        disease_item['related_symptoms'] = _related.xpath('ul/li/a[contains(@href, "/zhengzhuang/")]/@title').extract()
        # print disease_item['related_diseases'], disease_item['related_symptoms']
        # print disease_item
        yield disease_item

        # Go on parsing details
        detail_urls = response.xpath('//div[@class="p_lbox1_ab"]/a/@href').extract()
        detail_urls += response.xpath('//ul[@class="p_sibox2ul clears"]/li/a/@href').extract()
        # print detail_urls
        for url in detail_urls:
            request = Request(url=url, dont_filter=True, callback=self._parse_disease_detail)
            request.meta['disease_item'] = disease_item
            yield request

        # Go on parsing questions
        question_url = response.xpath('//div[@class="p_lbox5"]/div[@class="p_lboxti"]/a/@href').extract()[0]
        request = Request(url=question_url, dont_filter=True, callback=self._parse_disease_question)
        request.meta['disease_item'] = disease_item
        # print request
        yield request

    def _parse_disease_question(self, response):
        disease_question_item = response.meta.get('disease_questions')
        if not disease_question_item:
            disease_question_item = DiseaseQuestionItem()
            disease_question_item['disease_name'] = response.meta['disease_item']['name']
            disease_question_item['qids'] = []

        # parse
        urls = response.xpath('//div[@class="p_list_li"]/div[@class="p_list_cent"]/div[@class="p_list_centt"]/dl/dt/a/@href').extract()
        disease_question_item['qids'] += [u.split('/')[-1].split('.')[0] for u in urls]

        # last_url = response.xpath('//div[@class="portldet-content"]/a/@href').extract()[-1]
        next_url = response.xpath('//div[@class="portlet-content"]/a[text()="下一页 >"]/@href').extract()
        if not next_url:
             # 所有页都处理完了
            print disease_question_item
            yield disease_question_item
        else:
            url = next_url[0]
            # print url
            # print disease_question_item['qids']
            request = Request(url, dont_filter=True, callback=self._parse_disease_question)
            request.meta['disease_questions'] = disease_question_item
            # print request
            yield request

    def _parse_disease_detail(self, response):
        # http://tag.120ask.com/jibing/bidouyan/bingyin/
        # print response.url
        disease_item = response.meta['disease_item']
        key = response.url.split('/')[-2]
        field = self._detail_url_map[key]
        content = strip_tags('\n'.join(response.xpath('//div[@class="p_cleftartbox"]/div[@class="p_arttopab clears"]/following-sibling::*').extract())).strip()
        # print content
        if not content:
            self.logger.error('Empty disease detail content, url: {0}, response status: {1}'.format(response.url, response.status))
            return None
        disease_detail_item = DiseaseDetailItem()
        disease_detail_item['disease_name'] = disease_item['name']
        disease_detail_item['field'] = field
        disease_detail_item['content'] = content
        return disease_detail_item

    def parse_symptom(self, response):
        """解析【症状】页面"""
        symptom_item = SymptomItem()
        symptom_item['url'] = response.url
        symptom_item['name'] = response.xpath('//div[@id="m_1"]/div[@class="p_sibox1 p_siboxbor"]/div[@class="p_sititile"]/span/h1/text()').extract()[0]

        _related = response.xpath('//div[@id="yw3"]/div/div')
        symptom_item['related_diseases'] = _related.xpath('ul/li/a[contains(@href, "/jibing/")]/@title').extract()
        # symptom_item['related_symptoms'] = _related.xpath('ul/li/a[contains(@href, "/zhengzhuang/")]/@title').extract()
        # print symptom_item['related_diseases'], symptom_item['related_symptoms']
        # print symptom_item
        yield symptom_item

        # Go on parsing details
        detail_urls = response.xpath('//dl[@class="p_sibox1dl clears"]/dt/a/@href').extract()
        detail_urls += response.xpath('//ul[@class="p_sibox2ul clears"]/li/a[1]/@href').extract()
        # print detail_urls
        for url in detail_urls:
            request = Request(url=url, dont_filter=True, callback=self._parse_symptom_detail)
            request.meta['symptom_item'] = symptom_item
            yield request

        # Go on parsing questions
        question_url = response.xpath('//div[@class="p_sibox4 p_siboxbor"]/div[@class="p_sititile"]/a/@href').extract()[0]
        request = Request(url=question_url, dont_filter=True, callback=self._parse_symptom_question)
        request.meta['symptom_item'] = symptom_item
        # print request
        yield request

    def _parse_symptom_question(self, response):
        symptom_question_item = response.meta.get('symptom_questions')
        # print response.url
        if not symptom_question_item:
            symptom_question_item = SymptomQuestionItem()
            symptom_question_item['symptom_name'] = response.meta['symptom_item']['name']
            symptom_question_item['qids'] = []

        # parse
        urls = response.xpath('//div[@class="p_list_li"]/div[@class="p_list_cent"]/div[@class="p_list_centt"]/dl/dt/a/@href').extract()
        symptom_question_item['qids'] += [u.split('/')[-1].split('.')[0] for u in urls]

        # last_url = response.xpath('//div[@class="portldet-content"]/a/@href').extract()[-1]
        next_url = response.xpath('//div[@class="portlet-content"]/a[text()="下一页 >"]/@href').extract()
        if not next_url:
             # 所有页都处理完了
            print symptom_question_item
            yield symptom_question_item
        else:
            url = next_url[0]
            # print url
            # print symptom_question_item['qids']
            request = Request(url, dont_filter=True, callback=self._parse_symptom_question)
            request.meta['symptom_questions'] = symptom_question_item
            # print request
            yield request


    def _parse_symptom_detail(self, response):
        # http://tag.120ask.com/jibing/bidouyan/bingyin/
        # print response.url
        symptom_item = response.meta['symptom_item']
        key = response.url.split('/')[-2]
        field = self._detail_url_map[key]
        content = strip_tags('\n'.join(response.xpath('//div[@class="p_cleftartbox"]/div[@class="p_arttopab clears"]/following-sibling::*').extract())).strip()
        # print content
        if not content:
            self.logger.error('Empty symptom detail content, url: {0}, response status: {1}'.format(response.url, response.status))
            return None
        symptom_detail_item = SymptomDetailItem()
        symptom_detail_item['symptom_name'] = symptom_item['name']
        symptom_detail_item['field'] = field
        symptom_detail_item['content'] = content
        return symptom_detail_item

    def parse_question(self, response):
        """解析【问答】页面"""
        question_item = QuestionItem()
        question_item['url'] = response.url
        question_item['qid'] = response.url.split('/')[-1].split('.')[0]
        question_item['title'] = response.xpath('//h1[@id="d_askH1"]/text()').extract()[0]
        question_item['tags'] = response.xpath('//div[@class="b_route"]/a/text()').extract()[1:]
        question_item['tags'] += response.xpath('//div[@class="b_route"]/a/span/text()').extract()
        _content = response.xpath(u'//div[@id="d_msCon"]/p[@class="crazy_new"]')
        question_item['description'] = '\n'.join([d.strip() for d in _content.xpath('span[text()="健康咨询描述："]/parent::p/text()').extract()]).strip()
        question_item['requirement'] = '\n'.join([r.strip() for r in _content.xpath('span[text()="需要医生帮助提供远程诊断："]/parent::p/text()').extract()]).strip()

        patient = dict()

        _username = response.xpath('//div[@class="b_answerarea"]/span/a[contains(@href, "/user/")]/text()').extract()
        if _username:
            patient['username'] = _username[0]

        for _patient_info in response.xpath(u'//div[@class="b_askab1"]/span/text()').extract():
            # print _patient_info
            m = re.match(r'(男|女) \| (\d+岁)', _patient_info)
            if m:
                patient['gender'], patient['age'] = _patient_info.split(' | ')
                continue
            m = re.match(r'来自(.+)', _patient_info)
            if m:
                patient['location'] = m.group(1)
                continue
            m = re.match(r'\d{4}-\d{2}\-\d{2} \d{2}\:\d{2}\:\d{2}', _patient_info)
            if m:
                question_item['date'] = _patient_info
                continue

        # _age = _patient_info.xpath('font[@itemprop="age"]/text()').extract()
        # if _age:
        #     patient['age'] = _age[0]

        # _gender = _patient_info.xpath('font[@itemprop="gender"]/text()').extract()
        # if _gender:
        #     patient['gender'] = _gender[0]

        # _location = _patient_info.xpath('font[@itemprop="location"]/text()').extract()
        # if _location:
        #     patient['location'] = _location[0]

        # _date = _patient_info.xpath('font[@itemprop="post_time"]/text()').extract()
        # if _date:
        #     question_item['date'] = _date[0]

        question_item['patient'] = patient

        question_item['answers'] = []

        for _answer in response.xpath(u'//div[@class="b_answerli"]'):
            _answer_content = _answer.xpath('div/div[@class="b_anscontc"]')
            answer = dict()
            answer['content'] = '\n'.join([c.strip() for c in _answer_content.xpath('div[@class="b_anscont_cont"]/div/p/text()').extract()]).strip()

            _date = _answer_content.xpath('span[@class="b_anscont_time"]/text()').extract()
            if _date:
                answer['date'] = _date[0]

            _answer_title = _answer.xpath('div[@class="b_answertop clears"]/div[@class="b_answertl"]')
            doctor = dict()
            # print _answer_title.xpath('span//font[@itemprop="name"]/text()').extract()
            _name = _answer_title.xpath('span[@class="b_sp1"]/a/text()').extract()
            if _name:
                doctor['name'] = _name[0]
            else:
                _name = _answer_title.xpath('span[@class="b_sp1"]/var/text()').extract()
                if _name:
                    doctor['name'] = _name[0]

            _username = _answer_title.xpath('span/a/@href').extract()
            if _username:
                doctor['username'] = _username[0].split('/')[-1]

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
        return question_item

    def parse_examination(self, response):
        """解析【检查】页面"""
        examination_item = ExaminationItem()
        examination_item['url'] = response.url
        examination_item['name'] = response.xpath('//div[@class="w_cl1"]/h1[@class="h1 clears"]/@title').extract()[0]
        examination_item['introduction'] = strip_tags('\n'.join(response.xpath('//div[@class="w_cl1"]/div[@class="w_cll"]/div[1]/h3/following-sibling::*').extract())).strip()
        examination_item['normal_value'] = strip_tags('\n'.join(response.xpath('//div[@class="w_cl1"]/div[@class="w_cll"]/div[2]/h3/following-sibling::*').extract())).strip()
        examination_item['clinical_significance'] = strip_tags('\n'.join(response.xpath('//div[@class="w_cl1"]/div[@class="w_cll"]/div[3]/h3/following-sibling::*').extract())).strip()
        examination_item['precautions'] = strip_tags('\n'.join(response.xpath('//div[@class="w_cl1"]/div[@class="w_cll"]/div[4]/h3/following-sibling::*').extract())).strip()
        examination_item['process'] = strip_tags('\n'.join(response.xpath('//div[@class="w_cl1"]/div[@class="w_cll"]/div[5]/h3/following-sibling::*').extract())).strip()
        examination_item['cost'] = strip_tags('\n'.join(response.xpath('//div[@class="w_cl1"]/div[@class="w_cll"]/div[6]/h3/following-sibling::*').extract())).strip()
        print examination_item
        yield examination_item

    def parse_medication(self, response):
        """解析【药物】页面"""
        medication_item =  MedicationItem()
        medication_item['url'] = response.url

        _introduction = response.xpath('//div[@class="drugDecri"]/div[@class="box"]')
        _generic_name = _introduction.xpath('p[1]/var/i[1]/text()').extract()
        if _generic_name:
            medication_item['generic_name'] = _generic_name[0]
        _trade_name = _introduction.xpath('p[1]/var/i[2]/text()').extract()
        if _trade_name:
            medication_item['trade_name'] = _trade_name[0]
        _ingredient = _introduction.xpath('p[2]/var/text()').extract()
        if _ingredient:
            medication_item['ingredient'] = _ingredient[0]
        _description = _introduction.xpath('p[3]/var/text()').extract()
        if _description:
            medication_item['description'] = _description[0]
        _indications = _introduction.xpath('p[4]/var/text()').extract()
        if _indications:
            medication_item['indications'] = _indications[0]
        _disease = _introduction.xpath('p[5]/var/text()').extract()
        if _disease:
            medication_item['disease'] = _disease[0]
        _specification = _introduction.xpath('p[6]/var/text()').extract()
        if _specification:
            medication_item['specification'] = _specification[0]
        _dosage = _introduction.xpath('p[7]/var/text()').extract()
        if _dosage:
            medication_item['dosage'] = _dosage[0]
        _adverse_reactions = _introduction.xpath('p[8]/var/text()').extract()
        if _adverse_reactions:
            medication_item['adverse_reactions'] = _adverse_reactions[0]
        _contraindications = _introduction.xpath('p[9]/var/text()').extract()
        if _contraindications:
            medication_item['contraindications'] = _contraindications[0]
        _precautions = _introduction.xpath('p[10]/var/text()').extract()
        if _precautions:
            medication_item['precautions'] = _precautions[0]
        _interactions = _introduction.xpath('p[11]/var/text()').extract()
        if _interactions:
            medication_item['interactions'] = _interactions[0]
        _preservation = _introduction.xpath('p[12]/var/text()').extract()
        if _preservation:
            medication_item['preservation'] = _preservation[0]
        _term_of_validity = _introduction.xpath('p[13]/var/text()').extract()
        if _term_of_validity:
            medication_item['term_of_validity'] = _term_of_validity[0]
        
        yield medication_item

    def parse_surgery(self, response):
        print response.url
        surgery_item = SurgeryItem()
        surgery_item['url'] = response.url
        surgery_item['name'] = response.xpath('//div[@class="w_n"]/h3/text()').extract()[0]
        surgery_item['summary'] = response.xpath('//dd[@class="w_d3"]/text()').extract()[0]

        # Go on parsing details
        _next = response.xpath('//div[@class="w_n"]/div[@class="w_na clears"]/a[@class="hover"]/following-sibling::a[not(@class="w_la")][1]/@href').extract()
        next_detail_url = urljoin(response.url, _next[0])
        request = Request(url=next_detail_url, dont_filter=True, callback=self._parse_surgery_detail)
        request.meta['surgery_item'] = surgery_item
        yield request

    def _parse_surgery_detail(self, response):
        print response.url
        surgery_item = response.meta['surgery_item']
        key = response.url.split('/')[-1].split('.')[0]
        field = self._surgery_detail_url_map[key]
        print surgery_item['name'], key, field
        surgery_item[field] = strip_tags('\n'.join(response.xpath('//div[@class="w_contl fl"]/h3/following-sibling::*').extract())).strip()

        _next = response.xpath('//div[@class="w_n"]/div[@class="w_na clears"]/a[@class="hover"]/following-sibling::a[not(@class="w_la")][1]/@href').extract()
        if _next:
            next_detail_url = urljoin(response.url, _next[0])
            request = Request(url=next_detail_url, dont_filter=True, callback=self._parse_surgery_detail)
            request.meta['surgery_item'] = surgery_item
            yield request
        else:
            yield surgery_item