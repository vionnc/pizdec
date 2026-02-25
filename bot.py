import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import random
import os
import asyncio
import time
from discord import FFmpegPCMAudio
import glob

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = 'aura_data.json'
INVENTORY_FILE = 'inventory_data.json'
BUSINESS_FILE = 'business_data.json'
OILBASE_FILE = 'oilbase_data.json'
WEAPONS_FILE = 'weapons_data.json'
MINE_FILE = 'mine_data.json'
MUSIC_FOLDER = 'aura_phonk'

role_bonuses = {
    'Фонкер': {
        'multiplier': 1.1,
        'daily_limit': 1500,
        'color': 0x00ff00
    },
    'Легенда Аура Череп': {
        'multiplier': 1.2,
        'daily_limit': 2000,
        'color': 0xffd700
    },
    'Троллфейс': {
        'multiplier': 2.0,
        'daily_limit': 15000,
        'color': 0xff4500
    }
}

businesses = {
    'kiosk': {
        'name': 'Блядушник',
        'price': 5000,
        'income': 100,
        'cooldown': 3600,
        'emoji': '🏪'
    },
    'bank': {
        'name': 'Банк',
        'price': 50000,
        'income': 1500,
        'cooldown': 7200,
        'emoji': '🏦'
    },
    'factory': {
        'name': 'Завод',
        'price': 200000,
        'income': 10000,
        'cooldown': 21600,
        'emoji': '🏭'
    }
}

weapons_shop = {
    'pm': {
        'name': 'ПМ',
        'price': 9000,
        'damage': 10,
        'rob_bonus': 5,
        'description': 'Надёжный пистолет'
    },
    'm4a1': {
        'name': 'М4А1',
        'price': 12000,
        'damage': 30,
        'rob_bonus': 15,
        'description': 'Автомат для серьёзных дел'
    },
    'ak47': {
        'name': 'АК-47',
        'price': 20000,
        'damage': 50,
        'rob_bonus': 25,
        'description': 'Калаш, легенда'
    },
    'sniper': {
        'name': 'Снайперка',
        'price': 30000,
        'damage': 70,
        'rob_bonus': 35,
        'description': 'Для точных попаданий'
    },
    'grenade': {
        'name': 'Гранатомёт',
        'price': 50000,
        'damage': 90,
        'rob_bonus': 50,
        'description': 'Тяжёлая артиллерия'
    }
}

robbery_targets = {
    'shop': {
        'name': 'Магазин',
        'min_reward': 2000,
        'max_reward': 5000,
        'base_chance': 80,
        'cooldown': 3600,
        'emoji': '🏪'
    },
    'bank': {
        'name': 'Банк',
        'min_reward': 10000,
        'max_reward': 20000,
        'base_chance': 50,
        'cooldown': 10800,
        'emoji': '🏦'
    },
    'jewelry': {
        'name': 'Ювелирка',
        'min_reward': 30000,
        'max_reward': 50000,
        'base_chance': 35,
        'cooldown': 21600,
        'emoji': '💎'
    },
    'oilbase': {
        'name': 'Нефтебаза',
        'min_reward': 100000,
        'max_reward': 200000,
        'base_chance': 20,
        'cooldown': 43200,
        'emoji': '🛢️'
    },
    'worldbank': {
        'name': 'Мировой банк',
        'min_reward': 500000,
        'max_reward': 1000000,
        'base_chance': 5,
        'cooldown': 86400,
        'emoji': '🌍'
    }
}

oilbase_upgrades = {
    1: {'name': 'Начальная', 'security_bonus': 0, 'price': 500000, 'max_oil': 1000},
    2: {'name': 'Развитая', 'security_bonus': 5, 'price': 200000, 'max_oil': 5000},
    3: {'name': 'Промышленная', 'security_bonus': 10, 'price': 500000, 'max_oil': 20000},
    4: {'name': 'Гигант', 'security_bonus': 15, 'price': 1000000, 'max_oil': 100000},
    5: {'name': 'Империя', 'security_bonus': 20, 'price': 2000000, 'max_oil': 500000}
}

security_levels = {
    1: {'name': 'Нанятые бомжи', 'chance': 10, 'price': 0, 'emoji': '🧟'},
    2: {'name': 'Охранники с дубинками', 'chance': 25, 'price': 20000, 'emoji': '👮'},
    3: {'name': 'ЧОП с пистолетами', 'chance': 40, 'price': 50000, 'emoji': '🔫'},
    4: {'name': 'Спецназ Скебоба', 'chance': 60, 'price': 100000, 'emoji': '🛡️'},
    5: {'name': 'Частная армия', 'chance': 75, 'price': 200000, 'emoji': '💂'},
    6: {'name': 'Роботы-терминаторы фурри-ебы', 'chance': 85, 'price': 500000, 'emoji': '🤖'},
    7: {'name': 'Система ПРО', 'chance': 92, 'price': 1000000, 'emoji': '🛸'},
    8: {'name': 'Невидимость', 'chance': 97, 'price': 2000000, 'emoji': '👻'},
    9: {'name': 'Сдвиг реальности', 'chance': 99, 'price': 5000000, 'emoji': '🌀'},
    10: {'name': 'Аллах', 'chance': 100, 'price': 10000000, 'emoji': '😇'}
}

mine_resources = {
    'coal': {'name': 'Уголь', 'price': 100, 'chance': 50, 'emoji': '🪨'},
    'iron': {'name': 'Железо', 'price': 300, 'chance': 30, 'emoji': '⚙️'},
    'gold': {'name': 'Золото', 'price': 1000, 'chance': 15, 'emoji': '🪙'},
    'diamond': {'name': 'Алмазы', 'price': 5000, 'chance': 5, 'emoji': '💎'}
}

pickaxe_levels = {
    1: {'name': 'Деревянная кирка', 'power': 1, 'price': 1000, 'emoji': '🪓'},
    2: {'name': 'Каменная кирка', 'power': 2, 'price': 2000, 'emoji': '⛏️'},
    3: {'name': 'Железная кирка', 'power': 3, 'price': 5000, 'emoji': '⚒️'},
    4: {'name': 'Золотая кирка(хуета)', 'power': 4, 'price': 10000, 'emoji': '🔨'},
    5: {'name': 'Алмазная кирка', 'power': 5, 'price': 20000, 'emoji': '💎'},
    6: {'name': 'Мифриловая кирка(Made by Denis Mothers', 'power': 7, 'price': 50000, 'emoji': '🔮'},
    7: {'name': 'Драконья кирка(Made By FurryEbs)', 'power': 10, 'price': 100000, 'emoji': '🐉'}
}

last_click = {}
tax_counter = {}

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_businesses():
    try:
        with open(BUSINESS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_businesses(data):
    with open(BUSINESS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_oilbases():
    try:
        with open(OILBASE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_oilbases(data):
    with open(OILBASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_weapons():
    try:
        with open(WEAPONS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_weapons(data):
    with open(WEAPONS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_mine():
    try:
        with open(MINE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_mine(data):
    with open(MINE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_bonus(member):
    for role_name, bonus in role_bonuses.items():
        if discord.utils.get(member.roles, name=role_name):
            return bonus
    return {'multiplier': 1.0, 'daily_limit': 1000}

def needs_tax_check(user_id):
    if user_id not in tax_counter:
        tax_counter[user_id] = 0
    tax_counter[user_id] += 1
    if tax_counter[user_id] >= 75:
        tax_counter[user_id] = 0
        return True
    return False

# ========== КНОПКА ФАРМА ==========
class AuraFarmButton(Button):
    def __init__(self):
        super().__init__(label="AURA FARM", style=discord.ButtonStyle.green)
    
    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()
        
        if user_id in last_click:
            if current_time - last_click[user_id] < 1:
                await interaction.response.send_message("Не так быстро! Подожди секунду", ephemeral=True, delete_after=2)
                return
        
        last_click[user_id] = current_time
        
        if needs_tax_check(user_id):
            await interaction.response.send_message("Налоговая проверка! Напиши !налоговая в чат", ephemeral=True)
            return
        
        data = load_data()
        user_id_str = str(user_id)
        
        if user_id_str not in data:
            data[user_id_str] = {
                'name': interaction.user.name,
                'aura': 0,
                'total_farms': 0,
                'daily_farms': 0,
                'last_reset': current_time
            }
        
        if current_time - data[user_id_str].get('last_reset', 0) > 86400:
            data[user_id_str]['daily_farms'] = 0
            data[user_id_str]['last_reset'] = current_time
        
        bonus = get_user_bonus(interaction.user)
        if data[user_id_str]['daily_farms'] >= bonus['daily_limit']:
            await interaction.response.send_message("Дневной лимит исчерпан! Завтра продолжишь", ephemeral=True, delete_after=3)
            return
        
        base_amount = random.randint(3, 15)
        farm_amount = int(base_amount * bonus['multiplier'])
        
        data[user_id_str]['aura'] += farm_amount
        data[user_id_str]['total_farms'] += 1
        data[user_id_str]['daily_farms'] += 1
        save_data(data)
        
        await interaction.response.send_message(
            f"Ты нафармил {farm_amount} Aura!\nБаланс: {data[user_id_str]['aura']} Aura\nДневной лимит: {data[user_id_str]['daily_farms']}/{bonus['daily_limit']}",
            ephemeral=False, delete_after=5
        )

# ========== МЕНЮ (ВСЕ КЛАССЫ VIEW) ==========
class MainMenuView(View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="💰 Фарм", style=discord.ButtonStyle.green, custom_id="farm")
    async def farm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Нажми кнопку AURA FARM ниже", ephemeral=True)
        await interaction.followup.send(view=FarmPanelView())
    
    @discord.ui.button(label="🏢 Бизнесы", style=discord.ButtonStyle.blurple, custom_id="business")
    async def business_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="БИЗНЕСЫ", color=discord.Color.gold())
        for biz_id, biz in businesses.items():
            embed.add_field(name=f"{biz['emoji']} {biz['name']}", value=f"Цена: {biz['price']} Aura\nДоход: {biz['income']} Aura/час", inline=False)
        await interaction.response.send_message(embed=embed, view=BusinessView(), ephemeral=True)
    
    @discord.ui.button(label="🔫 Оружие", style=discord.ButtonStyle.red, custom_id="weapons")
    async def weapons_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔫 ОРУЖИЕ И ОГРАБЛЕНИЯ", view=WeaponsView(), ephemeral=True)
    
    @discord.ui.button(label="🛢️ Нефтебаза", style=discord.ButtonStyle.blurple, custom_id="oil")
    async def oil_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        oil_data = load_oilbases()
        if user_id in oil_data:
            await interaction.response.send_message("🛢️ УПРАВЛЕНИЕ НЕФТЕБАЗОЙ", view=OilBaseView(), ephemeral=True)
        else:
            await interaction.response.send_message("У тебя нет нефтебазы! Купи за 500к", view=BuyOilView(), ephemeral=True)
    
    @discord.ui.button(label="⛏️ Шахта", style=discord.ButtonStyle.gray, custom_id="mine")
    async def mine_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⛏️ ШАХТА", view=MineView(), ephemeral=True)
    
    @discord.ui.button(label="🛒 Магазин", style=discord.ButtonStyle.secondary, custom_id="shop")
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="МАГАЗИН РОЛЕЙ", color=discord.Color.gold())
        for item_id, item in shop_items.items():
            embed.add_field(name=item['name'], value=f"Цена: {item['price']} Aura\n{item['description']}", inline=False)
        await interaction.response.send_message(embed=embed, view=ShopView(), ephemeral=True)
    
    @discord.ui.button(label="🎵 Музыка", style=discord.ButtonStyle.success, custom_id="music")
    async def music_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🎵 МУЗЫКА", view=MusicView(), ephemeral=True)
    
    @discord.ui.button(label="🏆 Топы", style=discord.ButtonStyle.blurple, custom_id="top")
    async def top_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🏆 ВЫБЕРИ ТОП", view=TopView(), ephemeral=True)

class FarmPanelView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(AuraFarmButton())
    
    @discord.ui.button(label="◀️ Назад", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏠 ГЛАВНОЕ МЕНЮ", description="Выбери раздел:", color=discord.Color.blue())
        embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
        embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
        embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
        embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
        embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
        embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
        embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
        embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
        await interaction.response.edit_message(embed=embed, view=MainMenuView())

class BusinessView(View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="📋 Список", style=discord.ButtonStyle.blurple, custom_id="list_biz")
    async def list_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="БИЗНЕСЫ", color=discord.Color.gold())
        for biz_id, biz in businesses.items():
            embed.add_field(name=f"{biz['emoji']} {biz['name']}", value=f"Цена: {biz['price']} Aura\nДоход: {biz['income']} Aura/час\nID: {biz_id}", inline=False)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏪 Купить", style=discord.ButtonStyle.green, custom_id="buy_biz")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Напиши !купить_бизнес [id]", ephemeral=True)
    
    @discord.ui.button(label="💰 Собрать", style=discord.ButtonStyle.green, custom_id="collect")
    async def collect_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await собрать_доход(ctx)
    
    @discord.ui.button(label="◀️ Назад", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏠 ГЛАВНОЕ МЕНЮ", description="Выбери раздел:", color=discord.Color.blue())
        embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
        embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
        embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
        embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
        embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
        embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
        embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
        embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
        await interaction.response.edit_message(embed=embed, view=MainMenuView())

class WeaponsView(View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="🔫 Магазин", style=discord.ButtonStyle.red, custom_id="weapon_shop")
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="ОРУЖИЕ", color=discord.Color.red())
        for weapon_id, weapon in weapons_shop.items():
            embed.add_field(name=weapon['name'], value=f"Цена: {weapon['price']} Aura\nБонус: +{weapon['rob_bonus']}%\nID: {weapon_id}", inline=False)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="⚔️ Моё оружие", style=discord.ButtonStyle.blurple, custom_id="my_weapons")
    async def my_weapons_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await моё_оружие(ctx)
    
    @discord.ui.button(label="🎯 Цели", style=discord.ButtonStyle.orange, custom_id="targets")
    async def targets_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await цели(ctx)
    
    @discord.ui.button(label="💰 Ограбить", style=discord.ButtonStyle.green, custom_id="rob")
    async def rob_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Напиши !ограбить [id цели]", ephemeral=True)
    
    @discord.ui.button(label="◀️ Назад", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏠 ГЛАВНОЕ МЕНЮ", description="Выбери раздел:", color=discord.Color.blue())
        embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
        embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
        embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
        embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
        embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
        embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
        embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
        embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
        await interaction.response.edit_message(embed=embed, view=MainMenuView())

class MineView(View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="⛏️ Работать", style=discord.ButtonStyle.green, custom_id="mine_work")
    async def work_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await шахта(ctx)
    
    @discord.ui.button(label="🪓 Купить кирку", style=discord.ButtonStyle.blurple, custom_id="buy_pickaxe")
    async def buy_pickaxe_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await купить_кирку(ctx)
    
    @discord.ui.button(label="📦 Ресурсы", style=discord.ButtonStyle.blurple, custom_id="resources")
    async def resources_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await мои_ресурсы(ctx)
    
    @discord.ui.button(label="💰 Продать", style=discord.ButtonStyle.gold, custom_id="sell")
    async def sell_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Напиши !продать_ресурсы или !продать_ресурсы уголь 10", ephemeral=True)
    
    @discord.ui.button(label="◀️ Назад", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏠 ГЛАВНОЕ МЕНЮ", description="Выбери раздел:", color=discord.Color.blue())
        embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
        embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
        embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
        embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
        embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
        embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
        embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
        embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
        await interaction.response.edit_message(embed=embed, view=MainMenuView())

class OilBaseView(View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="📊 Статистика", style=discord.ButtonStyle.blurple, custom_id="oil_stats")
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await моя_нефтебаза(ctx)
    
    @discord.ui.button(label="🛡️ Охрана", style=discord.ButtonStyle.red, custom_id="oil_security")
    async def security_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Напиши !улучшить_охрану", ephemeral=True)
    
    @discord.ui.button(label="📈 Прокачка", style=discord.ButtonStyle.green, custom_id="oil_upgrade")
    async def upgrade_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Напиши !прокачать_базу", ephemeral=True)
    
    @discord.ui.button(label="🛢️ Купить нефть", style=discord.ButtonStyle.blurple, custom_id="buy_oil")
    async def buy_oil_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Напиши !купить_нефть [количество]", ephemeral=True)
    
    @discord.ui.button(label="💰 Продать", style=discord.ButtonStyle.gold, custom_id="sell_oil")
    async def sell_oil_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Напиши !продать_нефть", ephemeral=True)
    
    @discord.ui.button(label="◀️ Назад", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏠 ГЛАВНОЕ МЕНЮ", description="Выбери раздел:", color=discord.Color.blue())
        embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
        embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
        embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
        embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
        embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
        embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
        embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
        embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
        await interaction.response.edit_message(embed=embed, view=MainMenuView())

class BuyOilView(View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="🛢️ Купить нефтебазу", style=discord.ButtonStyle.green, custom_id="buy_oilbase")
    async def buy_oilbase_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await купить_нефтебазу(ctx)
    
    @discord.ui.button(label="◀️ Назад", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏠 ГЛАВНОЕ МЕНЮ", description="Выбери раздел:", color=discord.Color.blue())
        embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
        embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
        embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
        embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
        embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
        embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
        embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
        embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
        await interaction.response.edit_message(embed=embed, view=MainMenuView())

class ShopView(View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="📋 Список", style=discord.ButtonStyle.blurple, custom_id="shop_list")
    async def list_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="МАГАЗИН РОЛЕЙ", color=discord.Color.gold())
        for item_id, item in shop_items.items():
            embed.add_field(name=item['name'], value=f"Цена: {item['price']} Aura\n{item['description']}\nID: {item_id}", inline=False)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🛒 Купить", style=discord.ButtonStyle.green, custom_id="shop_buy")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Напиши !купить_роль [id]", ephemeral=True)
    
    @discord.ui.button(label="◀️ Назад", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏠 ГЛАВНОЕ МЕНЮ", description="Выбери раздел:", color=discord.Color.blue())
        embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
        embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
        embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
        embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
        embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
        embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
        embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
        embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
        await interaction.response.edit_message(embed=embed, view=MainMenuView())

class MusicView(View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="📋 Плейлист", style=discord.ButtonStyle.blurple, custom_id="playlist")
    async def playlist_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await плейлист(ctx)
    
    @discord.ui.button(label="🎵 Случайный", style=discord.ButtonStyle.green, custom_id="random_track")
    async def random_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await фонк(ctx)
    
    @discord.ui.button(label="⏸️ Пауза", style=discord.ButtonStyle.gray, custom_id="pause")
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await пауза(ctx)
    
    @discord.ui.button(label="▶️ Продолжить", style=discord.ButtonStyle.green, custom_id="resume")
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await продолжить(ctx)
    
    @discord.ui.button(label="⏹️ Стоп", style=discord.ButtonStyle.red, custom_id="stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await стоп(ctx)
    
    @discord.ui.button(label="◀️ Назад", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏠 ГЛАВНОЕ МЕНЮ", description="Выбери раздел:", color=discord.Color.blue())
        embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
        embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
        embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
        embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
        embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
        embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
        embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
        embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
        await interaction.response.edit_message(embed=embed, view=MainMenuView())

class TopView(View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="💰 По ауре", style=discord.ButtonStyle.gold, custom_id="top_aura")
    async def aura_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await топ(ctx, "aura")
    
    @discord.ui.button(label="🏢 По бизнесам", style=discord.ButtonStyle.blurple, custom_id="top_biz")
    async def biz_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await топ(ctx, "бизнесы")
    
    @discord.ui.button(label="🛢️ По нефтебазам", style=discord.ButtonStyle.orange, custom_id="top_oil")
    async def oil_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await топ(ctx, "нефтебазы")
    
    @discord.ui.button(label="🔫 По ограблениям", style=discord.ButtonStyle.red, custom_id="top_robs")
    async def robs_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await топ(ctx, "ограбления")
    
    @discord.ui.button(label="⛏️ По шахте", style=discord.ButtonStyle.gray, custom_id="top_mine")
    async def mine_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = await bot.get_context(interaction.message)
        ctx.author = interaction.user
        await топ(ctx, "шахта")
    
    @discord.ui.button(label="◀️ Назад", style=discord.ButtonStyle.secondary, custom_id="back")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🏠 ГЛАВНОЕ МЕНЮ", description="Выбери раздел:", color=discord.Color.blue())
        embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
        embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
        embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
        embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
        embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
        embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
        embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
        embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
        await interaction.response.edit_message(embed=embed, view=MainMenuView())

# ========== ОСНОВНЫЕ КОМАНДЫ ==========
@bot.command()
async def farm_panel(ctx):
    button = AuraFarmButton()
    view = View(timeout=None)
    view.add_item(button)
    embed = discord.Embed(title="AURA FARMING", description="Нажми на кнопку чтобы фармить ауру", color=discord.Color.purple())
    await ctx.send(embed=embed, view=view)

@bot.command()
async def меню(ctx):
    """Открыть главное меню"""
    embed = discord.Embed(
        title="🏠 ГЛАВНОЕ МЕНЮ",
        description="Выбери раздел:",
        color=discord.Color.blue()
    )
    embed.add_field(name="💰 Фарм", value="Кнопка AURA FARM", inline=True)
    embed.add_field(name="🏢 Бизнесы", value="Купить и собирать доход", inline=True)
    embed.add_field(name="🔫 Оружие", value="Магазин и ограбления", inline=True)
    embed.add_field(name="🛢️ Нефтебаза", value="Купить и управлять", inline=True)
    embed.add_field(name="⛏️ Шахта", value="Добывать ресурсы", inline=True)
    embed.add_field(name="🛒 Магазин", value="Купить роли", inline=True)
    embed.add_field(name="🎵 Музыка", value="Включить фонк", inline=True)
    embed.add_field(name="🏆 Топы", value="Рейтинги игроков", inline=True)
    
    await ctx.send(embed=embed, view=MainMenuView())

@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    if user_id not in data:
        await ctx.send("Ты еще не фармил, Используй !farm_panel")
    else:
        bonus = get_user_bonus(ctx.author)
        await ctx.send(f"{ctx.author.name}, у тебя {data[user_id]['aura']} Aura\nМножитель: x{bonus['multiplier']}\nДневной лимит: {data[user_id].get('daily_farms', 0)}/{bonus['daily_limit']}")

@bot.command()
async def передать(ctx, участник: discord.Member, сумма: int):
    if сумма <= 0:
        await ctx.send("Сумма должна быть больше 0!")
        return
    sender_id = str(ctx.author.id)
    receiver_id = str(участник.id)
    data = load_data()
    if sender_id not in data or data[sender_id]['aura'] < сумма:
        await ctx.send("У тебя недостаточно Aura!")
        return
    if sender_id == receiver_id:
        await ctx.send("Нельзя передавать ауру самому себе!")
        return
    if receiver_id not in data:
        data[receiver_id] = {
            'name': участник.name,
            'aura': 0,
            'total_farms': 0,
            'daily_farms': 0
        }
    data[sender_id]['aura'] -= сумма
    data[receiver_id]['aura'] += сумма
    save_data(data)
    await ctx.send(f"Ты передал {сумма} Aura пользователю {участник.mention}!")

@bot.command()
async def топ(ctx, категория: str = "aura"):
    data = load_data()
    biz_data = load_businesses()
    oil_data = load_oilbases()
    weapons_data = load_weapons()
    mine_data = load_mine()
    
    if категория.lower() == "aura":
        sorted_users = sorted(data.items(), key=lambda x: x[1]['aura'], reverse=True)[:10]
        title = "Топ по Aura"
        value_key = 'aura'
        unit = "Aura"
    elif категория.lower() == "farms":
        sorted_users = sorted(data.items(), key=lambda x: x[1].get('total_farms', 0), reverse=True)[:10]
        title = "Топ по фармам"
        value_key = 'total_farms'
        unit = "фармов"
    elif категория.lower() == "бизнесы":
        biz_count = {}
        for uid, biz_list in biz_data.items():
            if uid in data:
                biz_count[uid] = len(biz_list)
        sorted_users = sorted(biz_count.items(), key=lambda x: x[1], reverse=True)[:10]
        title = "Топ по бизнесам"
    elif категория.lower() == "нефтебазы":
        oil_levels = {}
        for uid, oil in oil_data.items():
            if uid in data:
                oil_levels[uid] = oil['level']
        sorted_users = sorted(oil_levels.items(), key=lambda x: x[1], reverse=True)[:10]
        title = "Топ по нефтебазам"
    elif категория.lower() == "ограбления":
        rob_count = {}
        for uid, wep in weapons_data.items():
            if uid in data:
                rob_count[uid] = wep.get('successful_robs', 0)
        sorted_users = sorted(rob_count.items(), key=lambda x: x[1], reverse=True)[:10]
        title = "Топ по ограблениям"
    elif категория.lower() == "шахта":
        mine_level = {}
        for uid, mine in mine_data.items():
            if uid in data:
                mine_level[uid] = mine.get('pickaxe', 1)
        sorted_users = sorted(mine_level.items(), key=lambda x: x[1], reverse=True)[:10]
        title = "Топ по шахте"
    else:
        await ctx.send("Доступные категории: aura, farms, бизнесы, нефтебазы, ограбления, шахта")
        return
    
    embed = discord.Embed(title=title, color=discord.Color.gold())
    
    if категория.lower() == "бизнесы":
        for i, (user_id, count) in enumerate(sorted_users, 1):
            user = await bot.fetch_user(int(user_id))
            prefix = "1." if i == 1 else "2." if i == 2 else "3." if i == 3 else f"{i}."
            embed.add_field(name=f"{prefix} {user.name}", value=f"Бизнесов: {count}", inline=False)
    elif категория.lower() == "нефтебазы":
        for i, (user_id, level) in enumerate(sorted_users, 1):
            user = await bot.fetch_user(int(user_id))
            prefix = "1." if i == 1 else "2." if i == 2 else "3." if i == 3 else f"{i}."
            embed.add_field(name=f"{prefix} {user.name}", value=f"Нефтебаза {level} уровня", inline=False)
    elif категория.lower() == "ограбления":
        for i, (user_id, count) in enumerate(sorted_users, 1):
            user = await bot.fetch_user(int(user_id))
            prefix = "1." if i == 1 else "2." if i == 2 else "3." if i == 3 else f"{i}."
            embed.add_field(name=f"{prefix} {user.name}", value=f"Ограблений: {count}", inline=False)
    elif категория.lower() == "шахта":
        for i, (user_id, level) in enumerate(sorted_users, 1):
            user = await bot.fetch_user(int(user_id))
            prefix = "1." if i == 1 else "2." if i == 2 else "3." if i == 3 else f"{i}."
            embed.add_field(name=f"{prefix} {user.name}", value=f"Кирка {level} уровня", inline=False)
    else:
        for i, (user_id, user_data) in enumerate(sorted_users, 1):
            user = await bot.fetch_user(int(user_id))
            prefix = "1." if i == 1 else "2." if i == 2 else "3." if i == 3 else f"{i}."
            value = user_data.get(value_key, 0)
            embed.add_field(name=f"{prefix} {user.name}", value=f"{value} {unit}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def казино(ctx, ставка: int):
    user_id = str(ctx.author.id)
    data = load_data()
    if user_id not in data or data[user_id]['aura'] < ставка:
        await ctx.send("Недостаточно Aura!")
        return
    if ставка <= 0:
        await ctx.send("Ставка должна быть больше 0")
        return
    if random.choice([True, False]):
        data[user_id]['aura'] += ставка
        save_data(data)
        await ctx.send(f"Ты выиграл {ставка} Aura! Баланс: {data[user_id]['aura']}")
    else:
        data[user_id]['aura'] -= ставка
        save_data(data)
        await ctx.send(f"Ты проиграл {ставка} Aura. Баланс: {data[user_id]['aura']}")

@bot.command()
async def налоговая(ctx):
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = a + b
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
    await ctx.send(f"Налоговая проверка: сколько будет {a} + {b}? (у тебя 15 секунд)")
    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if int(msg.content) == answer:
            await ctx.send("Проверка пройдена, Можешь продолжать фармить")
            tax_counter[ctx.author.id] = 0
        else:
            await ctx.send("Неправильно. Доступ к фарму заблокирован полторы минуты")
            last_click[ctx.author.id] = time.time() + 90
    except asyncio.TimeoutError:
        await ctx.send("Время вышло попробуй снова через !налоговая")

@bot.command()
async def оружейка(ctx):
    embed = discord.Embed(title="ОРУЖЕЙНЫЙ МАГАЗИН", color=discord.Color.red())
    for weapon_id, weapon in weapons_shop.items():
        embed.add_field(name=weapon['name'], value=f"Цена: {weapon['price']} Aura\nУрон: {weapon['damage']}%\nБонус к ограблению: +{weapon['rob_bonus']}%\n{weapon['description']}\nКупить: !купить_оружие {weapon_id}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def купить_оружие(ctx, weapon_id: str):
    if weapon_id not in weapons_shop:
        await ctx.send("Такого оружия нет!")
        return
    weapon = weapons_shop[weapon_id]
    user_id = str(ctx.author.id)
    data = load_data()
    weapons_data = load_weapons()
    if user_id not in data or data[user_id]['aura'] < weapon['price']:
        await ctx.send(f"Недостаточно Aura! Нужно {weapon['price']}")
        return
    if user_id not in weapons_data:
        weapons_data[user_id] = {'weapons': [], 'successful_robs': 0, 'failed_robs': 0}
    for w in weapons_data[user_id]['weapons']:
        if w['id'] == weapon_id:
            await ctx.send("У тебя уже есть это оружие!")
            return
    weapons_data[user_id]['weapons'].append({
        'id': weapon_id,
        'name': weapon['name'],
        'damage': weapon['damage'],
        'rob_bonus': weapon['rob_bonus']
    })
    data[user_id]['aura'] -= weapon['price']
    save_data(data)
    save_weapons(weapons_data)
    await ctx.send(f"Ты купил {weapon['name']}! Теперь можно грабить с бонусом +{weapon['rob_bonus']}%")

@bot.command()
async def моё_оружие(ctx):
    user_id = str(ctx.author.id)
    weapons_data = load_weapons()
    if user_id not in weapons_data or not weapons_data[user_id]['weapons']:
        await ctx.send("У тебя нет оружия! Купи в !оружейка")
        return
    embed = discord.Embed(title=f"Арсенал {ctx.author.name}", color=discord.Color.red())
    weapons_list = ""
    for w in weapons_data[user_id]['weapons']:
        weapons_list += f"• {w['name']} (урон {w['damage']}%, бонус +{w['rob_bonus']}%)\n"
    embed.add_field(name="Оружие", value=weapons_list, inline=False)
    embed.add_field(name="Статистика", value=f"Успешных ограблений: {weapons_data[user_id].get('successful_robs', 0)}\nПровалов: {weapons_data[user_id].get('failed_robs', 0)}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def цели(ctx):
    embed = discord.Embed(title="ЦЕЛИ ДЛЯ ОГРАБЛЕНИЯ", color=discord.Color.orange())
    for target_id, target in robbery_targets.items():
        embed.add_field(name=f"{target['emoji']} {target['name']}", value=f"Награда: {target['min_reward']}-{target['max_reward']} Aura\nБазовый шанс: {target['base_chance']}%\nКулдаун: {target['cooldown']//3600}ч\nГрабить: !ограбить {target_id}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ограбить(ctx, target_id: str):
    if target_id not in robbery_targets:
        await ctx.send("Такой цели нет! Смотри !цели")
        return
    target = robbery_targets[target_id]
    user_id = str(ctx.author.id)
    data = load_data()
    weapons_data = load_weapons()
    if user_id in weapons_data and 'last_rob' in weapons_data[user_id]:
        if target_id in weapons_data[user_id]['last_rob']:
            time_passed = time.time() - weapons_data[user_id]['last_rob'][target_id]
            if time_passed < target['cooldown']:
                hours_left = int((target['cooldown'] - time_passed) / 3600)
                minutes_left = int((target['cooldown'] - time_passed) / 60) % 60
                await ctx.send(f"Ещё рано! Подожди {hours_left}ч {minutes_left}мин")
                return
    if user_id not in weapons_data or not weapons_data[user_id]['weapons']:
        await ctx.send("У тебя нет оружия! Купи в !оружейка")
        return
    best_weapon = max(weapons_data[user_id]['weapons'], key=lambda x: x['rob_bonus'])
    bonus = best_weapon['rob_bonus']
    chance = target['base_chance'] + bonus
    if chance > 95:
        chance = 95
    await ctx.send(f"Готовимся к ограблению {target['name']}...\nТвоё оружие: {best_weapon['name']} (+{bonus}%)\nИтоговый шанс успеха: {chance}%")
    await asyncio.sleep(2)
    if random.randint(1, 100) <= chance:
        reward = random.randint(target['min_reward'], target['max_reward'])
        data[user_id]['aura'] += reward
        save_data(data)
        if user_id not in weapons_data:
            weapons_data[user_id] = {'weapons': [], 'successful_robs': 0, 'failed_robs': 0, 'last_rob': {}}
        weapons_data[user_id]['successful_robs'] = weapons_data[user_id].get('successful_robs', 0) + 1
        if 'last_rob' not in weapons_data[user_id]:
            weapons_data[user_id]['last_rob'] = {}
        weapons_data[user_id]['last_rob'][target_id] = time.time()
        save_weapons(weapons_data)
        await ctx.send(f"УСПЕХ! Ты ограбил {target['name']} и получил {reward} Aura!\nНовый баланс: {data[user_id]['aura']} Aura")
    else:
        if user_id not in weapons_data:
            weapons_data[user_id] = {'weapons': [], 'successful_robs': 0, 'failed_robs': 0, 'last_rob': {}}
        weapons_data[user_id]['failed_robs'] = weapons_data[user_id].get('failed_robs', 0) + 1
        if random.randint(1, 100) <= 30:
            lost_weapon = random.choice(weapons_data[user_id]['weapons'])
            weapons_data[user_id]['weapons'].remove(lost_weapon)
            save_weapons(weapons_data)
            await ctx.send(f"ПРОВАЛ! Ты попался при ограблении {target['name']} и потерял {lost_weapon['name']}! Штраф 5000 Aura")
        else:
            save_weapons(weapons_data)
            await ctx.send(f"ПРОВАЛ! Ты попался при ограблении {target['name']}! Штраф 5000 Aura")
        data[user_id]['aura'] = max(0, data[user_id]['aura'] - 5000)
        save_data(data)

@bot.command()
async def купить_нефтебазу(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    oil_data = load_oilbases()
    if user_id not in data or data[user_id]['aura'] < 500000:
        await ctx.send("Недостаточно Aura! Нужно 500к")
        return
    if user_id in oil_data:
        await ctx.send("У тебя уже есть нефтебаза!")
        return
    oil_data[user_id] = {
        'owner': ctx.author.name,
        'level': 1,
        'security': 1,
        'oil': 1000,
        'max_oil': 1000,
        'last_collect': time.time()
    }
    data[user_id]['aura'] -= 500000
    save_data(data)
    save_oilbases(oil_data)
    await ctx.send(f"Поздравляю! Ты купил нефтебазу!\nИспользуй !моя_нефтебаза для управления")

@bot.command()
async def моя_нефтебаза(ctx):
    user_id = str(ctx.author.id)
    oil_data = load_oilbases()
    if user_id not in oil_data:
        await ctx.send("У тебя нет нефтебазы! Купи за !купить_нефтебазу")
        return
    oil = oil_data[user_id]
    level_info = oilbase_upgrades[oil['level']]
    security_info = security_levels[oil['security']]
    time_passed = time.time() - oil['last_collect']
    hours_passed = time_passed / 3600
    potential_income = int(oil['oil'] * 1.5 * hours_passed)
    embed = discord.Embed(title=f"НЕФТЕБАЗА {ctx.author.name}", color=discord.Color.orange())
    embed.add_field(name="Уровень", value=f"{oil['level']} - {level_info['name']}", inline=True)
    embed.add_field(name="Охрана", value=f"{oil['security']} - {security_info['name']} {security_info['emoji']}\nЗащита: {security_info['chance']}%", inline=True)
    embed.add_field(name="Запасы нефти", value=f"{oil['oil']}/{level_info['max_oil']} барр.", inline=True)
    embed.add_field(name="Доступно к продаже", value=f"{potential_income} Aura", inline=True)
    embed.add_field(name="Цена нефти", value=f"{oil.get('oil_price', 100)} Aura/барр.", inline=True)
    embed.add_field(name="Улучшения", value=f"Улучшить охрану: !улучшить_охрану ({security_levels[oil['security']+1]['price']} Aura если есть)\nПрокачать базу: !прокачать_базу ({level_info['price']} Aura)", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def улучшить_охрану(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    oil_data = load_oilbases()
    if user_id not in oil_data:
        await ctx.send("У тебя нет нефтебазы!")
        return
    oil = oil_data[user_id]
    current_sec = oil['security']
    if current_sec >= 10:
        await ctx.send("У тебя уже максимальный уровень охраны!")
        return
    next_sec = current_sec + 1
    price = security_levels[next_sec]['price']
    if data[user_id]['aura'] < price:
        await ctx.send(f"Недостаточно Aura! Нужно {price}")
        return
    data[user_id]['aura'] -= price
    oil['security'] = next_sec
    save_data(data)
    save_oilbases(oil_data)
    await ctx.send(f"Охрана улучшена до {next_sec} уровня: {security_levels[next_sec]['name']} {security_levels[next_sec]['emoji']}\nШанс отбить ограбление: {security_levels[next_sec]['chance']}%")

@bot.command()
async def прокачать_базу(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    oil_data = load_oilbases()
    if user_id not in oil_data:
        await ctx.send("У тебя нет нефтебазы!")
        return
    oil = oil_data[user_id]
    current_level = oil['level']
    if current_level >= 5:
        await ctx.send("У тебя уже максимальный уровень базы!")
        return
    next_level = current_level + 1
    price = oilbase_upgrades[next_level]['price']
    if data[user_id]['aura'] < price:
        await ctx.send(f"Недостаточно Aura! Нужно {price}")
        return
    data[user_id]['aura'] -= price
    oil['level'] = next_level
    oil['max_oil'] = oilbase_upgrades[next_level]['max_oil']
    save_data(data)
    save_oilbases(oil_data)
    await ctx.send(f"Нефтебаза улучшена до {next_level} уровня: {oilbase_upgrades[next_level]['name']}\nМаксимум нефти: {oilbase_upgrades[next_level]['max_oil']} барр.")

@bot.command()
async def купить_нефть(ctx, количество: int):
    user_id = str(ctx.author.id)
    data = load_data()
    oil_data = load_oilbases()
    if user_id not in oil_data:
        await ctx.send("У тебя нет нефтебазы!")
        return
    oil = oil_data[user_id]
    level_info = oilbase_upgrades[oil['level']]
    price = количество * 100
    if data[user_id]['aura'] < price:
        await ctx.send(f"Недостаточно Aura! Нужно {price}")
        return
    if oil['oil'] + количество > level_info['max_oil']:
        await ctx.send(f"Не хватит места! Максимум {level_info['max_oil']} барр.")
        return
    data[user_id]['aura'] -= price
    oil['oil'] += количество
    save_data(data)
    save_oilbases(oil_data)
    await ctx.send(f"Куплено {количество} барр. нефти за {price} Aura\nТеперь у тебя {oil['oil']} барр.")

@bot.command()
async def продать_нефть(ctx, количество: int = None):
    user_id = str(ctx.author.id)
    data = load_data()
    oil_data = load_oilbases()
    if user_id not in oil_data:
        await ctx.send("У тебя нет нефтебазы!")
        return
    oil = oil_data[user_id]
    time_passed = time.time() - oil['last_collect']
    hours_passed = time_passed / 3600
    if количество is None:
        количество = oil['oil']
    if количество > oil['oil']:
        количество = oil['oil']
    if количество <= 0:
        await ctx.send("Нет нефти для продажи!")
        return
    base_price = oil.get('oil_price', 100)
    time_bonus = int(hours_passed * 10)
    if time_bonus > 200:
        time_bonus = 200
    price_per_barrel = base_price + time_bonus
    total = количество * price_per_barrel
    bonus = get_user_bonus(ctx.author)
    total = int(total * bonus['multiplier'])
    data[user_id]['aura'] += total
    oil['oil'] -= количество
    oil['last_collect'] = time.time()
    save_data(data)
    save_oilbases(oil_data)
    await ctx.send(f"Продано {количество} барр. нефти по {price_per_barrel} Aura (x{bonus['multiplier']} от роли)\nПолучено: {total} Aura\nОстаток нефти: {oil['oil']} барр.")

@bot.command()
async def разведка(ctx, владелец: discord.Member):
    target_id = str(владелец.id)
    oil_data = load_oilbases()
    if target_id not in oil_data:
        await ctx.send("У этого игрока нет нефтебазы!")
        return
    oil = oil_data[target_id]
    security_info = security_levels[oil['security']]
    embed = discord.Embed(title=f"РАЗВЕДКА: Нефтебаза {владелец.name}", color=discord.Color.blue())
    embed.add_field(name="Уровень базы", value=oil['level'], inline=True)
    embed.add_field(name="Охрана", value=f"{security_info['name']} {security_info['emoji']}\nШанс защиты: {security_info['chance']}%", inline=True)
    embed.add_field(name="Запасы нефти", value=f"~{oil['oil']} барр.", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def ограбить_нефтебазу(ctx, владелец: discord.Member):
    user_id = str(ctx.author.id)
    target_id = str(владелец.id)
    if user_id == target_id:
        await ctx.send("Нельзя грабить сам себя!")
        return
    data = load_data()
    oil_data = load_oilbases()
    weapons_data = load_weapons()
    if target_id not in oil_data:
        await ctx.send("У этого игрока нет нефтебазы!")
        return
    target_oil = oil_data[target_id]
    if user_id not in weapons_data or not weapons_data[user_id]['weapons']:
        await ctx.send("У тебя нет оружия! Купи в !оружейка")
        return
    if user_id in weapons_data and 'last_rob_oil' in weapons_data[user_id]:
        time_passed = time.time() - weapons_data[user_id]['last_rob_oil']
        if time_passed < 3600:
            minutes_left = int((3600 - time_passed) / 60)
            await ctx.send(f"Ещё рано! Подожди {minutes_left} минут")
            return
    best_weapon = max(weapons_data[user_id]['weapons'], key=lambda x: x['rob_bonus'])
    bonus = best_weapon['rob_bonus']
    security_chance = security_levels[target_oil['security']]['chance']
    success_chance = (100 - security_chance) + bonus
    if success_chance > 80:
        success_chance = 80
    await ctx.send(f"Готовимся к ограблению нефтебазы {владелец.name}...\nТвоё оружие: {best_weapon['name']} (+{bonus}%)\nОхрана цели: {security_levels[target_oil['security']]['name']} ({security_chance}% защиты)\nИтоговый шанс успеха: {success_chance}%")
    await asyncio.sleep(3)
    if random.randint(1, 100) <= success_chance:
        stolen = random.randint(1, min(500, target_oil['oil'] // 4))
        if stolen <= 0:
            stolen = 1
        target_oil['oil'] -= stolen
        oil_price = target_oil.get('oil_price', 100)
        reward = stolen * oil_price
        bonus_mult = get_user_bonus(ctx.author)
        reward = int(reward * bonus_mult['multiplier'])
        data[user_id]['aura'] += reward
        save_data(data)
        save_oilbases(oil_data)
        if user_id not in weapons_data:
            weapons_data[user_id] = {'weapons': [], 'successful_robs': 0, 'failed_robs': 0}
        weapons_data[user_id]['successful_robs'] = weapons_data[user_id].get('successful_robs', 0) + 1
        weapons_data[user_id]['last_rob_oil'] = time.time()
        save_weapons(weapons_data)
        await ctx.send(f"УСПЕХ! Ты украл {stolen} барр. нефти и продал за {reward} Aura (x{bonus_mult['multiplier']} от роли)!")
        try:
            owner_user = await bot.fetch_user(int(target_id))
            await owner_user.send(f"ТВОЮ НЕФТЕБАЗУ ОГРАБИЛИ! {ctx.author.name} украл {stolen} барр. нефти! Охрана не справилась.")
        except:
            pass
    else:
        if user_id not in weapons_data:
            weapons_data[user_id] = {'weapons': [], 'successful_robs': 0, 'failed_robs': 0}
        weapons_data[user_id]['failed_robs'] = weapons_data[user_id].get('failed_robs', 0) + 1
        if random.randint(1, 100) <= 40:
            lost_weapon = random.choice(weapons_data[user_id]['weapons'])
            weapons_data[user_id]['weapons'].remove(lost_weapon)
            save_weapons(weapons_data)
            await ctx.send(f"ПРОВАЛ! Охрана нефтебазы скрутила тебя! Ты потерял {lost_weapon['name']} и заплатил штраф 10000 Aura")
        else:
            save_weapons(weapons_data)
            await ctx.send(f"ПРОВАЛ! Охрана нефтебазы скрутила тебя! Ты заплатил штраф 10000 Aura")
        data[user_id]['aura'] = max(0, data[user_id]['aura'] - 10000)
        save_data(data)

@bot.command()
async def бизнесы(ctx):
    embed = discord.Embed(title="Бизнесы", color=discord.Color.gold())
    for biz_id, biz in businesses.items():
        embed.add_field(name=f"{biz['emoji']} {biz['name']}", value=f"Цена: {biz['price']} Aura\nДоход: {biz['income']} Aura/час\nКуплю: !купить_бизнес {biz_id}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def купить_бизнес(ctx, biz_id: str):
    if biz_id not in businesses:
        await ctx.send("Такого бизнеса нет")
        return
    biz = businesses[biz_id]
    user_id = str(ctx.author.id)
    data = load_data()
    biz_data = load_businesses()
    if user_id not in data or data[user_id]['aura'] < biz['price']:
        await ctx.send(f"Недостаточно Aura, Нужно {biz['price']}")
        return
    if user_id not in biz_data:
        biz_data[user_id] = []
    for b in biz_data[user_id]:
        if b['id'] == biz_id:
            await ctx.send("У тебя уже есть этот бизнес")
            return
    biz_data[user_id].append({
        'id': biz_id,
        'name': biz['name'],
        'last_collect': time.time()
    })
    data[user_id]['aura'] -= biz['price']
    save_data(data)
    save_businesses(biz_data)
    await ctx.send(f"Ты купил {biz['name']}! Используй !собрать_доход")

@bot.command()
async def собрать_доход(ctx):
    user_id = str(ctx.author.id)
    biz_data = load_businesses()
    data = load_data()
    if user_id not in biz_data or not biz_data[user_id]:
        await ctx.send("У тебя нет бизнесов, Купи через !бизнесы")
        return
    total_income = 0
    current_time = time.time()
    updated_biz = []
    for biz in biz_data[user_id]:
        biz_info = businesses[biz['id']]
        time_passed = current_time - biz['last_collect']
        if time_passed >= biz_info['cooldown']:
            cycles = int(time_passed / biz_info['cooldown'])
            income = biz_info['income'] * cycles
            total_income += income
            biz['last_collect'] = current_time
            updated_biz.append(biz)
        else:
            updated_biz.append(biz)
    if total_income > 0:
        bonus = get_user_bonus(ctx.author)
        total_income = int(total_income * bonus['multiplier'])
        data[user_id]['aura'] += total_income
        save_data(data)
        save_businesses({user_id: updated_biz})
        await ctx.send(f"Ты собрал {total_income} Aura с бизнесов (x{bonus['multiplier']} от роли)!")
    else:
        next_time = int((biz_info['cooldown'] - (current_time - biz['last_collect'])) / 60)
        await ctx.send(f"Ещё рано собирать доход! Подожди {next_time} минут")

# ========== ШАХТА ==========
@bot.command()
async def шахта(ctx):
    """Пойти работать в шахту"""
    user_id = str(ctx.author.id)
    data = load_data()
    mine_data = load_mine()
    
    if user_id not in mine_data:
        mine_data[user_id] = {
            'pickaxe': 1,
            'resources': {
                'coal': 0,
                'iron': 0,
                'gold': 0,
                'diamond': 0
            },
            'last_mine': 0
        }
    
    current_time = time.time()
    if current_time - mine_data[user_id]['last_mine'] < 300:
        remaining = 300 - (current_time - mine_data[user_id]['last_mine'])
        minutes = int(remaining / 60)
        seconds = int(remaining % 60)
        await ctx.send(f"Ты устал! Отдохни ещё {minutes} мин {seconds} сек")
        return
    
    pickaxe_level = mine_data[user_id]['pickaxe']
    pickaxe_power = pickaxe_levels[pickaxe_level]['power']
    
    collapse_chance = 5
    if random.randint(1, 100) <= collapse_chance:
        damage = random.randint(1, 5)
        mine_data[user_id]['pickaxe'] = max(1, pickaxe_level - damage)
        save_mine(mine_data)
        await ctx.send(f"ОБВАЛ! Ты потерял {damage} уровня кирки! Теперь кирка {mine_data[user_id]['pickaxe']} уровня")
        return
    
    found_resources = []
    for res_id, res in mine_resources.items():
        if random.randint(1, 100) <= res['chance'] * pickaxe_power:
            amount = random.randint(1, pickaxe_power)
            mine_data[user_id]['resources'][res_id] += amount
            found_resources.append(f"{res['name']} +{amount}")
    
    if found_resources:
        mine_data[user_id]['last_mine'] = current_time
        save_mine(mine_data)
        bonus = get_user_bonus(ctx.author)
        bonus_text = f" (x{bonus['multiplier']} от роли)" if bonus['multiplier'] > 1 else ""
        await ctx.send(f"Ты нашёл: {', '.join(found_resources)}{bonus_text}\nИспользуй !мои_ресурсы чтобы посмотреть")
    else:
        await ctx.send("Ты ничего не нашёл. Попробуй ещё раз")

@bot.command()
async def купить_кирку(ctx):
    """Купить кирку (900)"""
    user_id = str(ctx.author.id)
    data = load_data()
    mine_data = load_mine()
    
    if user_id not in data or data[user_id]['aura'] < 900:
        await ctx.send("Недостаточно Aura! Нужно 900")
        return
    
    if user_id not in mine_data:
        mine_data[user_id] = {
            'pickaxe': 1,
            'resources': {
                'coal': 0,
                'iron': 0,
                'gold': 0,
                'diamond': 0
            },
            'last_mine': 0
        }
    else:
        if mine_data[user_id]['pickaxe'] >= 7:
            await ctx.send("У тебя уже максимальная кирка!")
            return
        mine_data[user_id]['pickaxe'] += 1
    
    data[user_id]['aura'] -= 900
    save_data(data)
    save_mine(mine_data)
    
    level = mine_data[user_id]['pickaxe']
    await ctx.send(f"Ты купил {pickaxe_levels[level]['name']}! Теперь кирка {level} уровня")

@bot.command()
async def мои_ресурсы(ctx):
    """Посмотреть свои ресурсы"""
    user_id = str(ctx.author.id)
    mine_data = load_mine()
    
    if user_id not in mine_data:
        await ctx.send("У тебя нет ресурсов! Сходи в !шахта")
        return
    
    resources = mine_data[user_id]['resources']
    pickaxe = mine_data[user_id]['pickaxe']
    
    embed = discord.Embed(title=f"Ресурсы {ctx.author.name}", color=discord.Color.brown())
    embed.add_field(name="Кирка", value=f"{pickaxe_levels[pickaxe]['name']} ({pickaxe} ур.)", inline=False)
    
    res_list = ""
    total_value = 0
    for res_id, res in mine_resources.items():
        amount = resources.get(res_id, 0)
        value = amount * res['price']
        total_value += value
        res_list += f"{res['emoji']} {res['name']}: {amount} шт. ({value} Aura)\n"
    
    embed.add_field(name="Ресурсы", value=res_list, inline=False)
    embed.add_field(name="Общая стоимость", value=f"{total_value} Aura", inline=False)
    embed.add_field(name="Команды", value="!продать_ресурсы - продать всё\n!продать_уголь 10 - продать 10 угля", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def продать_ресурсы(ctx, ресурс: str = None, количество: int = None):
    """Продать ресурсы: !продать_ресурсы уголь 10"""
    user_id = str(ctx.author.id)
    data = load_data()
    mine_data = load_mine()
    
    if user_id not in mine_data:
        await ctx.send("У тебя нет ресурсов!")
        return
    
    if ресурс is None:
        total = 0
        sold_items = []
        for res_id, res in mine_resources.items():
            amount = mine_data[user_id]['resources'].get(res_id, 0)
            if amount > 0:
                value = amount * res['price']
                total += value
                mine_data[user_id]['resources'][res_id] = 0
                sold_items.append(f"{amount} {res['name']} на {value} Aura")
        
        if total == 0:
            await ctx.send("У тебя нет ресурсов для продажи!")
            return
        
        bonus = get_user_bonus(ctx.author)
        total = int(total * bonus['multiplier'])
        data[user_id]['aura'] += total
        save_data(data)
        save_mine(mine_data)
        
        await ctx.send(f"Продано: {', '.join(sold_items)}\nПолучено: {total} Aura (x{bonus['multiplier']} от роли)")
        return
    
    res_map = {
        'уголь': 'coal',
        'железо': 'iron',
        'золото': 'gold',
        'алмазы': 'diamond'
    }
    
    if ресурс.lower() not in res_map:
        await ctx.send("Доступные ресурсы: уголь, железо, золото, алмазы")
        return
    
    res_id = res_map[ресурс.lower()]
    res = mine_resources[res_id]
    available = mine_data[user_id]['resources'].get(res_id, 0)
    
    if количество is None:
        количество = available
    elif количество > available:
        количество = available
    
    if количество <= 0:
        await ctx.send(f"У тебя нет {ресурс} для продажи!")
        return
    
    value = количество * res['price']
    bonus = get_user_bonus(ctx.author)
    total = int(value * bonus['multiplier'])
    
    mine_data[user_id]['resources'][res_id] -= количество
    data[user_id]['aura'] += total
    save_data(data)
    save_mine(mine_data)
    
    await ctx.send(f"Продано {количество} {res['name']} за {total} Aura (x{bonus['multiplier']} от роли)")

@bot.command()
async def прокачать_кирку(ctx):
    """Улучшить кирку"""
    user_id = str(ctx.author.id)
    data = load_data()
    mine_data = load_mine()
    
    if user_id not in mine_data:
        await ctx.send("Сначала купи кирку через !купить_кирку")
        return
    
    current_level = mine_data[user_id]['pickaxe']
    if current_level >= 7:
        await ctx.send("У тебя уже максимальная кирка!")
        return
    
    next_level = current_level + 1
    price = pickaxe_levels[next_level]['price']
    
    if data[user_id]['aura'] < price:
        await ctx.send(f"Недостаточно Aura! Нужно {price}")
        return
    
    data[user_id]['aura'] -= price
    mine_data[user_id]['pickaxe'] = next_level
    save_data(data)
    save_mine(mine_data)
    
    await ctx.send(f"Кирка улучшена до {next_level} уровня: {pickaxe_levels[next_level]['name']}")

shop_items = {
    'fonker': {
        'name': 'Фонкер',
        'price': 10000,
        'description': 'Роль настоящего ценителя Пхонка',
        'role_name': 'Фонкер',
        'color': 0x00ff00
    },
    'legend': {
        'name': 'Легенда Аура Череп',
        'price': 50000,
        'description': 'Легендарный статус',
        'role_name': 'Легенда Аура Череп',
        'color': 0xffd700
    },
    'troll': {
        'name': 'Троллфейс',
        'price': 100000,
        'description': 'Тот кто знает',
        'role_name': 'Троллфейс',
        'color': 0xff4500
    }
}

@bot.command()
async def магазин(ctx):
    embed = discord.Embed(title="Магазин ролей", description="Тут за ауру покупаешь роли йоу", color=discord.Color.gold())
    for item_id, item in shop_items.items():
        embed.add_field(name=item['name'], value=f"Цена: {item['price']} Aura\n{item['description']}\nКупить: !купить_роль {item_id}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def купить_роль(ctx, item_id: str):
    item_id = item_id.lower()
    if item_id not in shop_items:
        await ctx.send("Такого товара нет, Смотри !магазин")
        return
    item = shop_items[item_id]
    data = load_data()
    user_id = str(ctx.author.id)
    if user_id not in data or data[user_id]['aura'] < item['price']:
        await ctx.send(f"Недостаточно Aura! Нужно {item['price']}")
        return
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("У бота нет прав выдавать роли")
        return
    role = discord.utils.get(ctx.guild.roles, name=item['role_name'])
    if not role:
        try:
            role = await ctx.guild.create_role(name=item['role_name'], color=item['color'], reason="Магазин")
        except:
            await ctx.send("Не могу создать роль. Проверь права")
            return
    if role.position >= ctx.guild.me.top_role.position:
        await ctx.send(f"Роль бота должна быть выше роли {item['role_name']}!")
        return
    try:
        await ctx.author.add_roles(role)
    except:
        await ctx.send("Не могу выдать роль")
        return
    data[user_id]['aura'] -= item['price']
    save_data(data)
    await ctx.send(f"Ты купил роль {item['name']}! Остаток: {data[user_id]['aura']} Aura")

@bot.command()
async def плейлист(ctx):
    files = glob.glob(os.path.join(MUSIC_FOLDER, '*.mp3'))
    if not files:
        await ctx.send("В папке aura_phonk нет музыки!")
        return
    tracks = "\n".join([f"{i}. {os.path.basename(f)}" for i, f in enumerate(files[:15], 1)])
    if len(files) > 15:
        tracks += f"\n...и ещё {len(files) - 15}"
    embed = discord.Embed(title="Плейлист", description=tracks, color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command()
async def фонк(ctx, *, запрос=None):
    if not ctx.author.voice:
        await ctx.send("Зайди в голосовой канал!")
        return
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    files = glob.glob(os.path.join(MUSIC_FOLDER, '*.mp3'))
    if not files:
        await ctx.send("Сначала добавь музыку в папку aura_phonk!")
        return
    if запрос is None:
        chosen = random.choice(files)
        await ctx.send(f"Случайный трек: {os.path.basename(chosen)}")
    else:
        matches = [f for f in files if запрос.lower() in os.path.basename(f).lower()]
        if not matches:
            await ctx.send(f"Трек '{запрос}' не найден")
            return
        chosen = matches[0]
        if len(matches) > 1:
            await ctx.send(f"Нашёл {len(matches)} треков, играю первый: {os.path.basename(chosen)}")
        else:
            await ctx.send(f"Играю: {os.path.basename(chosen)}")
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    ffmpeg_options = {'options': '-vn'}
    ctx.voice_client.play(FFmpegPCMAudio(chosen, **ffmpeg_options))
    embed = discord.Embed(title="Сейчас играет", description=os.path.basename(chosen), color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
async def стоп(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("Музыка остановлена")
    else:
        await ctx.send("Бот не в голосовом канале")

@bot.command()
async def пауза(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Пауза")

@bot.command()
async def продолжить(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Продолжаем")

async def random_attack():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(3600)
        oil_data = load_oilbases()
        if not oil_data:
            continue
        target_id = random.choice(list(oil_data.keys()))
        target_oil = oil_data[target_id]
        bandits = [
            {'name': 'Гопники Хуёпники', 'power': 10, 'emoji': '🧟'},
            {'name': 'Бандиты', 'power': 30, 'emoji': '🔫'},
            {'name': 'Мафия Bobrito Pidorito', 'power': 50, 'emoji': '🕴️'},
            {'name': 'Спецслужбы SOBR ', 'power': 70, 'emoji': '🕵️'},
            {'name': 'Конкуренты Eblans INC', 'power': 90, 'emoji': '💼'}
        ]
        bandit = random.choice(bandits)
        if random.randint(1, 100) <= 20:
            security_chance = security_levels[target_oil['security']]['chance']
            if random.randint(1, 100) <= security_chance:
                try:
                    owner_user = await bot.fetch_user(int(target_id))
                    await owner_user.send(f"ТВОЮ НЕФТЕБАЗУ АТАКОВАЛИ! Банда {bandit['name']} {bandit['emoji']} напала, но охрана справилась!")
                except:
                    pass
            else:
                stolen = random.randint(50, 300)
                if stolen > target_oil['oil']:
                    stolen = target_oil['oil']
                target_oil['oil'] -= stolen
                save_oilbases(oil_data)
                try:
                    owner_user = await bot.fetch_user(int(target_id))
                    await owner_user.send(f"ТВОЮ НЕФТЕБАЗУ ОГРАБИЛИ БОТЫ! Банда {bandit['name']} {bandit['emoji']} украла {stolen} барр. нефти! Улучши охрану.")
                except:
                    pass

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен!')
    print(f'Бот на серверах: {len(bot.guilds)}')
    print(f'Бизнесов: {len(businesses)}')
    print(f'Ролей с бонусами: {len(role_bonuses)}')
    print(f'Оружия: {len(weapons_shop)}')
    print(f'Целей для ограблений: {len(robbery_targets)}')
    print(f'Команды: !farm_panel, !balance, !передать, !топ, !казино, !налоговая, !бизнесы, !оружейка, !цели, !ограбить, !купить_нефтебазу, !моя_нефтебаза, !разведка, !ограбить_нефтебазу, !шахта, !купить_кирку, !мои_ресурсы, !продать_ресурсы, !прокачать_кирку, !меню')
    bot.loop.create_task(random_attack())

bot.run(os.getenv('TOKEN'))