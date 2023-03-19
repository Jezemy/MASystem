# coding=utf-8
'''
通过disease的json文件爬取并保存其他实体的内容
实体包括{
	疾病/并发症：disease
	症状：symptom
	检查：check
	药品：drug
	食谱：recipe
}

编码问题。由于医疗页面涉及大量不常用词汇，因此用gbk解码是不够的，应该用GB18030

requests库对中文解码识别有问题，需要用cchardet来进行检测
'''

import requests
import json
from lxml import etree
import re
import random
from retrying import retry
import cchardet
import vthread
import time

headers = {
		'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9',
	}

def extract_id(text:str):
	'''将id从字符串中抽出'''
	return re.search("[0-9]+",text).group()

def unify(s):
	'''去除非法字符'''
	return s.replace('\r', '').replace(' ', '').replace('\t', '').replace('\n', '')\
            .replace('\xa0', '').replace('\u3000', '')

def read_disease_data():
	'''读取disease.json的数据, 只保留其他实体的值'''
	lines = [line.strip() for line in open('entities/disease.json', 'r', encoding = 'utf-8')]
	for line in lines:
		d_data = json.loads(line)
		data = {
			'd_id':d_data['id'],
			'recipes':d_data['recipes'],
			'symptoms':d_data['symptoms'],
			'neopathy':d_data['neopathy'],
			'checks':d_data['checkes'],
			'drug':d_data['drug']
		}
		yield data

'''菜谱页面'''
@retry(stop_max_attempt_number=3,wait_fixed=2000)
def get_recipes_info_url(rp_url):
	rep = requests.get(rp_url, headers = headers)
	encoding = cchardet.detect(rep.content)
	rep.encoding = encoding['encoding']
	if not rep.text:
		return '', '暂无制作方式'
	html = etree.HTML(rep.text)
	print(rp_url)
	pic_url = html.xpath('//div[@class="w687 fl"]//a/img/@src')[0].strip().replace('error/', '')
	produce_way = html.xpath('//div[@class="text-intro f14 graydeep"]/dl[1]//li/text()')[0].strip()
	return pic_url, unify(produce_way)

def get_info_recipies(data:dict, idKey=list()):
	'''从data中获取recipes数据，进行爬虫获取其他信息
	菜谱recipes{
	    id
	    name
	    pic_url
	    produce_way
	}
	data['recipes']:[{rp_url, rp_name}...]
	'''

	rps = {}
	# print(data['d_id'])
	for rp in data['recipes']:
		rp_url = rp['rp_url']
		rp_id = extract_id(rp_url)
		if idKey and rp_id in idKey:
			continue

		rp_name = rp['rp_name']
		pic_url, produce_way = get_recipes_info_url(rp_url)

		rps[str(rp_id)] = {
			'id':rp_id,
			'name':rp_name,
			'pic_url':pic_url,
			'produce_way':produce_way
		}
	return rps


'''检查页面'''
@retry(stop_max_attempt_number=3,wait_fixed=2000)
def get_checks_desc_url(ck_url):
	rep = requests.get(ck_url, headers = headers)
	encoding = cchardet.detect(rep.content)
	if not rep.text:
		return '暂无简介'
	rep.encoding = encoding['encoding']
	html = etree.HTML(rep.text)
	print(ck_url)
	desc_tag = html.xpath('//div[@class="baby-weeks"]/p/text()')
	if desc_tag:
		desc = unify(desc_tag[0].strip())
	else:
		desc = '暂无简介'

	return desc

def get_info_checks(data:dict, idKey=list()):
	'''从data中获取checks数据，进行爬虫获取其他信息
	检查checkes{
	    id
	    name
	    desc
	}
	data['check']:[{ck_url, ck_name}...]
	'''
	cks = {}
	# print(data['d_id'])
	for ck in data['checks']:
		ck_url = ck['ck_url']
		ck_id = extract_id(ck_url)

		if idKey and ck_id in idKey:
			continue
		ck_name = ck['ck_name']

		desc = get_checks_desc_url(ck_url)

		cks[str(ck_id)] = {
			'id': ck_id,
			'name': ck_name,
			'desc': desc
		}
	return cks


'''症状页面'''
@retry(stop_max_attempt_number=3,wait_fixed=2000)
def get_symptoms_desc_url(sm_url):
	rep = requests.get(sm_url, headers = headers)
	encoding = cchardet.detect(rep.content)
	rep.encoding = encoding['encoding']
	html = etree.HTML(rep.text)
	desc_tags = html.xpath('//div[@class="zz-articl fr f14"]//*')
	desc_list = []
	for tag in desc_tags:
		s_list = tag.xpath('text()')
		if s_list and unify(s_list[0]):
			desc_list.append(unify(s_list[0]))
	if not desc_list:
		desc_list.append('暂无简介')
	return ','.join(desc_list)

def get_symptoms_diagnose_url(sm_url):
	rep = requests.get(sm_url, headers = headers)
	encoding = cchardet.detect(rep.content)
	rep.encoding = encoding['encoding']
	html = etree.HTML(rep.text)
	desc_tags = html.xpath('//div[@class="zz-articl fr f14"]//*')
	desc_list = []
	for tag in desc_tags:
		s_list = tag.xpath('text()')
		if s_list and unify(s_list[0]):
			desc_list.append(unify(s_list[0]))
	if not desc_list:
		desc_list.append('暂无简介')
	return ','.join(desc_list)

def get_info_symptoms(data:dict, idKey=list()):
	'''从data中获取checks数据，进行爬虫获取其他信息
	症状symptoms{
	    id
	    name
	    desc
	    diagnose
	}
	data['symptoms']:[{sm_id, sm_name}...]
	'''
	sms = {}
	# print(data['d_id'])
	for sm in data['symptoms']:
		sm_name = sm['sm_name']
		sm_id = sm['sm_id']
		if idKey and sm_id in idKey:
			continue
		# desc = get_symptoms_desc_url('http://zzk.xywy.com/{sm_id}_jieshao.html'.format(sm_id=sm_id))
		# diagnose = get_symptoms_diagnose_url('http://zzk.xywy.com/{sm_id}_zhenduan.html'.format(sm_id=sm_id))

		sms[str(sm_id)] = {
			'id': sm_id,
			'name': sm_name,
			# 'desc': desc,
			# 'diagnose':diagnose
		}
	return sms


'''药品页面'''
@retry(stop_max_attempt_number=3,wait_fixed=2000)
def get_drugs_info_url(dg_url):
	rep = requests.get(dg_url, headers = headers)
	encoding = cchardet.detect(rep.content)
	rep.encoding = encoding['encoding']
	html = etree.HTML(rep.text)
	print(dg_url)
	# 这个网站有个坑，长同个格式的网页可以访问到不同页面
	if rep.url != dg_url:
		return None, None, None, None, None

	pic_url = html.xpath('//div[@class="p-jqzoom fl mt20 ml20"]//img[1]/@src')[0]
	price = html.xpath('//div[@class="d-info-dl mt5"]//dl[2]/dd/span/text()')[0].strip()

	dl_tags = html.xpath('//div[@class="d-tab-inf"]/dl')
	name=func=use=None
	for dl in dl_tags:
		left = dl.xpath('dt/text()')[0].strip()
		if left == '批准文号':
			continue
		right = dl.xpath('dd/text()')
		if right:
			right = right[0].strip()
		else:
			right = None

		if left == '商品名称':
			name = right

		if left == '功能主治':
			func = right

		if left == '用法用量':
			use = right

	if not name:
		raise Exception('药品没有名字: '+dg_url)
	if not func:
		func = '暂无功能主治信息'
	if not use:
		use = '暂无用法用量信息'

	return name,pic_url, price, func, use

def get_info_drugs(data:dict, idKey=list()):
	'''从data中获取checks数据，进行爬虫获取其他信息
	药物drug{
	    id
	    name
	    pic_url
	    price
	    func
	    use
	}
	data['drug']:[url1,url2...]
	'''
	dgs = {}
	for dg_url in data['drug']:
		dg_id = extract_id(dg_url)
		if idKey and dg_id in idKey:
			continue
		name, pic_url, price, func, use = get_drugs_info_url(dg_url)
		# 如果遇到坑的网站，直接跳过一个药品
		if name==None or pic_url==None or price==None or func==None or use==None:
			continue
		dgs[str(dg_id)] = {
			'id':dg_id,
			'name':name,
			'pic_url':pic_url,
			'price':price,
			'func':func,
			'use':use
		}
	return dgs


'''随机测试一些数据'''
def random_test_func(funcName):
	lines = [line.strip() for line in open('entities/disease.json', 'r', encoding = 'utf-8')]
	tests = random.sample(lines,10)
	for t in tests:
		d_data = json.loads(t)
		data = {
			'd_id': d_data['id'],
			'recipes': d_data['recipes'],
			'symptoms': d_data['symptoms'],
			'neopathy': d_data['neopathy'],
			'checks': d_data['checkes'],
			'drug': d_data['drug']
		}
		res = funcName(data)
		print(res)

'''多线程爬虫'''
class Crawler:
	def __init__(self,fileName, funcName):
		# 根据传递的参数不同爬取不同的实体
		self.file = open('entities/{fn}.json'.format(fn=fileName), 'w', encoding = 'utf-8')
		self.funcName = funcName
		self.t = time.clock()
		self.idKey = set()

	@vthread.atom
	def update_Data(self, batch_data:dict):
		for key in batch_data.keys():
			if key not in self.idKey:
				self.idKey.add(key)
				self.file.write(json.dumps(batch_data[key], ensure_ascii = False) + '\n')

	@vthread.pool(1)
	def get_data(self, data:dict, cur_cnt):
		print('当前进度: {0} / {1}'.format(cur_cnt, 6544))
		batch_data = self.funcName(data)
		self.update_Data(batch_data)

	def run(self):
		cnt = 0
		for data in read_disease_data():
			cnt += 1
			self.get_data(data, cnt)
			# if cnt==10:
			# 	break

	def __del__(self):
		self.file.close()
		print('总共花费时间: %f'%(time.clock()-self.t))


if __name__ == '__main__':
	# data = read_disease_data()
	# print(data)
	# random_test_func(get_info_drugs)
	# print(get_drugs_info_url('http://yao.xywy.com/goods/9743.htm'))
	'''drug'''
	# c = Crawler('drug', get_info_drugs)
	# c.run()
	'''check'''
	# c = Crawler('check', get_info_checks)
	# c.run()
	'''recipe'''
	# c = Crawler('recipe', get_info_recipies)
	# c.run()
	'''symptom'''
	c = Crawler('symptom', get_info_symptoms)
	c.run()

