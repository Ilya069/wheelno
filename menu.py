from vk_api.keyboard import VkKeyboard, VkKeyboardColor
def main():
	keyboard = VkKeyboard(one_time=False)
	keyboard.add_button('Банк', color=VkKeyboardColor.POSITIVE)
	keyboard.add_button('Баланс', color=VkKeyboardColor.POSITIVE)
	keyboard.add_line() 
	keyboard.add_button('Красное', color=VkKeyboardColor.PRIMARY)
	keyboard.add_button('Чёрное', color=VkKeyboardColor.PRIMARY)
	keyboard.add_line() 
	keyboard.add_button('1-12', color=VkKeyboardColor.PRIMARY)
	keyboard.add_button('13-24', color=VkKeyboardColor.PRIMARY)
	keyboard.add_button('25-36', color=VkKeyboardColor.PRIMARY)
	keyboard.add_line()
	keyboard.add_button('Чётное', color=VkKeyboardColor.NEGATIVE)
	keyboard.add_button('На число', color=VkKeyboardColor.NEGATIVE)
	keyboard.add_button('Нечётное', color=VkKeyboardColor.NEGATIVE)
	keyboard.add_line() 
	keyboard.add_openlink_button('Пополнить',link='http://vk.com/app7349811#merchant505458404_1000000')
	keyboard.add_button('Вывод', color=VkKeyboardColor.DEFAULT)
	return keyboard.get_keyboard()

def groupmenu():
	keyboard = VkKeyboard(one_time=False)
	keyboard.add_button('Найти беседу', color=VkKeyboardColor.POSITIVE)
	keyboard.add_line()
	keyboard.add_button('Топ игроков', color=VkKeyboardColor.PRIMARY)
	return keyboard.get_keyboard()

def adminpanel():
	keyboard = VkKeyboard(one_time=False)
	keyboard.add_button('Обновить топ', color=VkKeyboardColor.NEGATIVE)
	keyboard.add_button('Обновить репосты', color=VkKeyboardColor.NEGATIVE)
	keyboard.add_line()
	keyboard.add_button('Выдать баланс',color=VkKeyboardColor.POSITIVE)
	return keyboard.get_keyboard()