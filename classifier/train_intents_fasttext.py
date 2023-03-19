# coding=utf-8

import os
import jieba
import fasttext.FastText as fasttext
import random

stopwords = set([line.strip() for line in open('stopwords.txt', 'r', encoding = 'utf-8')])

def read_data_file():

	# 读取intents
	_, _, files = list(os.walk('intent'))[0]

	# 从文件写入data
	data = {}
	for file in files:
		file_intent_list = [line.strip() for line in open('intent/'+file, 'r', encoding = 'utf-8')]
		data[file.replace('.txt','')] = random.sample(file_intent_list, int(0.9*len(file_intent_list)))

	return data

def read_dict_jieba():
	_, _, files = list(os.walk('dict'))[0]
	for file in files:
		jieba.load_userdict('dict/'+file)

def split_sentence_jieba(s:str):
	'''将句子进行分词, 返回列表'''
	res_list = []
	for word in jieba.cut(s):
		if word not in stopwords:
			res_list.append(word)
	return res_list


def build_fasttext_train_data():
	data = read_data_file()
	word_set = set()
	file = open('fasttext_data.txt', 'w', encoding = 'utf-8')
	for key in data.keys():
		for s in data[key]:
			split_list = split_sentence_jieba(s)
			for word in split_list:
				word_set.add(word)
			file.write('_%s '%key + ' '.join(split_list) + '\n')
	file.close()

	# 保存词典

	with open('vocabs.txt', 'w', encoding = 'utf-8') as f:
		for word in list(word_set):
			f.write(word + '\n')


def train_model_fasttext():
	classifier = fasttext.train_supervised('fasttext_data.txt', label='_', dim=100, epoch=500, lr=0.01, loss='softmax')
	classifier.save_model('models/fasttext.model')
	return classifier

def test_model_fasttext(s_list):
	model = fasttext.load_model('models/fasttext.model')
	for s in s_list:
		split_list = split_sentence_jieba(s)
		label_prob = model.predict(' '.join(split_list), k=5)
		print(s)
		print(split_list)
		print(label_prob)


if __name__ == '__main__':
	read_dict_jieba()
	build_fasttext_train_data()
	train_model_fasttext()
	test_model_fasttext([
		'药品有什么用',
		'要如何治疗',
		'这是什么疾病',
		'要去哪里看疾病',
		'吃什么好啊',
		'有什么症状',
		'要治疗多久',
		'疾病要花多少钱',
		'这药品要花多少钱',
		'怎么使用',
		'好的',
		'没有',
		'谢谢',
		'你好',
	])
