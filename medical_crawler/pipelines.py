# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
import requests
import os

from medical_crawler.database import mongo_connect, mongo_close
from medical_crawler.items import DepartmentItem, DiseaseItem, SymptomItem, QuestionItem, DiseaseDetailItem, SymptomDetailItem, DiseaseQuestionItem, SymptomQuestionItem, ExaminationItem

class Pipeline(object):

    download_directory = ''
    db_name = ''

    def __init__(self):
        # get connection
        self.client = mongo_connect()
        self.db = self.client[self.db_name]

    def __del__(self):
        mongo_close(self.client)

    def save_to_file(self, url, filename):
        """
            保存至文件，返回 SHA-1
        """
        if os.path.exists(filename):
            # 文件存在，计算 SHA-1
            print 'reading {filename}'.format(filename=filename)
            with open(filename, 'rb') as f:
                data = f.read()
        else:
            print 'downloading {url}'.format(url=url)
            # TODO: Request Header
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip,deflate,sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.103 Safari/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.content
            resp.close()

            dirname = os.path.dirname(filename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            with open(filename, 'wb') as f:
                f.write(data)

        sha1 = hashlib.sha1(data).hexdigest()
        return sha1

    def gen_path(self, **kwargs):
        raise NotImplementedError


class A120askPipeline(Pipeline):
    db_name = '120ask'
    # download_directory = '/mnt/my_book/'
    db_department_collection = 'department'
    db_disease_collection = 'disease'
    db_symptom_collection = 'symptom'
    db_question_collection = 'question'
    db_examination_collection = 'examination'

    def process_item(self, item, spider):

        if spider.name != '120ask':
            return item

        if isinstance(item, DepartmentItem):
            self._process_department_item(item)
        elif isinstance(item, DiseaseItem):
            self._process_disease_item(item)
        elif isinstance(item, SymptomItem):
            self._process_symptom_item(item)
        elif isinstance(item, QuestionItem):
            self._process_question_item(item)
        elif isinstance(item, DiseaseDetailItem):
            self._process_disease_detail_item(item)
        elif isinstance(item, SymptomDetailItem):
            self._process_symptom_detail_item(item)
        elif isinstance(item, DiseaseQuestionItem):
            self._process_disease_quesiton_item(item)
        elif isinstance(item, SymptomQuestionItem):
            self._process_symptom_quesiton_item(item)
        elif isinstance(item, ExaminationItem):
            self._process_examination_item(item)

        return item

    def _process_department_item(self, item):
        department_collection = self.db[self.db_department_collection]

        if not department_collection.find_one({'name': item['name']}):
            department = dict()
            department['name'] = item['name']
            if item['parent']:
                department['parent'] = item['parent']
            if item['children']:
                department['children'] = item['children']
            # print department
            department_collection.insert(department)
        else:
            pass

    def _process_disease_item(self, item):
        disease_collection = self.db[self.db_disease_collection]

        if not disease_collection.find_one({'name': item['name']}):
            disease = dict(item)
            # disease['names'] = item['names']
            # disease['related_symptoms'] = item['related_symptoms']
            # disease['related_diseases'] = item['related_diseases']
            # print disease
            disease_collection.insert(disease)
        else:
            pass

    def _process_symptom_item(self, item):
        symptom_collection = self.db[self.db_symptom_collection]

        if not symptom_collection.find_one({'name': item['name']}):
            symptom = dict(item)
            # symptom['name'] = item['name']
            # symptom['related_diseases'] = item['related_diseases']
            # print symptom
            symptom_collection.insert(symptom)
        else:
            pass

    def _process_question_item(self, item):
        question_collection = self.db[self.db_question_collection]

        if not question_collection.find_one({'qid': item['qid']}):
            question = dict(item)
            question_collection.insert(question)
        else:
            result = question_collection.update({'qid': item['qid']}, {'$set': {'answers': item['answers']}})
            # print 'question', result.matched_count

    def _process_disease_detail_item(self, item):
        disease_collection = self.db[self.db_disease_collection]
        result = disease_collection.update({'name': item['disease_name'], item['field']: {'$exists': False}}, {'$set': {item['field']: item['content']}})
        # print 'disease_detail', result.matched_count

    def _process_symptom_detail_item(self, item):
        symptom_collection = self.db[self.db_symptom_collection]
        result = symptom_collection.update({'name': item['symptom_name'], item['field']: {'$exists': False}}, {'$set': {item['field']: item['content']}})
        # print 'symptom_detail', result.matched_count

    def _process_disease_quesiton_item(self, item):
        question_collection = self.db[self.db_question_collection]
        print item['qids']
        for qid in item['qids']:
            # print qid, item['symptom_name']
            question_collection.update({'qid': qid}, {'$addToSet': {'related_diseases': item['disease_name']}})

    def _process_symptom_quesiton_item(self, item):
        question_collection = self.db[self.db_question_collection]
        print item['qids']
        for qid in item['qids']:
            # print qid, item['symptom_name']
            question_collection.update({'qid': qid}, {'$addToSet': {'related_symptoms': item['symptom_name']}})

    def _process_examination_item(self, item):
        examination_collection = self.db[self.db_examination_collection]
        if not examination_collection.find_one({'name': item['name']}):
            examination = dict(item)
            examination_collection.insert(examination)
        else:
            pass






