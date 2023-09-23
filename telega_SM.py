import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import CallbackQuery
import openpyxl
from datetime import datetime

token = "5734991862:AAGVxppmtLjCTIMg6bN6TolKjgGl3wgdgSQ"
    
my_bot = telebot.TeleBot(token)

class indications():
    def __init__(self, addr, appart, hot, cold, elct):
        self.addr = addr
        self.appart = appart
        self.hot = hot
        self.cold = cold
        self.elct = elct

current_indi = indications(addr="", appart="", hot="", cold="", elct="")

# TELEBOT HANDLERS 
# start button
@my_bot.message_handler(commands=['start'])
def welcome_message(message):
   markup = address_keyboard(message, first_run=True)
   my_bot.send_message(message.chat.id, text='Ващ айди ' + str(message.from_user.id))
   my_bot.send_message(message.chat.id, text='Выберете адрес:', reply_markup=markup)

# text handler
@my_bot.message_handler(content_types=['text'])
def addr_input(message):
   pass 
   
# Обработчик нажатий всех инлайн-кнопок
@my_bot.callback_query_handler(func=lambda call: True)
# навигация по меню
def menu_navigate(callback_obj: CallbackQuery):
    if callback_obj.data[2:] == "Назад": #нажата кнопка назад
        current_level = "0" #str(int(callback_obj.data[0])-2)
    elif callback_obj.data[2:] == "Выход": #нажата кнопка выход
        stop_bot(message=callback_obj.message)
    elif len(callback_obj.data) > 4: #кнопки адреса домов
        current_level = callback_obj.data[0]
        current_indi.addr = callback_obj.data[2:]
    else: 
        current_level = callback_obj.data[0] #нажата кнопка да
    levels = {
        "0": address_keyboard,
        "1": appart_input,
        "2": hot_keyboard,
        "3": cold_keyboard,
        "4": elct_keyboard,
        "5": confirm_keyboard,
        "6": make_rec
        }
    current_level_function = levels[current_level]
    current_level_function(callback_obj.message, first_run=False)
      
# stop button
def make_rec(message, **kwargs):
    path = 'D:\coding\Python\\'
    my_bot.send_message(message.chat.id, 'Пока!')
    wb = openpyxl.load_workbook(filename=path+'sample.xlsx')
    ws = wb[current_indi.addr]
    time = str(datetime.now().strftime('%d.%m.%Y в %H:%M:%S'))
    ws.append([f'{current_indi.addr}, кв. {current_indi.appart}', f'{current_indi.hot}', f'{current_indi.cold}', f'{current_indi.elct}', time])
    wb.save(path+'sample.xlsx')

@my_bot.message_handler(commands=['stop'])
def stop_bot(message, **kwargs):
    my_bot.stop_polling()
    
# other functions
# клавиатура выбора адреса 
def address_keyboard(message, first_run):
    current_level = 0
    list_of_address = [
        ('Еременко 38-1'),
        ('Зорге 70-1'),
        ('Содружества 88'),
        ('Коммунистический 14'),
        ('Стачки 204'),
        ('2-я Краснодарская 159'),
        ('Коммунистический 2-2'),
        ('3-я Кольцевая 58')
    ]
    if first_run: 
       return gen_markup(list_of_address, 2, current_level+1)
    else: my_bot.edit_message_text(chat_id=message.chat.id, message_id= message.id, text='Выберете адрес:', reply_markup = gen_markup(list_of_address, 2, current_level+1))

# клавиатура подтверждения правильности адреса
def confirm_addr(message, current_level, **kwargs):
    list_of_check = [('Да'), ('Назад'), ('Выход')]
    text = f'Верный адрес: {current_indi.addr}, кв. {current_indi.appart}?'
    my_bot.send_message(chat_id=message.chat.id, text=text, reply_markup = gen_markup(list_of_check, 3, current_level+1))

# запрос на ввод номера квартиры
def appart_input(message, **kwargs):
    old_message = my_bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text='Введите номер квартиры:')
    current_level = 1
    my_bot.register_next_step_handler(message, user_text_input, current_level, old_message)

# запрос на ввод показаний ГВ
def hot_keyboard(message, **kwargs):
    current_level = 2
    old_message = my_bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text='Введите показания cчетчика горячей воды:')
    my_bot.register_next_step_handler(message, user_text_input, current_level, old_message)

# запрос на ввод показаний ХВ
def cold_keyboard(message, **kwargs):
    current_level = 3
    old_message = my_bot.send_message(chat_id=message.chat.id, text='Введите показания cчетчика холодной воды:')
    my_bot.register_next_step_handler(message, user_text_input, current_level, old_message)

# запрос на ввод показаний электро
def elct_keyboard(message, **kwargs):
    current_level = 4
    old_message = my_bot.send_message(chat_id=message.chat.id, text='Введите показания электро-счетчика:')
    my_bot.register_next_step_handler(message, user_text_input, current_level, old_message)
   
# клавиатура передачи показаний
def confirm_keyboard(message, **kwargs):
    current_level = 5
    list_of_check = [('Да'), ('Назад'), ('Выход')]
    text = f"""Передать показания для адреса {current_indi.addr}, кв. {current_indi.appart}: горячая вода - {current_indi.hot} куб., холодная вода - {current_indi.cold} куб., электричество - {current_indi.elct} кВт?"""
    my_bot.send_message(chat_id=message.chat.id, text=text, reply_markup = gen_markup(list_of_check, 1, current_level+1))    

# обработчик пользовательского ввода
def user_text_input(message, current_level, old_message):
    my_bot.delete_message(chat_id = old_message.chat.id, message_id=old_message.id)
    if current_level == 1:
        current_indi.appart = message.text
        confirm_addr(message, current_level)
    elif current_level == 2:
        current_indi.hot = message.text
        cold_keyboard(message)
    elif current_level == 3:
        current_indi.cold = message.text
        elct_keyboard(message)
    elif current_level == 4:
        current_indi.elct = message.text
        confirm_keyboard(message)
# генерация клавиатур
def gen_markup(list_of_buttons, rowz, level):
    inline_key = InlineKeyboardMarkup(row_width=rowz)
    inline_key.add(*[InlineKeyboardButton(text=name, callback_data=f"{level}_{name}") for name in list_of_buttons])
    return inline_key

def main():
    my_bot.infinity_polling()

if __name__ == "__main__":
    main()

