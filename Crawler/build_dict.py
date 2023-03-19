# coding=utf-8

'''
根据爬虫结果抽取字典
'''
import json
import re


class build_dict:
	def __init__(self, fileName):
		self.readFile = open('entities/{fn}.json'.format(fn=fileName), 'r', encoding = 'utf-8')
		self.saveFile = open('dict/{fn}.txt'.format(fn = fileName), 'w', encoding = 'utf-8')

	def execute(self):
		name_set = set()
		# 去重
		for item in self.readFile:
			data = json.loads(item.strip())
			line = data['name'].strip()
			word_list = line.split()
			if len(word_list)>1:
				name_set.add(word_list[-1])
			else:
				name_set.add(word_list[0])


		# 保存词典
		for name in list(name_set):
			self.saveFile.write(name + '\n')

	def __del__(self):
		self.readFile.close()
		self.saveFile.close()

if __name__ == '__main__':
	# bd = build_dict('disease')
	# bd = build_dict('check')
	# bd = build_dict('symptom')
	# bd = build_dict('recipe')
	bd = build_dict('drug')
	bd.execute()