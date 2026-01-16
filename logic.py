import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, path, cities, marker_color='red'):
        """Создает карту с городами заданного цвета"""
        fig = plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        ax.stock_img()
        ax.coastlines()
        
        for city in cities:
            coords = self.get_coordinates(city)
            if coords:
                lat, lon = coords
                ax.plot(lon, lat, marker='o', color=marker_color, 
                       markersize=8, transform=ccrs.PlateCarree())
                ax.text(lon + 2, lat + 2, city, 
                       transform=ccrs.PlateCarree(), fontsize=8)
        
        plt.title('Города')
        plt.savefig(path, dpi=100)
        plt.close()

  
    def get_cities_by_country(self, country):
        """Получить города по стране"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT city FROM cities WHERE country = ?''', (country,))
            return [row[0] for row in cursor.fetchall()]

    def get_cities_by_population_density(self, min_density=None, max_density=None):
        """Получить города по плотности населения"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            query = '''SELECT city FROM cities WHERE population_density IS NOT NULL'''
            params = []
            
            if min_density is not None:
                query += ' AND population_density >= ?'
                params.append(min_density)
            if max_density is not None:
                query += ' AND population_density <= ?'
                params.append(max_density)
            
            cursor.execute(query, params)
            return [row[0] for row in cursor.fetchall()]

    def get_cities_by_country_and_density(self, country, min_density=None, max_density=None):
        """Получить города по стране и плотности"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            query = '''SELECT city FROM cities WHERE country = ? AND population_density IS NOT NULL'''
            params = [country]
            
            if min_density is not None:
                query += ' AND population_density >= ?'
                params.append(min_density)
            if max_density is not None:
                query += ' AND population_density <= ?'
                params.append(max_density)
            
            cursor.execute(query, params)
            return [row[0] for row in cursor.fetchall()]

    def draw_distance(self, city1, city2):
        pass