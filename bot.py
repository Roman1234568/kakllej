import telebot
from config import *
from logic import *
import os

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для городов. /help - список команд")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """Команды:
/show_city город - показать город
/remember_city город - сохранить город
/show_my_cities - мои города"""
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[-1]
    
    coords = manager.get_coordinates(city_name)
    if not coords:
        bot.send_message(message.chat.id, "Город не найден")
        return
    
    # Создаем карту
    manager.create_graph('temp_city.png', [city_name])
    
    # Отправляем
    with open('temp_city.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f"Город: {city_name}")
    
    os.remove('temp_city.png')

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} сохранен!')
    else:
        bot.send_message(message.chat.id, 'Город не найден')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    
    if not cities:
        bot.send_message(message.chat.id, "Нет сохраненных городов")
        return
    
    # Создаем карту
    manager.create_graph('temp_all.png', cities)
    
    # Отправляем
    with open('temp_all.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f"Ваши города: {len(cities)} шт")
    
    os.remove('temp_all.png')

if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()