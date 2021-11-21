import requests
import sqlite3
import telebot
from telebot import types
from pyowm import OWM
from pyowm.utils.config import get_default_config
from bs4 import BeautifulSoup

state = 0
def get_state():
    return state

config_url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
response = requests.get(config_url).json()
token = '2112568715:AAGyNE0nLpiJfPuRrhm3g_0P6fhns-Rlfy0'
bot = telebot.TeleBot(token)

connection = sqlite3.connect('INFO2.db')
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    userChatId INT PRIMARY KEY,
    userName TEXT,
    userTown TEXT);
    """)
connection.commit()


@bot.message_handler(commands = ['start'])
def starting(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    itembtn1 = types.KeyboardButton('Хочу узнать погоду на сегодня)')
    itembtn2 = types.KeyboardButton('Где же я нахожусь ?')
    itembtn3 = types.KeyboardButton('Хочу узнать курс валют')
    itembtn4 = types.KeyboardButton('Хочу зарегистрироваться)')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    msg = bot.send_message(message.chat.id,'Здраствуй, я самый полезный бот в мире)Я могу для тебя найти погоду,последние новости и я даже знаю где ты сейчас (хаха).Давай начнем?'
                                           '/registration - зарегистрироваться в системе \n /weather - узнать погоду в своем городе \n /converter - узнать курс валют \n /news - узнать последние мировые новости \n /location - узнать свои координаты \n'
                                           '/afisha - афиша театра, топ-10 в кино ,топ-10 в музыке')

@bot.message_handler(commands = ['registration'])
def subcribe(message):
    msg = bot.send_message(message.chat.id, "Приятно познакомится))Введите ваш город:" )
    bot.register_next_step_handler(msg,send_description)
def send_description(message):
    try:
        person_town = message.text
        bot.send_message(message.chat.id, "Приятно познакомится ,"+ str(message.from_user.first_name))
        local_connection = sqlite3.connect('INFO2.db')
        local_cursor = local_connection.cursor()
        local_cursor.execute("INSERT OR IGNORE INTO users VALUES(? ,? , ?);",
                             (message.chat.id, message.from_user.first_name, person_town))
        local_connection.commit()
        bot.send_message(message.chat.id, "Приятно познакомится ," + str(message.from_user.first_name))

    except Exception:
        bot.send_message(message.chat.id, "Вы уже в базе данных...")



@bot.message_handler(commands=['delete'])
def delete(message):
    try:
        local_connection = sqlite3.connect('INFO2.db')
        local_cursor = local_connection.cursor()
        people_id = message.chat.id
        local_cursor.execute(f"DELETE FROM users WHERE userChatId = {people_id};")
        bot.send_message(message.chat.id, "Ваши данные были успешно удалены")
        local_connection.commit()
    except Exception:
        bot.send_message(message.chat.id, "К сожалению, ваших данных ещё нет а базе данных...")



@bot.message_handler(commands=['check'])
def check(message):
    local_connection = sqlite3.connect('INFO2.db')
    local_cursor = local_connection.cursor()
    local_cursor.execute("SELECT * from users;")
    all_results = local_cursor.fetchall()
    if all_results is not None:
        bot.send_message(message.chat.id, str(all_results))
    else:
        bot.send_message(message.chat.id,"Oooops...к сожелению таблица пока пуста(")


@bot.message_handler(commands=['weather'])
def city(message):
    if message.text == "/weather":
        bot.send_message(message.chat.id, 'Введите город:')
        bot.register_next_step_handler(message,get_weather)
    else:
        bot.send_message(message.chat.id, 'smth went wrong')


def get_weather(message):
    try:
        place = message.text

        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        owm = OWM('c52242b2d4d80ae028d6e97b46ce1c39', config_dict)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(place)
        w = observation.weather
        t = w.temperature("celsius")
        t1 = t['temp']
        t2 = t['feels_like']
        t3 = t['temp_max']
        t4 = t['temp_min']
        wi = w.wind()['speed']
        humi = w.humidity
        cl = w.clouds
        st = w.status
        dt = w.detailed_status
        ti = w.reference_time('iso')
        pr = w.pressure['press']
        vd = w.visibility_distance
        bot.send_message(message.chat.id, "В городе " + str(place) + " температура " + str(t1) + " °C" + "\n" +
				"Максимальная температура " + str(t3) + " °C" +"\n" +
				"Минимальная температура " + str(t4) + " °C" + "\n" +
				"Ощущается как" + str(t2) + " °C" + "\n" +
				"Скорость ветра " + str(wi) + " м/с" + "\n" +
				"Давление " + str(pr) + " мм.рт.ст" + "\n" +
				"Влажность " + str(humi) + " %" + "\n" +
				"Видимость " + str(vd) + "  метров" + "\n" +
				"Описание " + str(st) + str(dt))
    except:
        bot.send_message(message.chat.id,"Такой город не найден!")
        print(str(message.text),"- не найден")


@bot.message_handler(commands=['location'])
def visualise(message):
    # Клавиатура с кнопкой запроса локации
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    msg = bot.send_message(message.chat.id, "Поделись местоположением", reply_markup=keyboard)
    bot.register_next_step_handler(msg, location)
def location (message):
    if message.location is not None:
        bot.send_message(message.chat.id,f"Твои координаты:{message.location}")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так,попробуй снова", message.location)


@bot.message_handler(commands=['converter'])
def send_description(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard= True , row_width=2)

    itembtn1 = types.KeyboardButton('USD')
    itembtn2 = types.KeyboardButton('EUR')
    itembtn3 = types.KeyboardButton('RUR')
    itembtn4 = types.KeyboardButton('BTS')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    msg = bot.send_message(message.chat.id, 'Узнать курс от ЦБ' , reply_markup=markup)
    bot.register_next_step_handler(msg, process_coin_step)

def process_coin_step(message):
    try:
        markup = types.ReplyKeyboardRemove(selective=False)

        for coin in response:
            if (message.text == coin['ccy']):
                bot.send_message(message.chat.id , printCoin(coin['buy'], coin['sale']),  reply_markup= markup , parse_mode= "Markdown" )
    except Exception as e :
        bot.reply_to(message , 'oooops!')

def printCoin(buy, sale):
    '''Вывод курса'''
    return 'Курс покупки ' + str(buy) + '\n "Курс продажи"' + str(sale)


@bot.message_handler(commands=['afisha'])
def initialisation(message):
    bot.send_message(message.chat.id, 'Введите,какой темой вы интересуетесь:новости,кино,музыка')
    global state  # определение переменной как глобальной
    state = 1

# елси пользователь что-то ввел то выполняется эта функция
@bot.message_handler(func=lambda message: message.text == 'кино')
def cinema(message):
    bot.send_message(message.chat.id, "Топ-10 лучших фильмов по версии КиноАфиша")
    URL = 'https://www.kinoafisha.info/rating/movies/'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    texts = soup.findAll('a', 'movieItem_ref')
    for i in range(0 ,len(texts[:-90])):
        txt = str(i + 1) + ')' + texts[i].text
        bot.send_message(message.chat.id, '<a href="{}">{}</a>'.format(texts[i]['href'], txt), parse_mode='html')



@bot.message_handler(func=lambda message: message.text == 'новости')
def music(message):  #search for url and thing to parse
    URL = 'https://ria.ru/world/'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    texts = soup.findAll('a', 'list-item__title')
    for i in range(0 ,len(texts[:-10])):
        txt = str(i + 1) + ')' + texts[i].text
        bot.send_message(message.chat.id, '<a href="{}">{}</a>'.format(texts[i]['href'], txt), parse_mode='html')
    global state
    state = 2



@bot.message_handler(func=lambda message: message.text == 'музыка')
def music(message):
    bot.send_message(message.chat.id,"Топ-10 популярных песен по версии Яндекс-Музыка")
    URL = 'https://music.yandex.ru/users/olegnovikov92/playlists/1001/'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    texts = soup.findAll('a','d-track__title')

    for i in range(0 , len(texts[:-20])):
        txt = str(i + 1) + ') ' + texts[i].text
        bot.send_message(message.chat.id,'<a href="{}">{}</a>'.format(texts[i]['href'], txt), parse_mode='html')
    global state
    state = 2


@bot.message_handler(func=lambda message: get_state() == 2)
def question(message):
    bot.send_message(message.chat.id,'Если хотите остановить программу введите "стоп" , '
                                     'если хотите узнать еще кое-что введите /afisha)')
@bot.message_handler(func=lambda message: message.text == 'стоп')
def stop(message):
    bot.send_message(message.chat.id, 'Для продолжение общения введите /start')


bot.polling(none_stop=True, interval=0)