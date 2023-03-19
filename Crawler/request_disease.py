# coding=utf-8
'''
实体包括{
	疾病/并发症：disease
	症状：symptom
	检查：check
	药品：drug
	食谱：recipe
}


思路：
网站：http://jib.xywy.com
通过先爬取疾病，获取主要信息，同时记录其他实体的ID信息，以便后续继续爬取相关实体的信息

疾病关系以及属性{
	id ：前置页面爬虫获取

	疾病名字：主页
	易感人群：主页 页面获取
	患病比例：主页 页面获取
	疾病图片：主页 页面获取
	症状（实体）： 主页 侧边栏获取 记录ID
	检查（实体）： 主页 侧边栏获取 记录ID
	并发症（实体）：主页 侧边栏获取 不用记录ID

	简介：简介 页面获取
	病因：病因 页面获取
	预防：预防 页面获取

	治疗： 治疗 页面获取
	治疗费用：治疗 页面获取
	治疗周期：治疗 页面获取
	治愈率： 治疗 页面获取
	科室：治疗 页面获取

	食物： 食物 页面获取
		宜吃食物：不记录ID
		忌吃食物：不记录ID

	推荐食谱（实体）： 食物页面获取 记录ID
	推荐药品（实体）： 药品页面获取 记录ID
}
'''
import requests
from lxml import etree
import re
import random
from retrying import retry
import json
import vthread

class UrlOption:
	def __init__(self):
		self.main = '主页'
		self.info = '简介'
		self.cause = '病因'
		self.prevent = '预防'
		self.neopathy = '并发症'
		self.symptom = '症状'
		self.inspect = '检查'
		self.treat = '治疗'
		self.food = '食物'
		self.drug = '药品'
options = UrlOption()

headers = {
		'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9',
	}

'''工具函数'''

def gen_website_url(option, diseaseID):
	'''返回URL'''
	main_url = "http://jib.xywy.com"
	url_dict = {
		'主页':'/il_sii_',
		'简介':'/il_sii/gaishu/',
		'病因':'/il_sii/cause/',
		'预防':'/il_sii/prevent/',
		'并发症':'/il_sii/neopathy/',
		'症状':'/il_sii/symptom/',
		'检查':'/il_sii/inspect/',
		'治疗':'/il_sii/treat/',
		'食物':'/il_sii/food/',
		'药品':'/il_sii/drug/',
	}
	return main_url+url_dict[option]+str(diseaseID)+'.htm'

def extract_id(text:str):
	'''将id从字符串中抽出，用于a标签的href属性'''
	return re.search("[0-9]+",text).group()

def unify(s):
	'''去除非法字符'''
	return s.replace('\r', '').replace(' ', '').replace('\t', '').replace('\n', '')\
            .replace('\xa0', '').replace('\u3000', '')


'''信息获取函数'''
def get_disease_id():
	'''
	函数作用：将每一个id爬取，然后保存至文件disease_id, 作为中间文件以进行后续工作
	out_url是由字母排序的所有疾病的网站，从a遍历到z即可获得疾病网站
	然后再根据网站对每一个疾病进行爬取
	'''
	out_url = 'http://jib.xywy.com/html/{letter}.html'
	f = open("entities/disease_id.txt","w",encoding = "utf-8")
	for let in [chr(97+i) for i in range(0,26)]:
		cur_url = out_url.format(letter=let)
		print("正在爬取", cur_url)
		rep = requests.get(cur_url, headers=headers)
		html = etree.HTML(rep.text)
		res = html.xpath('//div[@class="fl jblist-con-ear"]//ul//a')
		for item in res:
			d_id = extract_id(item.xpath('@href')[0])
			# d_name = item.xpath('text()')[0].encode('iso-8859-1').decode('gbk')
			print(d_id)
			f.write(d_id + '\n')
	f.close()

@retry(stop_max_attempt_number=3)
def get_info_main(d_id):
	'''根据疾病ID，到其主页获取相应信息'''
	main_url = gen_website_url(options.main, d_id)
	rep = requests.get(main_url, headers=headers)
	html = etree.HTML(rep.text)
	data = {}

	name = html.xpath('//div[@class="wrap mt5"]//div/text()')[0].strip()
	data['name'] = name

	easy_get = html.xpath('//div[@class="fl jib-common-sense"]/p[1]/span[@class="fl sense-right"]/text()')[0].strip()
	data['easy_get'] = easy_get

	'''注释是原来版本， 出错是因为有显示治愈率，但是治愈率是空的'''
	# ill_rate = html.xpath('//div[@class="fl jib-common-sense"]/p[2]/span[@class="fl sense-right"]/text()')[0].strip()
	# data['ill_rate'] = ill_rate
	'''修改版本分界线'''
	ill_rate = html.xpath('//div[@class="fl jib-common-sense"]/p[2]/span[@class="fl sense-right"]/text()')
	if ill_rate:
		data['ill_rate'] = ill_rate[0].strip()
	else:
		data['ill_rate'] = ''
	'''修改版本分界线'''

	pic_url = html.xpath('//div[@class="jib-art-box"]//img/@src')[0]
	data['pic_url'] = pic_url

	neopathies = html.xpath('//div[@class="jib-navbar fl bor pr"]/div[1]//div[@class="jib-navbar-bd "]/div[3]/p[not(@class="mt5")]/a')
	data['neopathy'] = []
	for neo in neopathies:
		neo_id = extract_id(neo.xpath('@href')[0])
		neo_name = neo.xpath('text()')[0].strip()
		data['neopathy'].append({"neo_id":neo_id,"neo_name":neo_name})

	checkes = html.xpath(
		'//div[@class="jib-navbar fl bor pr"]/div[2]//div[@class="jib-navbar-bd "]/div[2]/p[not(@class="mt5")]/a')
	data['checkes'] = []
	for ck in checkes:
		ck_url = ck.xpath('@href')[0]
		ck_name = ck.xpath('text()')[0].strip()
		data['checkes'].append({"ck_url": ck_url, "ck_name": ck_name})

	symptoms = html.xpath(
		'//div[@class="jib-navbar fl bor pr"]/div[2]//div[@class="jib-navbar-bd "]/div[1]/p[not(@class="mt5")]/a')
	data['symptoms'] = []
	for sm in symptoms:
		sm_id = extract_id(sm.xpath('@href')[0])
		sm_name = sm.xpath('text()')[0].strip()
		data['symptoms'].append({"sm_id": sm_id, "sm_name": sm_name})

	return data

@retry(stop_max_attempt_number=3)
def get_info_other(d_id):
	'''根据疾病ID，到其简介页， 病因页， 预防页 各获取相应信息'''
	data = {}
	info_url = gen_website_url(options.info, d_id)
	rep = requests.get(info_url, headers = headers)
	html = etree.HTML(rep.text)
	desc = html.xpath('//div[@class="jib-articl-con jib-lh-articl"]//p/text()')[0].strip()
	data['desc'] = unify(desc)

	cause_url = gen_website_url(options.cause, d_id)
	rep = requests.get(cause_url, headers = headers)
	html = etree.HTML(rep.text)
	cause_tag = html.xpath('(//div[@class=" jib-articl fr f14 jib-lh-articl"]/p)|(//div[@class=" jib-articl fr f14 jib-lh-articl"]/p/b)|(//div[@class=" jib-articl fr f14 jib-lh-articl"]/p/strong)')
	cause_list = []
	for tag in cause_tag:
		s_list = tag.xpath('text()')
		if s_list:
			s = unify(s_list[0])
			if s:
				cause_list.append(s)
	data['cause'] = '\n'.join(cause_list)

	prevent_url = gen_website_url(options.prevent, d_id)
	rep = requests.get(prevent_url, headers=headers)
	html = etree.HTML(rep.text)
	prevent_tag = html.xpath(
		'(//div[@class="jib-articl fr f14 jib-lh-articl"]/p)|(//div[@class="jib-articl fr f14 jib-lh-articl"]/p/b)|(//div[@class=" jib-articl fr f14 jib-lh-articl"]/p/strong)')
	prevent_list = []
	for tag in prevent_tag:
		s_list = tag.xpath('text()')
		if s_list:
			s = unify(s_list[0])
			if s:
				prevent_list.append(s)
	data['prevent'] = '\n'.join(prevent_list)

	return data

@retry(stop_max_attempt_number=3)
def get_info_treat(d_id):
	'''根据疾病ID，到其治疗页获取相应信息'''
	treat_url = gen_website_url(options.treat, d_id)
	rep = requests.get(treat_url, headers = headers)
	html = etree.HTML(rep.text)
	data = {}

	panel = html.xpath('//div[@class="mt20 articl-know "]//p')
	for pTag in panel:
		left_title = pTag.xpath('span[1]/text()')[0].strip()
		'''注释的是原版，下方的是修改版本，出错原因是网页有left_title，但是没有right_content'''
		# right_content = pTag.xpath('span[2]/text()')[0].strip()
		'''修改版本分割线'''
		right_content = pTag.xpath('span[2]/text()')
		if right_content:
			right_content = right_content[0].strip()
		else:
			right_content = ''
		'''修改版本分割线'''
		if left_title == '就诊科室：':
			data['department'] = right_content
		elif left_title == '治疗方式：':
			data['treat_way'] = right_content
		elif left_title == '治疗周期：':
			data['treat_time'] = right_content
		elif left_title == '治愈率：':
			data['treat_rate'] = right_content
		elif left_title == '治疗费用：':
			data['treat_cost'] = right_content

	if len(list(data.keys())) != 5:
		print("id=%s get_info_treat 数据获取不完整"%d_id)
		print(data)

	return data

@retry(stop_max_attempt_number=3)
def get_info_food(d_id):
	'''根据疾病ID，到其食物页获取相应信息'''
	food_url = gen_website_url(options.food, d_id)
	rep = requests.get(food_url, headers = headers)
	html = etree.HTML(rep.text)
	data = {}

	diet_good_text = html.xpath('//div[@class="panels mt10"]/div[2]//div[@class="fl diet-good-txt"]/text()')[0].strip()
	diet_good_food_list = html.xpath('//div[@class="panels mt10"]/div[2]//div[@class="diet-img clearfix mt20"]//p')
	data['diet_good'] = diet_good_text + " 宜吃：" + '，'.join([food.xpath('text()')[0].strip() for food in diet_good_food_list])

	diet_bad_text = html.xpath('///div[@class="panels mt10"]/div[3]//div[@class="fl diet-good-txt"]/text()')[
		0].strip()
	diet_bad_food_list = html.xpath('//div[@class="panels mt10"]/div[3]//div[@class="diet-img clearfix mt20"]//p')
	data['diet_bad'] = diet_bad_text + " 不宜吃：" + '，'.join(
		[food.xpath('text()')[0].strip() for food in diet_bad_food_list])

	recipes_list = html.xpath('//div[@class="panels mt10"]/div[4]//div[@class="diet-img clearfix mt20"]/div')
	data['recipes'] = []
	for rp in recipes_list:
		rp_url = rp.xpath('a/@href')[0]
		rp_name = rp.xpath('p/text()')[0].strip()
		data['recipes'].append({"rp_url":rp_url, "rp_name":rp_name})

	return data

@retry(stop_max_attempt_number=3)
def get_info_drug(d_id):
	'''根据疾病ID，到其药品页获取相应信息'''
	drug_url = gen_website_url(options.drug, d_id)
	rep = requests.get(drug_url, headers = headers)
	html = etree.HTML(rep.text)
	data = {}
	drugs = html.xpath('//div[@class="city-item"]//div[@class="fl drug-pic bor mr10"]')
	data['drug'] = []
	for d in drugs:
		d_url = d.xpath('a/@href')[0]
		data['drug'].append(d_url)
	return data

'''随机测试函数'''
def random_test_func(funcName):
	'''随机从id中取出数据，测试上述函数是否发生错误'''
	disease_ids = [line.strip() for line in open('entities/disease_id.txt', 'r', encoding = 'utf-8')]
	samples = random.sample(disease_ids, 10)
	for id in samples:
		print(id)
		print(funcName(id))

def save_test_all():
	'''测试汇总并存储'''
	disease_ids = [line.strip() for line in open('entities/disease_id.txt', 'r', encoding = 'utf-8')]
	f = open('entities/disease.json','w')
	samples = random.sample(disease_ids, 10)
	for id in samples:
		print(id)
		data = {
			'id':id,
			**get_info_main(id),
			**get_info_other(id),
			**get_info_treat(id),
			**get_info_food(id),
			**get_info_drug(id)
		}
		print(data)
		# 不加ensure_ascii的话，保存到文件是Unicode，看不了中文
		f.write(json.dumps(data,ensure_ascii = False) + '\n')
	f.close()

'''多线程进行爬虫下载'''

class Crawler:
	def __init__(self):
		self.file = open('entities/disease.json', 'w', encoding = 'utf-8')
		self.disease_ids = [line.strip() for line in open('entities/disease_id.txt', 'r', encoding = 'utf-8')]

	@vthread.atom
	def save_one_line(self, data:str):
		self.file.write(data)

	@vthread.pool(10)
	def get_one_line(self, d_id):
		'''多线程下载'''
		print(d_id)
		data = {
			'id': d_id,
			**get_info_main(d_id),
			**get_info_other(d_id),
			**get_info_treat(d_id),
			**get_info_food(d_id),
			**get_info_drug(d_id)
		}
		self.save_one_line(json.dumps(data, ensure_ascii = False) + '\n')

	def __del__(self):
		self.file.close()

	def run(self):
		for d_id in self.disease_ids:
			self.get_one_line(d_id)

def single_process():
	'''单独处理'''
	ids = [4839,4467,9765]
	for id in ids:
		data = {
			'id': id,
			**get_info_main(id),
			**get_info_other(id),
			**get_info_treat(id),
			**get_info_food(id),
			**get_info_drug(id)
		}
		print(json.dumps(data, ensure_ascii = False))


if __name__ == '__main__':
	# c = Crawler()
	# c.run()
	'''爬虫总结：
	线程应该开到30甚至50，只有10太慢了
	小部分数据缺少treat_rate或treat_time，后续存入数据库的时候需要注意判断
	忘记在Crawler类中加记录时间的代码了
	3个数据中间出错，需要单独处理。[4839，4467，9765]
	'''
	single_process()
	'''
	修改后的版本可以直接用Crawler，应该就没问题了
	'''
	# random_test_func(save_info_all)