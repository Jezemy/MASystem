# coding=utf-8

'''
查询数据库
'''

from py2neo import *
import re

# 在这里修改Neo4j用户名和密码
graph = Graph("http://localhost:7474", username="neo4j",password='root')

# 读取专业词汇
'''django用第二个，普通用第一个'''
# classifier_path = '../classifier'
classifier_path = 'classifier'
disease_names = list(set([line.strip() for line in open('{classifier_path}/dict/disease.txt'.format(classifier_path=classifier_path), 'r', encoding = 'utf-8')]))
drug_names = list(set([line.strip() for line in open('{classifier_path}/dict/drug.txt'.format(classifier_path=classifier_path), 'r', encoding = 'utf-8')]))

class Disease:
	name = 'name'
	easy_get = 'easy_get'
	ill_rate = 'ill_rate'
	pic_url = 'pic_url'
	desc = 'desc'
	cause = 'cause'
	prevent = 'prevent'
	department = 'department'
	treat_way = 'treat_way'
	treat_time = 'treat_time'
	treat_rate = 'treat_rate'
	treat_cost = 'treat_cost'
	diet_good = 'diet_good'
	diet_bad = 'diet_bad'

class Drug:
	name = 'name'
	pic_url = 'pic_url'
	price = 'price'
	func = 'func'
	use = 'use'

class Recipe:
	name = 'name'
	pic_url = 'pic_url'
	produce_way = 'produce_way'

def query_disease(disease):
	'''查询所有相似名字的疾病'''
	name_list = []
	pattern = '.*{disease}.*'.format(disease=disease)
	for name in disease_names:
		ret = re.findall(pattern, name)
		if ret:
			name_list.append(ret[0])
	return name_list

def query_disease_property(disease:str, property_name:str, sure:bool=False):
	'''查找disease实体的属性'''
	if not sure:
		return query_disease(disease)

	cql = 'match (n:Disease) where n.name="{disease}" return n.{property}'.format(disease = disease, property=property_name)
	ret = graph.run(cql).data()

	# 进行属性空判断, 理论上都是匹配字典的，应该不会空，但是以防万一还是判断下
	if ret:
		ret_content = ret[0]['n.{0}'.format(property_name)]
		if ret_content:
			return {"property": ret_content}

	return {"property": ""}


def query_drug(drug:str):
	'''查找drug实体的属性'''
	cql = 'match (n:Drug) where n.name=~".*{drug}.*" return n.name'.format(drug=drug)
	ret = graph.run(cql).data()

	name_list = []
	for drug_data in ret:
		if drug_data['n.name']:
			name_list.append(drug_data['n.name'])

	return name_list

def query_drug_property(drug:str, property_name:str, sure:bool=False):
	'''查找drug实体的属性'''
	if not sure:
		return query_drug(drug)

	cql = 'match (n:Drug) where n.name="{drug}" return n.{property}'.format(drug=drug, property=property_name)
	ret = graph.run(cql).data()

	if ret:
		ret_content = ret[0]['n.{0}'.format(property_name)]
		if ret_content:
			return {"property": ret_content}

	return {"property": ""}

def query_recipe_property(recipe:str, property_name:str):
	cql = 'match (n:Recipe) where n.name="{recipe}" return n.{property}'.format(recipe = recipe, property = property_name)
	ret = graph.run(cql).data()

	if ret:
		ret_content = ret[0]['n.{0}'.format(property_name)]
		if ret_content:
			return {"property": ret_content}

	return {"property": ""}


def query_disease_rels_neopathy(disease:str, sure:bool=False):
	'''查找疾病的并发症'''
	if not sure:
		return query_disease(disease)
	cql = 'match(n:Disease)-[r:accompany_with]-(m:Disease) where n.name="{0}" return m.name'.format(disease)
	ret = graph.run(cql).data()

	name_list = []
	for neo in ret:
		if neo['m.name']:
			name_list.append(neo['m.name'])
	return name_list

def query_disease_rels_symptom(disease:str, sure:bool=False):
	'''查找疾病的症状'''
	if not sure:
		return query_disease(disease)
	cql = 'match(n:Disease)-[r:has_symptom]-(m:Symptom) where n.name="{0}" return m.name'.format(disease)
	ret = graph.run(cql).data()

	name_list = []
	for neo in ret:
		if neo['m.name']:
			name_list.append(neo['m.name'])
	return name_list

def query_disease_rels_drug(disease:str, sure:bool=False):
	'''查找疾病的推荐药品'''
	if not sure:
		return query_disease(disease)
	cql = 'match(n:Disease)-[r:recommend_drug]-(m:Drug) where n.name="{0}" return m.name'.format(disease)
	ret = graph.run(cql).data()

	name_list = []
	for neo in ret:
		if neo['m.name']:
			name_list.append(neo['m.name'])
	return name_list

def query_disease_rels_check(disease:str, sure:bool=False):
	'''查找疾病的检查项目'''
	if not sure:
		return query_disease(disease)
	cql = 'match(n:Disease)-[r:need_check]-(m:Check) where n.name="{0}" return m.name'.format(disease)
	ret = graph.run(cql).data()

	name_list = []
	for neo in ret:
		if neo['m.name']:
			name_list.append(neo['m.name'])
	return name_list

def query_disease_rels_recipe(disease:str, sure:bool=False):
	'''查找疾病的菜谱'''
	if not sure:
		return query_disease(disease)
	cql = 'match(n:Disease)-[r:recommend_diet]-(m:Recipe) where n.name="{0}" return m.name'.format(disease)
	ret = graph.run(cql).data()

	name_list = []
	for neo in ret:
		if neo['m.name']:
			name_list.append(neo['m.name'])
	return name_list

if __name__ == '__main__':
	data = query_recipe_property("西芹百合", Recipe.produce_way)
	print(data)
