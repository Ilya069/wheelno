import psycopg2
from psycopg2 import sql
from datetime import datetime
import time
import settings
import vk_api
import menu
import hashlib
import random
from vkcoinapi import *
import ast
import traceback
import requests
from datetime import datetime
from datetime import timedelta
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
session = vk_api.VkApi(token=settings.key)
methods = session.get_api()
def get_username(userid):
	name = methods.users.get(user_ids=userid)
	name = name[0]['first_name'] + ' ' + name[0]['last_name']
	return name
imgarray = ['photo-193803197_457239066','photo-193803197_457239067','photo-193803197_457239068',
			'photo-193803197_457239069','photo-193803197_457239070','photo-193803197_457239071',
			'photo-193803197_457239072','photo-193803197_457239073','photo-193803197_457239074',
			'photo-193803197_457239075','photo-193803197_457239076','photo-193803197_457239077',
			'photo-193803197_457239078','photo-193803197_457239079','photo-193803197_457239080',
			'photo-193803197_457239081','photo-193803197_457239082','photo-193803197_457239083',
			'photo-193803197_457239084','photo-193803197_457239085','photo-193803197_457239086',
			'photo-193803197_457239087','photo-193803197_457239088','photo-193803197_457239089',
			'photo-193803197_457239090','photo-193803197_457239091','photo-193803197_457239092',
			'photo-193803197_457239093','photo-193803197_457239094','photo-193803197_457239095',
			'photo-193803197_457239096','photo-193803197_457239097','photo-193803197_457239061',
			'photo-193803197_457239062','photo-193803197_457239063','photo-193803197_457239064']
imgzero = 'photo-193803197_457239065'
symbolsz = {'red':'красное','black':'чёрное','blue':'чёрное'}
def get_withdraw():
	url = 'https://corona-coins.ru/api/'
	headers = {'content-type': 'application/json'}
	payload = {'token':'sV6m66q8x5QL8ESKAwV3DiKVybYumFkL','method':'score','user_ids':[505458404]}
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	coins = r.json()['response'][0]['coins']
	return int(coins)
def message_win_send(roomid,message,winimg):
	attachments = [winimg]
	methods.messages.send(peer_id=roomid,random_id=0,message=message,attachment=','.join(attachments))

def messages_send(roomid,message,menu):
	try:
		methods.messages.send(peer_id=roomid,random_id=0,message=message,keyboard=menu)
	except Exception:
		traceback.print_exc()

def messages_sendgroup(userid,message):
	methods.messages.send(user_id=userid,random_id=0,message=message,keyboard=menu.groupmenu())

def addbalance(userid,value):
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"SELECT * FROM goldenusers WHERE userid = '{userid}'")
			user = cursor.fetchall()[0]
			balance = int(user[2])
			balance = balance + value
			cursor.execute(F"UPDATE goldenusers SET balance = '{balance}' WHERE userid = '{userid}'")
			try:
				messages_sendgroup(userid,F"✅ Зачислено {value} коинов")
			except:
				pass
	except Exception:
		traceback.print_exc()
def addbonus_balance(userid,value):
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"SELECT * FROM goldenusers WHERE userid = '{userid}'")
			user = cursor.fetchall()[0]
			bonus_balance = int(user[3])
			bonus_balance = bonus_balance + value
			cursor.execute(F"UPDATE goldenusers SET bonus_balance = '{bonus_balance}' WHERE userid = '{userid}'")
	except Exception:
		traceback.print_exc()


def UserReg(userid,username,invited_from):
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"SELECT EXISTS(SELECT 1 from goldenusers where userid = '{userid}')")
			if cursor.fetchall()[0][0] == True:
				pass
			else:
				cursor.execute(F"INSERT INTO goldenusers (userid,username,balance,bonus_balance,wins_all,wins_today,last_choice,max_bet,repost) VALUES ('{userid}','{username}','0','250000','0','0','None','0','0')")
	except Exception:
		traceback.print_exc()

def GetBalance(userid):
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"SELECT username,balance,bonus_balance FROM goldenusers WHERE userid = '{userid}'")
			userget = cursor.fetchall()[0]
			username = userget[0].split()[0]
			balance = int(userget[1])
			bonus_balance = userget[2]
			balance = "{:,}".format(balance).replace(',',' ')
			ggbonus = "{:,}".format(int(bonus_balance)).replace(',',' ')
			if bonus_balance != 0:
				message = F'*id{userid} ({username}), твой баланс: {balance}\nБонусный баланс: {ggbonus}'
			else:
				message = F'*id{userid} ({username}), твой баланс: {balance}'
		return message
	except Exception:
		traceback.print_exc()


def SetChoice(userid,roomid,choice,choicename):
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"SELECT username,balance,bonus_balance FROM goldenusers WHERE userid = '{userid}'")
			userget = cursor.fetchone()
			username = userget[0].split()[0]
			balance = int(userget[1]) + int(userget[2])
			if (balance > 200000000) or (balance <= 10):
				balance = 300000000

			cursor.execute(F"UPDATE goldenusers SET last_choice = '{choice}' WHERE userid = '{userid}'")
			message = F"{username}, введи ставку на {choicename} или нажми кнопку:"
			keyboard = VkKeyboard(inline=True)
			keyboard.add_button(F"{round(balance * 0.1)}", color=VkKeyboardColor.DEFAULT)
			keyboard.add_line()
			keyboard.add_button(F"{round(balance * 0.25)}", color=VkKeyboardColor.DEFAULT)
			keyboard.add_line()
			keyboard.add_button(F"{round(balance)}", color=VkKeyboardColor.DEFAULT)
			methods.messages.send(peer_id=roomid,random_id=0,message=message,keyboard=keyboard.get_keyboard())
	except Exception:
		traceback.print_exc()
		
def SetChoiceNumber(userid):
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"UPDATE goldenusers SET last_choice = 'numbers',last_number = 'None' WHERE userid = '{userid}'")
	except Exception:
		traceback.print_exc()

def acceptbet(userid,roomid,bet):
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"SELECT rolltime FROM goldenrooms")
			rolltime = cursor.fetchone()[0]
			roomrolltime = datetime.strptime(rolltime, '%Y-%m-%d %H:%M:%S')
			timenow = datetime.now()
			seconds = (timenow - roomrolltime).seconds
			if seconds >= 55:
				pass
			else:
				value = {'black':0,'red':1,'odd':2,'even':3,'numbers':4,'first_gap':5,'second_gap':6,'third_gap':7}
				userid = int(userid)
				cursor.execute(F"SELECT * FROM goldenusers WHERE userid = '{userid}'")
				userinfo = cursor.fetchone()
				name = userinfo[1].split()[0]
				balance = int(userinfo[2])
				bonus_balance = int(userinfo[3])
				textchoice = userinfo[6]
				get_number = userinfo[9]
				if textchoice == 'numbers':
					if get_number == 'None':
						if (bet >= 0) and (bet <= 36):
							cursor.execute(F"UPDATE goldenusers SET last_number = '{bet}'")
							messages_send(roomid,F"{name}, введи ставку на число {bet}:",menu.main())
							return 'hello'
						else:
							return 'hello'
				if textchoice != 'None':
					maxbet = int(userinfo[7])
					maxbet += bet
					if (maxbet <= 100900000000) and (bet > 99):
						if balance + bonus_balance >= bet:
							if balance - bet >= 0:
								newbalance = balance - bet
								cursor.execute(F"UPDATE goldenusers SET balance = '{newbalance}',last_choice = 'None',max_bet = '{maxbet}',last_number = 'None' WHERE userid = '{userid}'")
							elif balance - bet < 0:
								newbalance = 0
								newbonus_balance = bonus_balance - (bet - balance)
								cursor.execute(F"UPDATE goldenusers SET balance = '{newbalance}',bonus_balance = '{newbonus_balance}',last_choice = 'None',max_bet = '{maxbet}',last_number = 'None' WHERE userid = '{userid}'")
							cursor.execute(F"SELECT black,red,odd,even,numbers,first_gap,second_gap,third_gap FROM goldenrooms WHERE room_id = '{roomid}'")
							roominfo = cursor.fetchone()
							choice = roominfo[value[textchoice]]
							if textchoice == 'numbers':
								if choice == 'None': 
									bets = F"[{userid},{bet},{get_number}]"
									cursor.execute(F"UPDATE goldenrooms SET {textchoice} = '{bets}',play = 'Yes' WHERE room_id = '{roomid}'")
									message = F"{name}, успешная ставка {bet} коинов на число {get_number}"
									messages_send(roomid,message,menu.main())
								else:
									bets = ast.literal_eval(choice)
									g = False
									if userid in bets:
										k = 0
										for i in bets:
											if (int(i) == int(userid)) and (int(bets[k + 2]) == int(get_number)):
												lastbet = bets[k + 1]
												nowbet = lastbet + bet
												bets[k + 1] = nowbet
												g = True
											k += 1
										if g == False:
											bets.append(int(userid))
											bets.append(int(bet))
											bets.append(int(get_number))
									else:
										bets.append(int(userid))
										bets.append(int(bet))
										bets.append(int(get_number))
									cursor.execute(F"UPDATE goldenrooms SET {textchoice} = '{bets}',play = 'Yes' WHERE room_id = '{roomid}'")
									bet = "{:,}".format(bet).replace(',',',')
									message = F"{name}, успешная ставка {bet} коинов на число {get_number}"
									messages_send(roomid,message,menu.main())
							else:
								if choice == 'None': 
									bets = F"[{userid},{bet}]"
									cursor.execute(F"UPDATE goldenrooms SET {textchoice} = '{bets}',play = 'Yes' WHERE room_id = '{roomid}'")
								else:
									bets = ast.literal_eval(choice)
									if userid in bets:
										choiceid = bets.index(userid)
										lastbet = bets[choiceid + 1]
										nowbet = lastbet + bet
										bets[choiceid + 1] = nowbet
									else:
										bets.append(int(userid))
										bets.append(int(bet))
									cursor.execute(F"UPDATE goldenrooms SET {textchoice} = '{bets}',play = 'Yes' WHERE room_id = '{roomid}'")
								bet = "{:,}".format(bet).replace(',',' ')
								message = F"{name}, успешная ставка {bet} коинов"
								messages_send(roomid,message,menu.main())
						else:
							cursor.execute(F"UPDATE goldenusers SET last_choice = 'None',last_number = 'None' WHERE userid = '{userid}'")
							message = F"{name}, на вашем балансе недостаточно средств."
							messages_send(roomid,message,menu.main())
					else:
						cursor.execute(F"UPDATE goldenusers SET last_choice = 'None',last_number = 'None' WHERE userid = '{userid}'")
						message = F"{name}, максимальная сумма ставок: 100900000000 коинов, минимальная: 100."
						messages_send(roomid,message,menu.main())
	except Exception:
		traceback.print_exc()

def rounds():
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"SELECT * FROM goldenrooms")
			rooms = cursor.fetchall()
			for room in rooms:
				randompass = ''
				messagelose = ''
			#	timenow = datetime.now().strftime('%Y-%m-%d %H:%M:%S') когда добавляем в бд
				timenow = datetime.now()
				room_id = room[0]
				roomrolltime = datetime.strptime(room[1], '%Y-%m-%d %H:%M:%S')
				dropvalue = int(room[2]) # Выпавший коэффициент
				dropcolor = room[3]
				if dropvalue == 0:
					messagewin = F'Выпало число 0!\n\n'
					winimg = imgzero
				else:
					winimg = imgarray[dropvalue - 1]
					messagewin = F'Выпало число {dropvalue}, {symbolsz[dropcolor]}\n\n'
				black = room[4]
				red = room[5]
				odd = room[6]
				even = room[7]
				numbers = room[8]
				play = room[12]
				first_gap = room[9]
				second_gap = room[10]
				third_gap = room[11]
				room_hash = room[13]
				hash_decode = room[14]
				seconds = (timenow - roomrolltime).seconds
				if seconds >= 60:
					if play == 'No':
						timenow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
						cursor.execute(F"UPDATE goldenrooms SET rolltime = '{timenow}' Where room_id = '{room_id}'")
						continue
					timenow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					cursor.execute(F"UPDATE goldenrooms SET black = 'None',red = 'None',odd = 'None',even = 'None',numbers = 'None',first_gap = 'None',second_gap = 'None',third_gap = 'None',play = 'No' Where room_id = '{room_id}'")
	#------------------------------------------------------------------
	#------------------------------------------------------------------
	#------------------------------------------------------------------
					if dropvalue != 0: # Если != 0
						if dropvalue % 2 == 0: # если чётное
							if even != 'None':
								roombets = ast.literal_eval(even)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
										userinfo = cursor.fetchone()
										username = userinfo[0]
										userbalance = round(int(userinfo[1]) + roombets[bet+1] * 2)
										wins_all = int(userinfo[2]) + round(roombets[bet+1] * 2)
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										cursor.execute(F"UPDATE goldenusers set balance = '{userbalance}',wins_all= '{wins_all}',wins_today = '{wins_all}' WHERE userid = '{userid}'")
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										prize = "{:,}".format(round(roombets[bet+1] * 2)).replace(',',' ')
										messagewin += F"✅ {username} ставка {stavka} на чётное выиграла! (приз {prize} коинов)\n"
							if odd != 'None':
								roombets = ast.literal_eval(odd)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на нечётное проиграла\n"
						else:
							if odd != 'None':
								roombets = ast.literal_eval(odd)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
										userinfo = cursor.fetchone()
										username = userinfo[0]
										userbalance = round(int(userinfo[1]) + roombets[bet+1] * 2)
										wins_all = int(userinfo[2]) + round(roombets[bet+1] * 2)
										cursor.execute(F"UPDATE goldenusers set balance = '{userbalance}',wins_all= '{wins_all}',wins_today = '{wins_all}' WHERE userid = '{userid}'")
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										prize = "{:,}".format(round(roombets[bet+1] * 2)).replace(',',' ')
										messagelose += F"✅ {username} ставка {stavka} на нечётное выиграла! (приз {prize} коинов)\n"
							if even != 'None':
								roombets = ast.literal_eval(even)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на чётное проиграла\n"
	#------------------------------------------------------------------
	#------------------------------------------------------------------
	#------------------------------------------------------------------				
				
						if dropcolor == 'black':
							if black != 'None':
								roombets = ast.literal_eval(black)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
										userinfo = cursor.fetchone()
										username = userinfo[0]
										userbalance = round(int(userinfo[1]) + roombets[bet+1] * 2)
										wins_all = int(userinfo[2]) + round(roombets[bet+1] * 2)
										cursor.execute(F"UPDATE goldenusers set balance = '{userbalance}',wins_all= '{wins_all}',wins_today = '{wins_all}' WHERE userid = '{userid}'")
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										prize = "{:,}".format(round(roombets[bet+1] * 2)).replace(',',' ')
										messagewin += F"✅ {username} ставка {stavka} на чёрное выиграла! (приз {prize} коинов)\n"
							if red != 'None':
								roombets = ast.literal_eval(red)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на красное проиграла\n"
						else:
							if black != 'None':
								roombets = ast.literal_eval(black)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на чёрное проиграла\n"
							if red != 'None':
								roombets = ast.literal_eval(red)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
										userinfo = cursor.fetchone()
										username = userinfo[0]
										userbalance = round(int(userinfo[1]) + roombets[bet+1] * 2)
										wins_all = int(userinfo[2]) + round(roombets[bet+1] * 2)
										cursor.execute(F"UPDATE goldenusers set balance = '{userbalance}',wins_all= '{wins_all}',wins_today = '{wins_all}' WHERE userid = '{userid}'")
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										prize = "{:,}".format(round(roombets[bet+1] * 2)).replace(',',' ')
										messagewin += F"✅ {username} ставка {stavka} на красное выиграла! (приз {prize} коинов)\n"


						if dropvalue in range(1,13):
							if first_gap != 'None':
								roombets = ast.literal_eval(first_gap)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
										userinfo = cursor.fetchone()
										username = userinfo[0]
										userbalance = round(int(userinfo[1]) + roombets[bet+1] * 3)
										wins_all = int(userinfo[2]) + round(roombets[bet+1] * 3)
										cursor.execute(F"UPDATE goldenusers set balance = '{userbalance}',wins_all= '{wins_all}',wins_today = '{wins_all}' WHERE userid = '{userid}'")
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										prize = "{:,}".format(round(roombets[bet+1] * 3)).replace(',',' ')
										messagewin += F"✅ {username} ставка {stavka} на 1-12 выиграла! (приз {prize} коинов)\n"
							if second_gap != 'None':
								roombets = ast.literal_eval(second_gap)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на 13-24 проиграла\n"
							if third_gap != 'None':
								roombets = ast.literal_eval(third_gap)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на 25-36 проиграла\n"
						elif dropvalue in range(13,25):
							if first_gap != 'None':
								roombets = ast.literal_eval(first_gap)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на 1-12 проиграла\n"
							if second_gap != 'None':
								roombets = ast.literal_eval(second_gap)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
										userinfo = cursor.fetchone()
										username = userinfo[0]
										userbalance = round(int(userinfo[1]) + roombets[bet+1] * 3)
										wins_all = int(userinfo[2]) + round(roombets[bet+1] * 3)
										cursor.execute(F"UPDATE goldenusers set balance = '{userbalance}',wins_all= '{wins_all}',wins_today = '{wins_all}' WHERE userid = '{userid}'")
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										prize = "{:,}".format(round(roombets[bet+1] * 3)).replace(',',' ')
										messagewin += F"✅ {username} ставка {stavka} на 13-24 выиграла! (приз {prize} коинов)\n"
							if third_gap != 'None':
								roombets = ast.literal_eval(third_gap)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на 25-36 проиграла\n"
						elif dropvalue in range(25,37):
							if first_gap != 'None':
								roombets = ast.literal_eval(first_gap)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на 1-12 проиграла\n"
							if second_gap != 'None':
								roombets = ast.literal_eval(second_gap)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
										cursor.execute(getusername)
										userinfo = cursor.fetchone()
										username = userinfo[0]
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										messagelose += F"❌ {username} ставка {stavka} на 13-24 проиграла\n"
							if third_gap != 'None':
								roombets = ast.literal_eval(third_gap)
								roombetsvalue = len(roombets)
								for bet in range(roombetsvalue):
									if bet % 2 == 0:
										userid = roombets[bet]
										cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
										cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
										userinfo = cursor.fetchone()
										username = userinfo[0]
										userbalance = round(int(userinfo[1]) + roombets[bet+1] * 3)
										wins_all = int(userinfo[2]) + round(roombets[bet+1] * 3)
										cursor.execute(F"UPDATE goldenusers set balance = '{userbalance}',wins_all= '{wins_all}',wins_today = '{wins_all}' WHERE userid = '{userid}'")
										stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
										prize = "{:,}".format(round(roombets[bet+1] * 3)).replace(',',' ')
										messagewin += F"✅ {username} ставка {stavka} на 25-36 выиграла! (приз {prize} коинов)\n"
						if numbers != 'None':
							roombets = ast.literal_eval(numbers)
							roombetsvalue = len(roombets)
							for bet in range(roombetsvalue):
								if bet % 3 == 0:
									userid = roombets[bet]
									cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
									cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
									userinfo = cursor.fetchone()
									username = userinfo[0]
									userbalance = round(int(userinfo[1]) + roombets[bet+1] * 13)
									wins_all = int(userinfo[2]) + round(roombets[bet+1] * 13)
									stavka = "{:,}".format(roombets[bet + 1]).replace(',',',')
									if dropvalue == roombets[bet + 2]:
										cursor.execute(F"UPDATE goldenusers set balance = '{userbalance}',wins_all= '{wins_all}',wins_today = '{wins_all}' WHERE userid = '{userid}'")
										prize = "{:,}".format(round(roombets[bet+1] * 13)).replace(',',',')
										messagewin += F"✅ {username} ставка {stavka} на число {roombets[bet + 2]} выиграла! (приз {prize} коинов)\n"
									else:
										messagelose += F"❌ {username} ставка {stavka} на число {roombets[bet + 2]} проиграла\n"
					else:
						if even != 'None':
							roombets = ast.literal_eval(even)
							roombetsvalue = len(roombets)
							for bet in range(roombetsvalue):
								if bet % 2 == 0:
									userid = roombets[bet]
									cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
									getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
									cursor.execute(getusername)
									userinfo = cursor.fetchone()
									username = userinfo[0]
									stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
									messagelose += F"❌ {username} ставка {stavka} на чётное проиграла\n"
						if odd != 'None':
							roombets = ast.literal_eval(odd)
							roombetsvalue = len(roombets)
							for bet in range(roombetsvalue):
								if bet % 2 == 0:
									userid = roombets[bet]
									cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
									getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
									cursor.execute(getusername)
									userinfo = cursor.fetchone()
									username = userinfo[0]
									stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
									messagelose += F"❌ {username} ставка {stavka} на нечётное проиграла\n"
						if black != 'None':
							roombets = ast.literal_eval(black)
							roombetsvalue = len(roombets)
							for bet in range(roombetsvalue):
								if bet % 2 == 0:
									userid = roombets[bet]
									cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
									getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
									cursor.execute(getusername)
									userinfo = cursor.fetchone()
									username = userinfo[0]
									stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
									messagelose += F"❌ {username} ставка {stavka} на чёрное проиграла\n"
						if red != 'None':
							roombets = ast.literal_eval(red)
							roombetsvalue = len(roombets)
							for bet in range(roombetsvalue):
								if bet % 2 == 0:
									userid = roombets[bet]
									cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
									getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
									cursor.execute(getusername)
									userinfo = cursor.fetchone()
									username = userinfo[0]
									stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
									messagelose += F"❌ {username} ставка {stavka} на красное проиграла\n"
						if first_gap != 'None':
							roombets = ast.literal_eval(first_gap)
							roombetsvalue = len(roombets)
							for bet in range(roombetsvalue):
								if bet % 2 == 0:
									userid = roombets[bet]
									cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
									getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
									cursor.execute(getusername)
									userinfo = cursor.fetchone()
									username = userinfo[0]
									stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
									messagelose += F"❌ {username} ставка {stavka} на 1-12 проиграла\n"
						if second_gap != 'None':
							roombets = ast.literal_eval(second_gap)
							roombetsvalue = len(roombets)
							for bet in range(roombetsvalue):
								if bet % 2 == 0:
									userid = roombets[bet]
									cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
									getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
									cursor.execute(getusername)
									userinfo = cursor.fetchone()
									username = userinfo[0]
									stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
									messagelose += F"❌ {username} ставка {stavka} на 13-24 проиграла\n"
						if third_gap != 'None':
							roombets = ast.literal_eval(third_gap)
							roombetsvalue = len(roombets)
							for bet in range(roombetsvalue):
								if bet % 2 == 0:
									userid = roombets[bet]
									cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
									getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
									cursor.execute(getusername)
									userinfo = cursor.fetchone()
									username = userinfo[0]
									stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
									messagelose += F"❌ {username} ставка {stavka} на 25-36 проиграла\n"
						if numbers != 'None':
							roombets = ast.literal_eval(numbers)
							roombetsvalue = len(roombets)
							for bet in range(roombetsvalue):
								if bet % 3 == 0:
									userid = roombets[bet]
									cursor.execute(F"UPDATE goldenusers set max_bet = '0', last_number = 'None' Where userid = '{userid}'")
									cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
									userinfo = cursor.fetchone()
									username = userinfo[0]
									userbalance = round(int(userinfo[1]) + roombets[bet+1] * 13)
									wins_all = int(userinfo[2]) + round(roombets[bet+1] * 13)
									stavka = "{:,}".format(roombets[bet + 1]).replace(',',',')
									if dropvalue == roombets[bet + 2]:
										cursor.execute(F"UPDATE goldenusers set balance = '{userbalance}',wins_all= '{wins_all}',wins_today = '{wins_all}' WHERE userid = '{userid}'")
										prize = "{:,}".format(round(roombets[bet+1] * 13)).replace(',',',')
										messagewin += F"✅ {username} ставка {stavka} на число {roombets[bet + 2]} выиграла! (приз {prize} коинов)\n"
									else:
										messagelose += F"❌ {username} ставка {stavka} на число {roombets[bet + 2]} проиграла\n"
	#------------------------------------------------------------------
	#------------------------------------------------------------------
	#------------------------------------------------------------------

					messagewin += messagelose
					messagewin += F'\n\nХэш игры: {room_hash}\nПроверка честности: {hash_decode}'
					for i in range(15):
						randompass += random.choice(chars)
					dropvalue = random.randint(1,38)
					if (dropvalue == 37) or (dropvalue == 38):
						dropvalue = 0
					else:
						dropvalue = dropvalue
					if (dropvalue >= 1 and dropvalue <= 18):
						color = 'red'
					else:
						color = 'black'
					if color == 'black':
						ss = 'black'
					else:
						ss = 'red'
					if dropvalue == 0:
						hashdecode = F"{dropvalue}|zero|{randompass}"
						md5hash = hashlib.md5(hashdecode.encode()).hexdigest()
					else:
						hashdecode = F"{dropvalue}|{ss}|{randompass}"
						md5hash = hashlib.md5(hashdecode.encode()).hexdigest()
					cursor.execute(F"UPDATE goldenrooms SET rolltime ='{timenow}',dropvalue ='{dropvalue}',dropcolor = '{color}',hash = '{md5hash}',hash_decode = '{hashdecode}' WHERE room_id = '{room_id}'")
					messages_send(room_id,'Итак, результаты раунда...',menu.main())
					time.sleep(1)
					message_win_send(room_id,messagewin,winimg)
	except Exception:
		traceback.print_exc()

def GetBank(roomid):
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			messagebank = ''
			allbets = 0
			cursor.execute(F"SELECT * FROM goldenrooms where room_id = '{roomid}'")
			room = cursor.fetchone()
			roomid = room[0]
			rolltime = room[1]
			timenow = datetime.now()
			roomrolltime = datetime.strptime(rolltime, '%Y-%m-%d %H:%M:%S')
			black = room[4]
			red = room[5]
			odd = room[6]
			even = room[7]
			numbers = room[8]
			play = room[12]
			first_gap = room[9]
			second_gap = room[10]
			third_gap = room[11]
			room_hash = room[13]
			if black != 'None':
				messagebank +='\n'
				messagebank += 'Ставки на чёрное:\n'
				roombets = ast.literal_eval(black)
				roombetsvalue = len(roombets)
				for bet in range(roombetsvalue):
					if bet % 2 == 0:
						userid = roombets[bet]
						getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
						cursor.execute(getusername)
						userinfo = cursor.fetchone()
						username = userinfo[0]
						allbets += roombets[bet + 1]
						stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
						messagebank += F"{username} - {stavka} коинов\n"
			if red != 'None':
				messagebank +='\n'
				messagebank += 'Ставки на красное:\n'
				roombets = ast.literal_eval(red)
				roombetsvalue = len(roombets)
				for bet in range(roombetsvalue):
					if bet % 2 == 0:
						userid = roombets[bet]
						getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
						cursor.execute(getusername)
						userinfo = cursor.fetchone()
						username = userinfo[0]
						allbets += roombets[bet + 1]
						stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
						messagebank += F"{username} - {stavka} коинов\n"
			if even != 'None':
				messagebank +='\n'
				messagebank += 'Ставки на чётное:\n'
				roombets = ast.literal_eval(even)
				roombetsvalue = len(roombets)
				for bet in range(roombetsvalue):
					if bet % 2 == 0:
						userid = roombets[bet]
						getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
						cursor.execute(getusername)
						userinfo = cursor.fetchone()
						username = userinfo[0]
						allbets += roombets[bet + 1]
						stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
						messagebank += F"{username} - {stavka} коинов\n"
			if odd != 'None':
				messagebank +='\n'
				messagebank += 'Ставки на нечётное:\n'
				roombets = ast.literal_eval(odd)
				roombetsvalue = len(roombets)
				for bet in range(roombetsvalue):
					if bet % 2 == 0:
						userid = roombets[bet]
						getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
						cursor.execute(getusername)
						userinfo = cursor.fetchone()
						username = userinfo[0]
						allbets += roombets[bet + 1]
						stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
						messagebank += F"{username} - {stavka} коинов\n"
			if first_gap != 'None':
				messagebank +='\n'
				messagebank += 'Ставки на 1-12:\n'
				roombets = ast.literal_eval(first_gap)
				roombetsvalue = len(roombets)
				for bet in range(roombetsvalue):
					if bet % 2 == 0:
						userid = roombets[bet]
						getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
						cursor.execute(getusername)
						userinfo = cursor.fetchone()
						username = userinfo[0]
						allbets += roombets[bet + 1]
						stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
						messagebank += F"{username} - {stavka} коинов\n"
			if second_gap != 'None':
				messagebank +='\n'
				messagebank += 'Ставки на 13-24:\n'
				roombets = ast.literal_eval(second_gap)
				roombetsvalue = len(roombets)
				for bet in range(roombetsvalue):
					if bet % 2 == 0:
						userid = roombets[bet]
						getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
						cursor.execute(getusername)
						userinfo = cursor.fetchone()
						username = userinfo[0]
						allbets += roombets[bet + 1]
						stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
						messagebank += F"{username} - {stavka} коинов\n"
			if third_gap != 'None':
				messagebank +='\n'
				messagebank += 'Ставки на 25-36:\n'
				roombets = ast.literal_eval(third_gap)
				roombetsvalue = len(roombets)
				for bet in range(roombetsvalue):
					if bet % 2 == 0:
						userid = roombets[bet]
						getusername = (F"SELECT username,balance FROM goldenusers WHERE userid = '{userid}'")
						cursor.execute(getusername)
						userinfo = cursor.fetchone()
						username = userinfo[0]
						allbets += roombets[bet + 1]
						stavka = "{:,}".format(roombets[bet + 1]).replace(',',' ')
						messagebank += F"{username} - {stavka} коинов\n"
			if numbers != 'None':
				messagebank +='\n'
				messagebank += 'Ставки на числа:\n'
				roombets = ast.literal_eval(numbers)
				roombetsvalue = len(roombets)
				for bet in range(roombetsvalue):
					if bet % 3 == 0:
						userid = roombets[bet]
						cursor.execute(F"SELECT username,balance,wins_all,wins_today FROM goldenusers WHERE userid = '{userid}'")
						userinfo = cursor.fetchone()
						username = userinfo[0]
						stavka = "{:,}".format(roombets[bet + 1]).replace(',',',')
						allbets += roombets[bet + 1]
						messagebank += F"{username} - {stavka} коинов на число {roombets[bet + 2]}\n"

			seconds = (timenow - roomrolltime).seconds
			timez = str(timedelta(seconds=60 - seconds))[3::]
			if play == 'No':
				messagebank = F"В этом раунде ещё никто не поставил.\n\nХэш игры:\n{room_hash}\n\nДо конца раунда: {timez}"
			else:
				allbets = "{:,}".format(int(allbets)).replace(',',' ')
				messagebank = F"Всего поставлено {allbets} коинов\n\n{messagebank}\n\nХэш игры:\n{room_hash}\n\nДо конца раунда: {timez}"
			messages_send(roomid,messagebank,menu.main())
	except Exception:
		traceback.print_exc()

def repost(userid):
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			userget = (F"SELECT repost,bonus_balance from goldenusers where userid = '{userid}'")
			cursor.execute(userget)
			userinfo = cursor.fetchone()
			repost = userinfo[0]
			bonus_balance = int(userinfo[1])
			if repost == '0':
				cursor.execute(F"UPDATE goldenusers SET bonus_balance = '{bonus_balance + 5000000}',repost = '1' WHERE userid = '{userid}'")
	except Exception:
		traceback.print_exc()

def get_top():
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			userget = (F"SELECT userid,username,wins_all from goldenusers ORDER BY wins_all DESC")
			cursor.execute(userget)
			users = cursor.fetchall()
			number = 0
			message = "ТОП 10 игроков\n\n"
			for i in users:
				userid = i[0]
				name = i[1]
				wins_all = int(i[2])
				number +=1
				wins_all = "{:,}".format(wins_all).replace(',',' ')
				message = message + F"{number}. *id{userid} ({name}) выиграл {wins_all} коинов.\n"
				if number == 10:
					break
		return message
	except Exception:
		traceback.print_exc()

def deposits():
	url = 'https://corona-coins.ru/api/'
	payload = {'token':'sV6m66q8x5QL8ESKAwV3DiKVybYumFkL','method':'history','type':'1','offset':'0'}
	headers = {'content-type': 'application/json'}
	r = requests.post(url, data=json.dumps(payload), headers=headers)
	conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
							password=settings.pgpassword, host=settings.pghost)
	with conn.cursor() as cursor:
		conn.autocommit = True
		cursor.execute(F"SELECT * FROM botinfo")
		a = cursor.fetchone()
		transactions = a[0]
		transactions = ast.literal_eval(transactions)
		getinfo = r.json()['response']
		getinfo = getinfo[:5]
		for i in getinfo:
			transaction_id = int(i['id'])
			if transaction_id in transactions:
				continue
			else:	
				userid = i['from_id']
				amount = i['amount']
				UserReg(userid,get_username(userid),'None')
				transactions = transactions[1:]
				transactions.append(transaction_id)
				addbalance(userid,amount)
				cursor.execute(F"UPDATE botinfo SET transactions = '{transactions}'")
def withdraw(roomid,userid):
	try:
		url = 'https://corona-coins.ru/api/'
		headers = {'content-type': 'application/json'}
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			userget = (F"SELECT * FROM goldenusers WHERE userid = '{userid}'")
			cursor.execute(userget)
			user = cursor.fetchall()[0]
			username = user[1]
			balance = int(user[2])
			if balance > 0:
				botbalance = get_withdraw()
				if balance <= botbalance:
					payload = {'token':'sV6m66q8x5QL8ESKAwV3DiKVybYumFkL','method':'transfer','to_id':F'{userid}','amount':f'{balance}'}
					r = requests.post(url, data=json.dumps(payload), headers=headers)	
					update = sql.SQL(F"UPDATE goldenusers SET balance = '0' WHERE userid = '{userid}'")
					cursor.execute(update)
					balance = "{:,}".format(balance).replace(',',',')
					messages_send(roomid,F'*id{userid} ({get_username(userid).split()[0]}), выведено {balance} коинов',menu.main())
				else:
					messages_send(roomid,F'*id{userid} ({get_username(userid).split()[0]}), на балансе бота недостаточно средств.',menu.main())
	except Exception:
		traceback.print_exc()

def admin_updatetop():
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"UPDATE goldenusers SET wins_today = '0',wins_all= '0'")
	except Exception:
		traceback.print_exc()
def admin_updaterepost():
	try:
		conn = psycopg2.connect(dbname=settings.pgdatabase, user=settings.pguser, 
								password=settings.pgpassword, host=settings.pghost)
		with conn.cursor() as cursor:
			conn.autocommit = True
			cursor.execute(F"UPDATE goldenusers SET repost = '0'")
	except Exception:
		traceback.print_exc()