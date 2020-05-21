import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
import settings
from multiprocessing import Process
from datetime import datetime
import traceback
session = vk_api.VkApi(token=settings.key)
session.get_api()
longpoll = VkBotLongPoll(session, 193803197)
methods = session.get_api()
import psycopg2
import sql
import time
import menu
from vkcoinapi import *
from vk_api import VkUpload
from vkcoinapi import *
import random
#methods.messages.send(peer_id=peer_id,random_id=0,message='#.',keyboard=interface())
#refflink = https://vk.me/public189535455?ref=123
rooms_choicez = ['Заходим в беседу https://vk.me/join/AJQ1d_8XWhe8Tcs6LCcaZXDF']
def get_username(userid):
	name = methods.users.get(user_ids=userid)
	name = name[0]['first_name'] + ' ' + name[0]['last_name']
	return name

def messages_send(roomid,message,menu):
	methods.messages.send(peer_id=roomid,random_id=0,message=message,keyboard=menu)

def messages_sendgroup(userid,message):
	methods.messages.send(user_id=userid,random_id=0,message=message,keyboard=menu.groupmenu())

def runbot():
	while True:
		try:
			for event in longpoll.listen():
				if event.type == VkBotEventType.MESSAGE_NEW:
					userid = event.object.from_id
					roomid = event.object.peer_id
					text = event.object.text.lower()
					print(roomid)
					print(text)
					if event.object.action != None:
						if event.object.action['type'] == 'chat_invite_user_by_link':
							sql.UserReg(userid,get_username(userid),'None')
					if (text == '[club193803197|@winwheelcoronacoin] банк' or text == '[club193803197|win wheel corona coin] банк'):
						sql.GetBank(roomid)
					elif (text == '[club193803197|@winwheelcoronacoin] баланс' or text == '[club193803197|win wheel corona coin] баланс'):
						message = sql.GetBalance(userid)
						messages_send(roomid,message,menu.main())
					elif (text == '[club193803197|@winwheelcoronacoin] чётное' or text == '[club193803197|win wheel corona coin] чётное'):
						sql.SetChoice(userid,roomid,'even','чётное')
					elif (text == '[club193803197|@winwheelcoronacoin] нечётное' or text == '[club193803197|win wheel corona coin] нечётное'):
						sql.SetChoice(userid,roomid,'odd','нечётное')
					elif (text == '[club193803197|@winwheelcoronacoin] красное' or text == '[club193803197|win wheel corona coin] красное'):
						sql.SetChoice(userid,roomid,'red','красное')
					elif (text == '[club193803197|@winwheelcoronacoin] чёрное' or text == '[club193803197|win wheel corona coin] чёрное'):
						sql.SetChoice(userid,roomid,'black','чёрное')
					elif (text == '[club193803197|@winwheelcoronacoin] 1-12' or text == '[club193803197|win wheel corona coin] 1-12'):
						sql.SetChoice(userid,roomid,'first_gap','промежуток 1-12')
					elif (text == '[club193803197|@winwheelcoronacoin] 13-24' or text == '[club193803197|win wheel corona coin] 13-24'):
						sql.SetChoice(userid,roomid,'second_gap','промежуток 13-24')
					elif (text == '[club193803197|@winwheelcoronacoin] 25-36' or text == '[club193803197|win wheel corona coin] 25-36'):
						sql.SetChoice(userid,roomid,'third_gap','промежуток 25-36')
					elif (text == '[club193803197|@winwheelcoronacoin] на число' or text == '[club193803197|win wheel corona coin] на число'):
						sql.SetChoiceNumber(userid)
						messages_send(roomid,F"{get_username(userid).split()[0]}, на какое число ты ставишь?",menu.main())
					elif (text == '[club193803197|@winwheelcoronacoin] вывод' or text == '[club193803197|win wheel corona coin] вывод'):
						sql.withdraw(roomid,userid)
					elif text == 'adminpanel':
						if userid == 387159377:
							messages_send(387159377,'Админка',menu.adminpanel())
					elif 'addbonusbalance' in text:
						if userid == 387159377:
							try:
								text = text.split()
								userid = int(text[1])
								value = int(text[2])
								kek = "{:,}".format(value).replace(',',' ')
								messages_send(387159377,F"userid: {userid}\nВыдан бонусный баланс: {kek}",menu.adminpanel())
								sql.addbonus_balance(userid,value)	
							except:
								print('bag')
					elif 'addbalance' in text:
						if userid == 387159377:
							try:
								text = text.split()
								userid = int(text[1])
								value = int(text[2])
								kek = "{:,}".format(value).replace(',',' ')
								messages_send(387159377,F"userid: {userid}\nВыдан баланс: {kek}",menu.adminpanel())
								sql.addbalance(userid,value)	
							except:
								print('bag')
					elif text == 'обновить топ':
						if userid == 387159377:
							sql.admin_updatetop()
							messages_send(387159377,'Топ обнулён',menu.adminpanel())
					elif text == 'обновить репосты':
						if userid == 387159377:
							sql.admin_updaterepost()
							messages_send(387159377,'Репосты обновлены',menu.adminpanel())
					elif text == 'выдать баланс':
						if userid == 387159377:
							messages_send(387159377,'Выдать баланс:\naddbalance userid value\nВыдать бонусный баланс:\naddbonusbalance userid value',menu.adminpanel())
					elif text.isdigit():
						bet = int(text)
						sql.acceptbet(userid,roomid,bet)
					elif text[36:].isdigit():
						bet = int(text[36:])
						sql.acceptbet(userid,roomid,bet)
					elif text[38:].isdigit():
						bet = int(text[38:])
						sql.acceptbet(userid,roomid,bet)
					elif text == 'начать':
						try: #Если перешёл по реф ссылк
							invited_from = event.object.ref
							sql.UserReg(userid,get_username(userid),invited_from)
						except:
							sql.UserReg(userid,get_username(userid),'None')
						messages_send(userid,'Добро пожаловать',menu.groupmenu())
					elif text == 'найти беседу':
						messages_send(userid,random.choice(rooms_choicez),menu.groupmenu())
					elif text == 'профиль':
						messages_send(userid,sql.getprofile(userid),menu.groupmenu())
					elif text == 'топ игроков':
						messages_send(userid,sql.get_top(),menu.groupmenu())

				elif event.type == VkBotEventType.WALL_REPOST:
					try:
						userid = event.object.from_id
						getsub = methods.groups.isMember(group_id=193803197,user_id=userid)
						if getsub == 1:
							sql.repost(userid)
					except Exception:
						traceback.print_exc()	
		except Exception:
			sql.UserReg(userid,get_username(userid),'None')
			traceback.print_exc()
def rollbot():
	while True:
		try:
			time.sleep(1)
			sql.rounds()
		except Exception:
			traceback.print_exc()
def checkcoin():
	while True:
		try:
			sql.deposits()
			time.sleep(2)
		except Exception:
			traceback.print_exc()
if __name__ == '__main__':
	try:
		Process(target=runbot).start()
		Process(target=rollbot).start()
		Process(target=checkcoin).start()
	except Exception:
		traceback.print_exc()