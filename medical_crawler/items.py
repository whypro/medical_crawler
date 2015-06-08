# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class DepartmentItem(Item):
    name = Field()              # 名称
    parent = Field()            # 父科室
    children = Field()          # 子科室


class DiseaseItem(Item):
    names = Field()              # 名称
    summary = Field()           # 概述
    cause = Field()             # 病因
    symptom = Field()           # 症状
    examination = Field()       # 检查
    identification = Field()    # 鉴别
    complication = Field()      # 并发症
    prevention = Field()        # 预防
    treat = Field()             # 治疗
    diet = Field()              # 饮食
    diet_tyerapy = Field()      # 食疗
    cases = Field()             # 病例
    experience = Field()        # 经验
    articles = Field()          # 文章
    questions = Field()         # 问答
    medicines = Field()         # 药品
    related_symptoms = Field()  # 相关症状
    related_diseases = Field()  # 相关疾病


class SymptomItem(Item):
    name = Field()              # 名称
    summary = Field()           # 概述
    cause = Field()             # 病因
    examination = Field()       # 检查
    identification = Field()    # 鉴别
    treat = Field()             # 治疗
    diet_tyerapy = Field()      # 食疗
    experience = Field()        # 经验
    articles = Field()          # 文章
    questions = Field()         # 问答
    related_diseases = Field()  # 相关疾病
    related_symptoms = Field()  # 相关症状

class QuestionItem(Item):
    title = Field()             # 标题
    description = Field()       # 描述
    confusion = Field()         # 疑惑
    department = Field()        # 科室
    disease = Field()           # 疾病
    replies = Field()           # 回复


class MedicineItem(Item):
    pass

class HospitalItem(Item):
    pass
