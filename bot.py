import telebot
from config import *
from logic import *
import os

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 
                    "Привет! Я бот для городов. /help - список команд\n"
                    "Доступные цвета: red, blue, green, yellow, purple, orange, black")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """Команды:
/show_city город [цвет] - показать город (цвет по умолчанию: red)
/remember_city город - сохранить город
/show_my_cities [цвет] - мои города
/country страна [цвет] - города страны (например: Russia)
/density мин_плотность [цвет] - города с плотностью от (например: 1000)
/country_density страна мин_плотность [цвет] - города страны с плотностью
Цвета: red, blue, green, yellow, purple, orange, black"""
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажите город: /show_city Moscow")
        return
    
    city_name = parts[1]
    marker_color = parts[2] if len(parts) > 2 else 'red'
    
    coords = manager.get_coordinates(city_name)
    if not coords:
        bot.send_message(message.chat.id, "Город не найден")
        return
    
    manager.create_graph('temp.png', [city_name], marker_color)
    
    with open('temp.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, 
                      caption=f"Город: {city_name} (цвет: {marker_color})")
    
    os.remove('temp.png')

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажите город: /remember_city London")
        return
    
    city_name = parts[1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} сохранен!')
    else:
        bot.send_message(message.chat.id, 'Город не найден')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    parts = message.text.split()
    marker_color = parts[1] if len(parts) > 1 else 'blue'
    
    cities = manager.select_cities(message.chat.id)
    
    if not cities:
        bot.send_message(message.chat.id, "Нет сохраненных городов")
        return
    
    manager.create_graph('temp.png', cities, marker_color)
    
    with open('temp.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, 
                      caption=f"Ваши города: {len(cities)} шт (цвет: {marker_color})")
    
    os.remove('temp.png')

@bot.message_handler(commands=['country'])
def handle_country(message):
    """Вывод городов по стране"""
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажите страну: /country Russia")
        return
    
    country = parts[1]
    marker_color = parts[2] if len(parts) > 2 else 'green'
    
    cities = manager.get_cities_by_country(country)
    
    if not cities:
        bot.send_message(message.chat.id, f"Города страны '{country}' не найдены")
        return
    
    manager.create_graph('temp.png', cities[:50], marker_color)  # ограничиваем 50 городами
    
    with open('temp.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, 
                      caption=f"Города {country}: {len(cities)} шт (цвет: {marker_color})")
    
    os.remove('temp.png')

@bot.message_handler(commands=['density'])
def handle_density(message):
    """Вывод городов по плотности населения"""
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажите мин. плотность: /density 1000")
        return
    
    try:
        min_density = float(parts[1])
        marker_color = parts[2] if len(parts) > 2 else 'purple'
        
        cities = manager.get_cities_by_population_density(min_density=min_density)
        
        if not cities:
            bot.send_message(message.chat.id, f"Города с плотностью от {min_density} не найдены")
            return
        
        manager.create_graph('temp.png', cities[:50], marker_color)
        
        with open('temp.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, 
                          caption=f"Города с плотностью от {min_density}: {len(cities)} шт")
        
        os.remove('temp.png')
    except ValueError:
        bot.send_message(message.chat.id, "Плотность должна быть числом")

@bot.message_handler(commands=['country_density'])
def handle_country_density(message):
    """Вывод городов по стране и плотности"""
    parts = message.text.split()
    if len(parts) < 3:
        bot.send_message(message.chat.id, "Укажите страну и плотность: /country_density Russia 1000")
        return
    
    country = parts[1]
    try:
        min_density = float(parts[2])
        marker_color = parts[3] if len(parts) > 3 else 'orange'
        
        cities = manager.get_cities_by_country_and_density(country, min_density=min_density)
        
        if not cities:
            bot.send_message(message.chat.id, f"В {country} города с плотностью от {min_density} не найдены")
            return
        
        manager.create_graph('temp.png', cities[:50], marker_color)
        
        with open('temp.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, 
                          caption=f"Города {country} с плотностью от {min_density}: {len(cities)} шт")
        
        os.remove('temp.png')
    except ValueError:
        bot.send_message(message.chat.id, "Плотность должна быть числом")

if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()