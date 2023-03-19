# coding=utf-8

'''
这里的工作是从保存的json文件中取出内容进行处理
构建图先构建实体，再建立联系。

实体存入neo4j只需要存自己的属性，涉及的其他实体都是关系
关系从disease的json文件中找到关系
'''

import json
from py2neo import *
from collections import defaultdict
import re
import time

class Build_Graph:

	# 静态成员变量
	disease = 'disease'
	symptom = 'symptom'
	drug = 'drug'
	recipe = 'recipe'
	check = 'check'

	# 联系类型
	disease_rel_recipe = 'recommend_diet'
	disease_rel_neopathy = 'accompany_with'
	disease_rel_check = 'need_check'
	disease_rel_symptom = 'has_symptom'
	disease_rel_drug = 'recommend_drug'

	def __init__(self):
		self.graph = Graph("http://localhost:7474", username="neo4j",password='root')
		# self._delete_origin_database()
		self.start_time = time.clock()

	def _extract_id(self, text: str):
		'''将id从字符串中抽出，用于a标签的href属性'''
		return re.search("[0-9]+", text).group()

	def _delete_origin_database(self):
		print('正在清空当前数据库...')
		self.graph.delete_all()
		print('清除原数据库成功')

	def _extract_data(self, fileName):
		'''从json中取出每一行信息'''
		for line in open('entities/{fn}.json'.format(fn=fileName), 'r', encoding = 'utf-8'):
			data = json.loads(line.strip())
			# 转化成defaultDict 避免错误, 如果取不到key的话可以获得到一个空的字符串
			dd = defaultdict(str)
			dd.update(data)
			yield dd

	def _build_entities(self):
		'''创建Disease实体'''

		for data in self._extract_data(Build_Graph.disease):
			print("Disease: ", data['name'])
			disease = Node('Disease',
			               d_id = data['id'],
			               name = data['name'],
			               easy_get = data['easy_get'],
			               ill_rate = data['ill_rate'],
			               pic_url = data['pic_url'],
			               desc = data['desc'],
			               cause = data['cause'],
			               prevent = data['prevent'],
			               department = data['department'],
			               treat_way = data['treat_way'],
			               treat_time = data['treat_time'],
			               treat_rate = data['treat_rate'],
			               treat_cost = data['treat_cost'],
			               diet_good = data['diet_good'],
			               diet_bad = data['diet_bad'] )
			self.graph.create(disease)

		'''创建Drug实体'''
		for data in self._extract_data(Build_Graph.drug):
			print("Drug: ", data['name'])
			drug = Node('Drug',
			            dg_id = data['id'],
			            name = data['name'],
			            pic_url = data['pic_url'],
			            price = data['price'],
			            func = data['func'],
			            use = data['use'],)
			self.graph.create(drug)

		'''创建symptom实体'''
		for data in self._extract_data(Build_Graph.symptom):
			print("Symptom: ", data['name'])
			symptom = Node('Symptom',
			            sm_id = data['id'],
			            name = data['name'])
			self.graph.create(symptom)

		'''创建check实体'''
		for data in self._extract_data(Build_Graph.check):
			print("Check: ", data['name'])
			check = Node('Check',
			            ck_id = data['id'],
			            desc = data['desc'],
			            name = data['name'])
			self.graph.create(check)

		'''创建recipe实体'''
		for data in self._extract_data(Build_Graph.recipe):
			print("Recipe: ", data['name'])
			recipe = Node('Recipe',
			            rp_id = data['id'],
			            name = data['name'],
			            pic_url = data['pic_url'],
			            produce_way = data['produce_way'],)
			self.graph.create(recipe)

	def _test_build_relationship(self):
		# 大致看看会不会有匹配不上的关系，或者看看有什么其他问题
		for data in self._extract_data(Build_Graph.disease):
			# disease = self.graph.nodes.match('Disease', d_id = data['id']).first()
			# 测试并发症是不是都能在数据库找到对应实体
			# if data['neopathy']:
			# 	for neo in data['neopathy']:
			# 		neo_id = neo['neo_id']
			# 		neo_name = neo['neo_name']
			# 		neopathy = self.graph.nodes.match("Disease", d_id=neo_id, name=neo_name).first()
			# 		if neopathy:
			# 			print(neo_id, neo_name)
			# 			print(neopathy['d_id'], neopathy['name'])

			# 测试检查项目是不是都能在数据库找到对应实体
			# if data['checkes']:
			# 	for ck in data['checkes']:
			# 		ck_id = self._extract_id(ck['ck_url'])
			# 		ck_name = ck['ck_name']
			# 		check = self.graph.nodes.match("Check", ck_id=ck_id, name=ck_name).first()
			# 		if check:
			# 			print(check['ck_id'], check['name'])

			# 测试症状是不是都能在数据库找到对应实体
			# if data['symptoms']:
			# 	for sm in data['symptoms']:
			# 		sm_id = sm['sm_id']
			# 		sm_name = sm['sm_name']
			# 		symptom = self.graph.nodes.match("Symptom", sm_id=sm_id, name=sm_name).first()
			# 		if symptom:
			# 			print(symptom['sm_id'], symptom['name'])

			# 测试菜谱是不是都能在数据库找到对应实体
			# if data['recipes']:
			# 	for rp in data['recipes']:
			# 		rp_id = self._extract_id(rp['rp_url'])
			# 		rp_name = rp['rp_name']
			# 		recipe = self.graph.nodes.match("Recipe", rp_id = rp_id, name = rp_name).first()
			# 		if recipe:
			# 			print(recipe['rp_id'], recipe['name'])

			# 测试药品是不是都能在数据库找到对应实体
			if data['drug']:
				for dg_url in data['drug']:
					dg_id = self._extract_id(dg_url)
					drug = self.graph.nodes.match("Drug", dg_id = dg_id).first()
					if drug:
						print(drug['dg_id'], drug['name'])

	def _build_relationship(self):
		# 建立节点之间的联系
		for data in self._extract_data(Build_Graph.disease):
			rel_list = []
			disease = self.graph.nodes.match('Disease', d_id = data['id']).first()
			# 建立并发症关系
			if data['neopathy']:
				for neo in data['neopathy']:
					neo_id = neo['neo_id']
					neo_name = neo['neo_name']
					neopathy = self.graph.nodes.match("Disease", d_id=neo_id, name=neo_name).first()
					if neopathy:
						print(neopathy['d_id'], neopathy['name'])
						rel_list.append(Relationship(disease, Build_Graph.disease_rel_neopathy, neopathy))

			# 建立检查项目关系
			if data['checkes']:
				for ck in data['checkes']:
					ck_id = self._extract_id(ck['ck_url'])
					ck_name = ck['ck_name']
					check = self.graph.nodes.match("Check", ck_id=ck_id, name=ck_name).first()
					if check:
						print(check['ck_id'], check['name'])
						rel_list.append(Relationship(disease, Build_Graph.disease_rel_check, check))

			# 建立检查项目关系
			if data['symptoms']:
				for sm in data['symptoms']:
					sm_id = sm['sm_id']
					sm_name = sm['sm_name']
					symptom = self.graph.nodes.match("Symptom", sm_id=sm_id, name=sm_name).first()
					if symptom:
						print(symptom['sm_id'], symptom['name'])
						rel_list.append(Relationship(disease, Build_Graph.disease_rel_symptom, symptom))

			# 建立食谱项目关系
			if data['recipes']:
				for rp in data['recipes']:
					rp_id = self._extract_id(rp['rp_url'])
					rp_name = rp['rp_name']
					recipe = self.graph.nodes.match("Recipe", rp_id = rp_id, name = rp_name).first()
					if recipe:
						print(recipe['rp_id'], recipe['name'])
						rel_list.append(Relationship(disease, Build_Graph.disease_rel_recipe, recipe))

			# 建立药物项目关系
			if data['drug']:
				for dg_url in data['drug']:
					dg_id = self._extract_id(dg_url)
					drug = self.graph.nodes.match("Drug", dg_id = dg_id).first()
					if drug:
						print(drug['dg_id'], drug['name'])
						rel_list.append(Relationship(disease, Build_Graph.disease_rel_drug, drug))

			Rels = Subgraph(relationships = rel_list)
			self.graph.create(Rels)

	def extra_data(self):
		'''添加一些额外的数据, '''


	def run(self):
		# self._build_entities()
		# self._build_relationship()
		self.extra_data()

	def __del__(self):
		print("执行花费时间: %f"%(time.clock() - self.start_time))

if __name__ == '__main__':
	graph = Build_Graph()
	graph.run()


