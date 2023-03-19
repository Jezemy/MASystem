from django.shortcuts import render
from django.http import JsonResponse
from contextual.IntentProcessor import IntentProcessor

'''
前端数据：
sentence = request.POST.get('msg')
username = request.POST.get('username')

返回数据：
{"code":"200", "response":text, "buttons":[]}

{"code":"200", "response":text}
'''

# Create your views here.
def indexPage(request):
	return render(request,'index.html')

def receiveMsg(request):
	sentence = request.POST.get('msg')
	username = request.POST.get('username')

	data_back = {"code": "200", "response": '', "buttons": [], 'pic_url':""}
	data = IntentProcessor.intent_not_sure(username, sentence)
	if data['text']:
		data_back['response'] = data['text']

	if data['button']:
		data_back['buttons'] = data['button']
		data_back['intent'] = data['intent']

	if data['pic_url']:
		data_back["pic_url"] = data['pic_url']



	return JsonResponse(data_back, safe = False)

def receiveBtn(request):
	entity = request.POST.get("msg")
	username = request.POST.get('username')
	intent = request.POST.get('intent')

	entity_name = intent.split("_")[0]
	IntentProcessor.set_single_slot(username, entity_name, entity)
	data = IntentProcessor.intent_button_sure(username, intent)
	data_back = {"code":"200", "response":data['text'], "pic_url":""}
	if data['pic_url']:
		data_back['pic_url'] = data['pic_url']
	return JsonResponse(data_back, safe = False)

def getTest(request):
	return JsonResponse({"code":"200","content":"connect successfully"}, safe = False)