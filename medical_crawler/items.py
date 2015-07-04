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

class DiseaseDetailItem(Item):
    disease_name = Field()
    field = Field()
    content = Field()

class SymptomDetailItem(Item):
    symptom_name = Field()
    field = Field()
    content = Field()

class DiseaseQuestionItem(Item):
    disease_name = Field()
    qids = Field()

class SymptomQuestionItem(Item):
    symptom_name = Field()
    qids = Field()

class DiseaseItem(Item):
    url = Field()               # URL
    name = Field()              # 名称
    aliases = Field()           # 别名
    # summary = Field()           # 概述
    # cause = Field()             # 病因
    # symptom = Field()           # 症状
    # examination = Field()       # 检查
    # identification = Field()    # 鉴别
    # complication = Field()      # 并发症
    # prevention = Field()        # 预防
    # treat = Field()             # 治疗
    # diet = Field()              # 饮食
    # diet_tyerapy = Field()      # 食疗
    # cases = Field()             # 病例
    # experience = Field()        # 经验
    # articles = Field()          # 文章
    # questions = Field()         # 问答
    # medicines = Field()         # 药品
    related_symptoms = Field()  # 相关症状
    related_diseases = Field()  # 相关疾病


class SymptomItem(Item):
    url = Field()               # URL
    name = Field()              # 名称
    # summary = Field()           # 概述
    # cause = Field()             # 病因
    # examination = Field()       # 检查
    # identification = Field()    # 鉴别
    # prevention = Field()        # 预防
    # treat = Field()             # 治疗
    # relief = Field()            # 缓解
    # diet_tyerapy = Field()      # 食疗
    # experience = Field()        # 经验
    # articles = Field()          # 文章
    # questions = Field()         # 问答
    related_diseases = Field()  # 相关疾病
    related_symptoms = Field()  # 相关症状

class QuestionItem(Item):
    url = Field()               # URL
    qid = Field()               # 编号
    title = Field()             # 标题
    description = Field()       # 描述
    requirement = Field()       # 需求
    tags = Field()              # 标签
    related_diseases = Field()  # 疾病
    related_symptoms = Field()  # 症状
    answers = Field()           # 回答
    patient = Field()           # 病人
    date = Field()              # 时间

class PatientItem(Item):
    username = Field()          # 用户名
    age = Field()               # 年龄
    gender = Field()            # 性别
    location = Field()          # 地区

class AnswerItem(Item):
    doctor = Field()            # 医生
    content = Field()           # 回答
    addition = Field()          # 追问和回答
    date = Field()              # 时间


class MedicineItem(Item):
    pass

class HospitalItem(Item):
    pass
