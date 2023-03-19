# coding=utf-8
'''
上下文机制

输入一句问句，判断意图，查询数据库

返回数据data = {text:"回复内容", buttons:[], pic_url:""}

'''
from contextual.IntentDetector import IntentDetector
from contextual.KGQuery import *

import random

class IntentProcess:
	def __init__(self):
		pass

	'''固定模板的intent'''
	def _action_greet(self):
		'''greet的回答方式'''
		# 将从下面的模板中随机选择一条回复
		response_pattern = [
			'你好',
			'你好啊',
		]
		text = random.choice(response_pattern)
		return {'text':text, 'button':[], 'pic_url':""}

	def _action_deny(self):
		response_pattern = [
			'希望我能帮到你',
			'很高兴为您服务'
		]
		text = random.choice(response_pattern)
		return {'text':text, 'button':[], 'pic_url':""}

	def _action_goodbye(self):
		response_pattern = [
			'再见，希望您身体健康',
			'拜拜，希望我有帮助到您',
			'再见，很高兴能够为您服务'
		]
		text = random.choice(response_pattern)
		return {'text':text, 'button':[], 'pic_url':""}

	def _action_affirm(self):
		response_pattern = [
			'嗯嗯，请问还有其他问题吗',
			'好的，如果你有问题还可以继续询问我',
			'很高兴能够帮到你，请问还有其他什么要问的吗'
		]
		text = random.choice(response_pattern)
		return {'text':text, 'button':[], 'pic_url':""}

	def _action_thankyou(self):
		response_pattern = [
			'不用客气',
			'能帮到您是我的荣幸',
			'很高兴为您服务',
			'很高兴能够帮助到您'
		]
		text = random.choice(response_pattern)
		return {'text':text, 'button':[], 'pic_url':""}

	'''查询数据库的Intent'''
	def _button_data_process(self, data, intent):
		# 要保证data有数据
		if data:
			return {'text': '请点击选择想要查询的内容', 'button': data, 'pic_url': "", "intent":intent}
		else:
			return {'text': '知识库暂无相关内容', 'button': [], 'pic_url': ""}

	def _action_disease_cause(self, slot:dict, sure=False):
		data = query_disease_property(slot['disease'], Disease.cause, sure)

		# 如果sure是False，那么返回的将会是数据库中与disease名字相似的名字列表，直接放进button
		if not sure:
			return self._button_data_process(data, "disease_cause")

		# 如果sure是True，那么查询到的结果是确定的disease的cause了。
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_disease_department(self, slot:dict, sure=False):
		data = query_disease_property(slot['disease'], Disease.department, sure)

		if not sure:
			return self._button_data_process(data, "disease_department")
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_disease_desc(self, slot: dict, sure = False):
		desc = query_disease_property(slot['disease'], Disease.desc, sure)

		if not sure:
			return self._button_data_process(desc, "disease_desc")
		else:

			data = {'text':'知识库暂无相关信息', 'button':[], 'pic_url':""}

			text = desc['property']
			if text:
				data['text'] = text

			# 获取图片数据
			pic_url = query_disease_property(slot['disease'], Disease.pic_url, sure)
			if pic_url:
				data['pic_url'] = pic_url['property']

			return data

	def _action_disease_diet(self, slot: dict, sure = False):
		diet_good = query_disease_property(slot['disease'], Disease.diet_good, sure)

		# 这里的diet_good有可能是按钮列表
		if not sure:
			return self._button_data_process(diet_good, "disease_diet")
		else:
			data = {'text': '', 'button': [], 'pic_url': "", "intent":"recipe_produce_way"}
			# 获取另外的属性
			good = diet_good['property']
			if good:
				data['text'] = good + "\n"

			diet_bad = query_disease_property(slot['disease'], Disease.diet_bad, sure)
			bad = diet_bad['property']
			if bad:
				data['text'] += bad

			recipe_list = query_disease_rels_recipe(slot['disease'], sure)
			if recipe_list:
				data['button'] = recipe_list

			if data['button'] and not data['text']:
				data['text'] = '{0}可以尝试以下食疗方式'.format(slot['disease'])

			if not (data['text'] and data['button']):
				data['text'] = '知识库暂无相关信息'

			return data

	def _action_disease_drug(self, slot: dict, sure = False):
		if not sure:
			data = query_disease(slot['disease'])
			return self._button_data_process(data, "disease_drug")
		else:
			drug_list = query_disease_rels_drug(slot['disease'], sure)
			return {'text': '{0}可以尝试以下药物'.format(slot['disease']), 'button': drug_list, 'pic_url': "", "intent":"drug_func"}

	def _action_disease_easy_get(self, slot:dict, sure=False):
		data = query_disease_property(slot['disease'], Disease.easy_get, sure)

		if not sure:
			return self._button_data_process(data, "disease_easy_get")
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_disease_neopathy(self, slot:dict, sure=False):
		if not sure:
			data = query_disease(slot['disease'])
			return self._button_data_process(data, "disease_neopathy")
		else:
			neopathy_list = query_disease_rels_neopathy(slot['disease'], sure)
			return {'text': '{0}常常会伴随有如下并发症'.format(slot['disease']), 'button': neopathy_list, 'pic_url': "", "intent":"disease_desc"}

	def _action_disease_prevent(self, slot:dict, sure=False):
		data = query_disease_property(slot['disease'], Disease.prevent, sure)

		if not sure:
			return self._button_data_process(data, "disease_prevent")
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_disease_symptom(self, slot:dict, sure=False):
		if not sure:
			data = query_disease(slot['disease'])
			return self._button_data_process(data, "disease_symptom")
		else:
			symptom_list = query_disease_rels_symptom(slot['disease'], sure)
			return {'text': '{0}常常会有{1}的症状'.format(slot['disease'], "，".join(symptom_list)), 'button': [], 'pic_url': ""}

	def _action_disease_treat_cost(self, slot:dict, sure=False):
		data = query_disease_property(slot['disease'], Disease.treat_cost, sure)

		if not sure:
			return self._button_data_process(data, "disease_treat_cost")
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_disease_treat_rate(self, slot:dict, sure=False):
		data = query_disease_property(slot['disease'], Disease.treat_rate, sure)

		if not sure:
			return self._button_data_process(data, "disease_treat_rate")
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_disease_treat_time(self, slot:dict, sure=False):
		data = query_disease_property(slot['disease'], Disease.treat_time, sure)

		if not sure:
			return self._button_data_process(data, "disease_treat_time")
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_disease_treat_way(self, slot:dict, sure=False):
		data = query_disease_property(slot['disease'], Disease.treat_way, sure)

		if not sure:
			return self._button_data_process(data, "disease_treat_way")
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_drug_func(self, slot:dict, sure=False):
		func = query_drug_property(slot['drug'], Drug.func, sure)

		if not sure:
			return self._button_data_process(func, "drug_func")
		else:
			data = {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}
			text = func['property']
			if text:
				data['text'] = text

			pic_url = query_drug_property(slot['drug'], Drug.pic_url, sure)
			if pic_url['property']:
				data['pic_url'] = pic_url['property']

		return data

	def _action_drug_price(self, slot:dict, sure=False):
		data = query_drug_property(slot['drug'], Drug.price, sure)

		if not sure:
			return self._button_data_process(data, "drug_price")
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_drug_use(self, slot:dict, sure=False):
		data = query_drug_property(slot['drug'], Drug.use, sure)

		if not sure:
			return self._button_data_process(data, "drug_use")
		else:
			text = data['property']
			if text:
				return {'text': text, 'button': [], 'pic_url': ""}
			else:
				return {'text': "知识库中暂无相关信息", 'button': [], 'pic_url': ""}

	def _action_recipe_produce_way(self, slot:dict, sure=False):
		produce_way = query_recipe_property(slot['recipe'], Recipe.produce_way)
		pic_url = query_recipe_property(slot['recipe'], Recipe.pic_url)

		data = {'text': '知识库中暂无相关信息', 'button': [], 'pic_url': ""}
		if produce_way['property']:
			data['text'] = produce_way['property']

		if pic_url['property']:
			data['pic_url'] = pic_url['property']

		return data

	'''对外开放的接口'''
	def intent_not_sure(self, username, sentence):
		'''处理文本，提取出意图类型，调用对应函数, 用getattr简化代码，不然要写很长的if判断'''
		intent, sure = IntentDetector.detect(username, sentence)

		if "_" not in intent:
			# 固定模板的intent
			response_data = getattr(self, '_action_{intent}'.format(intent = intent))()
		else:
			# 查询数据库的intent
			slot = IntentDetector.gain_slot(username)
			response_data = getattr(self, '_action_{intent}'.format(intent = intent))(slot, sure)


		print(response_data)
		print(IntentDetector.gain_slot(username))
		print("-"*50)
		return response_data

	def intent_button_sure(self, username, intent):
		'''进入这个方法的，都是按钮点进来的'''
		slot = IntentDetector.gain_slot(username)
		response_data = getattr(self, '_action_{intent}'.format(intent = intent))(slot, True)
		print(response_data)
		return response_data

	def set_slot(self, username, disease=None, drug=None, symptom=None, check=None, recipe=None):
		IntentDetector.update_slots(username, disease, drug, symptom, check, recipe)

	def set_single_slot(self, username, entity_name, content):
		IntentDetector.set_single_slot(username, entity_name, content)

IntentProcessor = IntentProcess()
if __name__ == '__main__':
	# 测试
	username = 'jezemy'

	IntentProcessor.set_slot(username, disease = "感冒")
	IntentProcessor.intent_not_sure(username, '是怎么引起的')
	IntentProcessor.intent_not_sure(username, '要去哪看病')
	IntentProcessor.intent_not_sure(username, '是什么')
	IntentProcessor.intent_not_sure(username, '饮食要注意什么')
	IntentProcessor.intent_not_sure(username, '吃什么药好')
	IntentProcessor.intent_not_sure(username, '谁比较容易得')
	IntentProcessor.intent_not_sure(username, '有什么并发症')
	IntentProcessor.intent_not_sure(username, '怎么预防')
	IntentProcessor.intent_not_sure(username, '一般有什么症状')
	IntentProcessor.intent_not_sure(username, '治疗要多少钱')
	IntentProcessor.intent_not_sure(username, '要治疗多久')
	IntentProcessor.intent_not_sure(username, '怎么治疗')

	IntentDetector.update_slots(username, drug = '广州白云山陈李济 上清丸')
	IntentProcessor.intent_button_sure(username, 'drug_func')
	IntentProcessor.intent_button_sure(username, 'drug_price')
	IntentProcessor.intent_button_sure(username, 'drug_use')
	IntentDetector.update_slots(username, recipe = "荔枝荷花蒸鸭")
	IntentProcessor.intent_button_sure(username, 'recipe_produce_way')