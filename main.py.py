import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
from zoneinfo import ZoneInfo  # Импорт для работы с временными зонами

# Создание экземпляра бота
bot = telebot.TeleBot('Вставьте код телеграм бота')

# Создаем планировщик в фоновом режиме
scheduler = BackgroundScheduler(timezone=ZoneInfo("Europe/Moscow"))  # Указываем часовой пояс
scheduler.start()

# Словарь для хранения настроек пользователей
user_settings = {}

def send_reminder(chat_id, text):
    bot.send_message(chat_id, text)

def schedule_default_reminders(chat_id):
    # Дни и время напоминаний по умолчанию
    days = [14, 15, 16]  # Дни напоминаний
    times = ['10:00', '14:30', '17:00']  # Время напоминаний
    for day in days:
        for time in times:
            hour, minute = map(int, time.split(':'))
            scheduler.add_job(send_reminder, 'cron', day=day, hour=hour, minute=minute, args=(chat_id, "Не забудь сдать показания воды!"))

def schedule_user_reminders(chat_id):
    days = user_settings[chat_id]['days']
    times = user_settings[chat_id]['times']
    for day in days:
        for time in times:
            hour, minute = map(int, time.split(':'))
            scheduler.add_job(send_reminder, 'cron', day=day, hour=hour, minute=minute, args=(chat_id, "Не забудь сдать показания воды!"))

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = types.KeyboardButton('Стандартное напоминание')
    btn2 = types.KeyboardButton('Расширенные настройки')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Привет! Выберите режим напоминания:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Стандартное напоминание')
def handle_default(message):
    schedule_default_reminders(message.chat.id)
    bot.send_message(message.chat.id, 'Стандартные напоминания установлены!')

@bot.message_handler(func=lambda message: message.text == 'Расширенные настройки')
def handle_custom(message):
    user_settings[message.chat.id] = {'days': [], 'times': []}
    bot.send_message(message.chat.id, 'Введите дни для напоминаний через запятую (например, 15,16,21):')

@bot.message_handler(func=lambda message: 'days' in user_settings.get(message.chat.id, {}) and not user_settings[message.chat.id]['days'])
def set_days(message):
    days = message.text.split(',')
    user_settings[message.chat.id]['days'] = days
    bot.send_message(message.chat.id, 'Теперь введите время напоминаний через запятую (например, 10:00,14:30,17:00):')

@bot.message_handler(func=lambda message: 'times' in user_settings.get(message.chat.id, {}) and not user_settings[message.chat.id]['times'])
def set_times(message):
    times = message.text.split(',')
    user_settings[message.chat.id]['times'] = times
    schedule_user_reminders(message.chat.id)
    bot.send_message(message.chat.id, 'Напоминания установлены!')

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    run_bot()
