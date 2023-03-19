# coding=utf-8
from gensim.models.word2vec import Word2Vec
import jieba
import numpy as np

def split_sentence_jieba(s:str):
	'''将句子进行分词, 返回列表'''
	res_list = jieba.cut(s)
	return list(res_list)

def build_corpus():
	corpus = []
	corpus.append(split_sentence_jieba("我想问下疾病"))
	corpus.append(split_sentence_jieba("请问疾病是什么"))
	corpus.append(split_sentence_jieba("告诉我什么是疾病"))
	corpus.append(split_sentence_jieba("疾病到底是什么"))
	return corpus

def train_word2vec(corpus):
	'''传入的corpus为二维数组, 行代表一句话的分词，列代表每句话
	eg:
	[
		["我", "今天", "上班"],
		["你", "找", "我", "干嘛"],
		...
	]
	'''
	model = Word2Vec(corpus, min_count = 1)
	model.save('models/test.model')
	model.wv.save_word2vec_format('models/test.bin', binary = True)
	print('训练完成')

def get_sentence_vector(s_list):
	model = Word2Vec.load('models/test.model')
	v = np.zeros((1,100))
	for s in s_list:
		v += np.array(model[s])
	return v/len(s_list)

if __name__ == '__main__':
	# corpus = build_corpus()
	# print(corpus)
	# train_word2vec(corpus)


	s_list = split_sentence_jieba('我想问下疾病')
	s_v = get_sentence_vector(s_list)
	print(s_v)


