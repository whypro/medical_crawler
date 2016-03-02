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


class MedicationItem(Item):
    url = Field()               # URL
    generic_name = Field()      # 通用名称
    trade_name = Field()        # 商用名称
    ingredient = Field()        # 主要成份
    description = Field()       # 性状
    indications = Field()       # 适应症
    disease = Field()           # 主治疾病
    specification = Field()     # 规格
    dosage = Field()            # 用法用量
    adverse_reactions = Field() # 不良反应
    contraindications = Field() # 禁忌
    precautions = Field()       # 注意事项
    interactions = Field()      # 药物相互作用
    preservation = Field()      # 贮藏
    term_of_validity = Field()  # 有效期


class ExaminationItem(Item):
    url = Field()               # URL
    name = Field()              # 名称
    introduction = Field()      # 介绍
    normal_value = Field()      # 正常值
    clinical_significance = Field() # 临床意义
    precautions = Field()       # 注意事项
    process = Field()           # 检查过程
    cost = Field()              # 一般费用


class SurgeryItem(Item):
    url = Field()               # URL
    name = Field()              # 名称
    summary = Field()           # 概述
    symptom = Field()           # 适应症
    complication = Field()      # 并发症
    contraindications = Field() # 禁忌
    process = Field()           # 步骤
    before = Field()            # 术前准备
    after = Field()             # 术后护理
    precautions = Field()       # 注意事项
    cost = Field()              # 报价

