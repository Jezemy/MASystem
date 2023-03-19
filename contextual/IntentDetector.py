# coding=utf-8

'''
意图检测分类，上下文槽
'''
import fasttext.FastText as fasttext
import jieba
import os


class Detector:

	def __init__(self):
		self.slots = {}
		'''django用第二个，普通用第一个'''
		# self.classifier_path = '../classifier'
		self.classifier_path = 'classifier'

		self.model = fasttext.load_model(
			'{classifier_path}/models/fasttext.model'.format(classifier_path = self.classifier_path))

		self.stopwords = set([line.strip() for line in open('{classifier_path}/stopwords.txt'.format(classifier_path = self.classifier_path),'r',encoding = 'utf-8')])

		self.vocabs = set([line.strip() for line in open('{classifier_path}/vocabs.txt'.format(classifier_path = self.classifier_path), 'r',encoding = 'utf-8')])

		# 读取专业词汇
		self.disease = set([line.strip() for line in open('{classifier_path}/dict/disease.txt'.format(classifier_path = self.classifier_path),'r',encoding = 'utf-8')])

		self.drug = set([line.strip() for line in open('{classifier_path}/dict/drug.txt'.format(classifier_path = self.classifier_path), 'r',encoding = 'utf-8')])

		# 初始化方法
		self._read_dict()

	def _read_dict(self):
		# jieba读取字典
		_, _, files = list(os.walk('{classifier_path}/dict'.format(classifier_path = self.classifier_path)))[0]
		for file in files:
			# print('jieba分词器读取文件: ' + file)
			jieba.load_userdict('{classifier_path}/dict/'.format(classifier_path = self.classifier_path) + file)

	def _init_slot(self, username):
		self.slots[username] = {
			"disease": None,
			"drug": None,
			"symptom": None,
			"recipe": None,
			"check": None
		}

	def detect(self, username: str, sentence: str):
		# 针对用户名初始化slot
		if username not in self.slots:
			self._init_slot(username)

		# 先用jieba初步分词
		split_list = list(jieba.cut(sentence))

		# 检测是否有更新slot
		isUpdateSlot = False

		# 过滤掉不在fasttext训练中的词汇,即未登录词
		# 修正专业词汇
		filter_list = []
		for word in split_list:
			if word in self.disease:
				self.update_slots(username, disease = word)
				isUpdateSlot = True
				filter_list.append('疾病')
				continue

			if word in self.drug:
				self.update_slots(username, drug = word)
				isUpdateSlot = True
				filter_list.append('药品')
				continue

			if word in self.vocabs:
				filter_list.append(word)

		print(filter_list)
		label_prob = self.model.predict(' '.join(filter_list))
		print(label_prob)
		return label_prob[0][0][1:], not isUpdateSlot

	def update_slots(self, username, disease=None, drug=None, symptom=None, check=None, recipe=None):
		if username not in self.slots:
			self._init_slot(username)

		if disease:
			self.slots[username]['disease'] = disease

		if drug:
			self.slots[username]['drug'] = drug

		if symptom:
			self.slots[username]['symptom'] = symptom

		if check:
			self.slots[username]['check'] = check

		if recipe:
			self.slots[username]['recipe'] = recipe

	def set_single_slot(self, username, entity_name, content):
		self.slots[username][entity_name] = content

	def gain_slot(self, username):
		if username not in self.slots:
			self._init_slot(username)

		return self.slots[username]

IntentDetector = Detector()

if __name__ == '__main__':
	username = 'jezemy'
	IntentDetector.detect(username, '请问感冒怎么办')
	print(IntentDetector.gain_slot(username))
	IntentDetector.detect(username, '骨折治疗费用是多少')
	print(IntentDetector.gain_slot(username))
	IntentDetector.detect(username, '上清丸怎么使用')
	print(IntentDetector.gain_slot(username))
