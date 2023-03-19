# coding=utf-8
'''
移植到telegram上
'''

import telebot
from telebot.types import *
from contextual.IntentProcessor import IntentProcessor
import json
import requests
import re

TOKEN = '改成自己的TelegramBotID'

bot = telebot.TeleBot(TOKEN, parse_mode = None)  # You can set parse_mode by default. HTML or MARKDOWN


@bot.message_handler(commands = ['start', 'help'])
def send_welcome(message):
	bot.send_message(message.chat.id, "你好，我是你的私人医疗助理")
	inform = '''您可以这样向我提问：\n感冒怎么办\n什么人容易感冒\n感冒吃什么药\n感冒属于什么科\n如何防止感冒\n感冒要治多久\n感冒有什么并发症状\n感冒有什么症状\n感冒治疗几率大吗\n上清丸可以治什么病'''
	bot.send_message(message.chat.id, inform)

def generateMarkupButton(names:list, intent):
	markup = InlineKeyboardMarkup()
	buttons = []

	for name in names:
		buttons.append(InlineKeyboardButton(name, callback_data = name+"#"+intent))
	markup.add(*buttons, row_width = 3)
	return markup

def sendPhoto(chat_id, pic_url):
	pattern = '\.[a-z]{3,4}'
	file_type = re.findall(pattern, pic_url)[-1]
	file_name = 'telegramPhotoTemp' + file_type
	rp = requests.get(pic_url)
	with open(file_name, 'wb') as f:
		f.write(rp.content)
	photo = open(file_name, 'rb')
	bot.send_photo(chat_id, photo)
	photo.close()

@bot.message_handler(func = lambda m: m.text is not None)
def receiveMsg(message):
	sentence = message.text
	username = message.chat.first_name
	print("receiveMsg: ", sentence, username)
	data = IntentProcessor.intent_not_sure(username,sentence)


	if data["button"]:
		button_names = [name for name in data['button']]
		intent = data['intent']
		markup = generateMarkupButton(button_names, intent)
		bot.send_message(message.chat.id, data['text'], reply_markup = markup)
	else:
		bot.send_message(message.chat.id, data['text'])

	if data['pic_url']:
		sendPhoto(message.chat.id, data['pic_url'])

@bot.callback_query_handler(func=lambda call: True)
def receiveBtn(call):
	username=call.message.json['chat']['first_name']
	data_str = call.data

	entity,intent = data_str.split("#")
	entity_name = intent.split("_")[0]

	print("receiveMsg: ",entity, intent)
	IntentProcessor.set_single_slot(username, entity_name, entity)

	data = IntentProcessor.intent_button_sure(username, intent)
	chat_id = call.message.json['chat']['id']
	bot.send_message(chat_id, data['text'])
	if data['button']:
		button_names = [name for name in data['button']]
		intent = data['intent']
		markup = generateMarkupButton(button_names, intent)
		bot.send_message(chat_id, "可以试试如下食疗", reply_markup = markup)

	if data['pic_url']:
		sendPhoto(chat_id, data['pic_url'])

bot.polling()