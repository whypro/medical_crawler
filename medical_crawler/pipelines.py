# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
import requests
import os

from PIL import Image
import imagehash

from medical_crawler.database import mongo_connect, mongo_close
from medical_crawler.items import DepartmentItem, DiseaseItem, SymptomItem, QuestionItem

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

    def gen_image_hash(self, path):
        image = Image.open(path)
        dhash = imagehash.dhash(image)
        return str(dhash)


class A120askPipeline(Pipeline):
    db_name = '120ask'
    # download_directory = '/mnt/my_book/一些资料/【爬虫】/dbmeizi/photos/pics'
    db_department_collection = 'department'
    db_disease_collection = 'disease'
    db_symptom_collection = 'symptom'
    db_question_collection = 'question'

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

        return item

    def _process_department_item(self, item):
        department_collection = self.db[self.db_department_collection]

        if not department_collection.find({'name': item['name']}).count():
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

        if not disease_collection.find({'names': item['names'][0]}).count():
            disease = dict()
            disease['names'] = item['names']
            disease['related_symptoms'] = item['related_symptoms']
            disease['related_diseases'] = item['related_diseases']
            # print disease
            disease_collection.insert(disease)
        else:
            pass

    def _process_symptom_item(self, item):
        symptom_collection = self.db[self.db_symptom_collection]

        if not symptom_collection.find({'name': item['name']}).count():
            symptom = dict()
            symptom['name'] = item['name']
            symptom['related_diseases'] = item['related_diseases']
            # print symptom
            symptom_collection.insert(symptom)
        else:
            pass

    def _process_question_item(self, item):
        question_collection = self.db[self.db_question_collection]

        if not question_collection.find({'qid': item['qid']}).count():
            question = dict(item)
            question_collection.insert(question)
        else:
            pass



