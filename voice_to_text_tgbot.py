
!pip install pyTelegramBotAPI
!pip install SpeechRecognition
!pip install pydub
import os
import telebot
import speech_recognition
from PIL import Image, ImageEnhance, ImageFilter
from pydub import AudioSegment

token = ''
bot = telebot.TeleBot(token)

def transform_image(filename):
    # Функция обработки изображения
    source_image = Image.open(filename)
    enhanced_image = source_image.filter(ImageFilter.EMBOSS)
    enhanced_image = enhanced_image.convert('RGB')
    width = enhanced_image.size[0]
    height = enhanced_image.size[1]

    enhanced_image = enhanced_image.resize((width // 2, height // 2))

    enhanced_image.save(filename)
    return filename


@bot.message_handler(content_types=['photo'])
def resend_photo(message):
    # Функция отправки обработанного изображения
    file_id = message.photo[-1].file_id
    filename = download_file(bot, file_id)

    # Трансформируем изображение
    transform_image(filename)

    image = open(filename, 'rb')
    bot.send_photo(message.chat.id, image)
    image.close()
    
    # Не забываем удалять ненужные изображения
    if os.path.exists(filename):
        os.remove(filename)

def oga2wav(filename):
    # Конвертация формата файлов
    new_filename = filename.replace('.oga', '.wav')
    audio = AudioSegment.from_file(filename)
    audio.export(new_filename, format='wav')
    return new_filename

def recognize_speech(oga_filename):
    # Перевод голоса в текст + удаление использованных файлов
    wav_filename = oga2wav(oga_filename)
    recognizer = speech_recognition.Recognizer()

    with speech_recognition.WavFile(wav_filename) as source:
        wav_audio = recognizer.record(source)

    text = recognizer.recognize_google(wav_audio, language='ru')

    if os.path.exists(oga_filename):
        os.remove(oga_filename)

    if os.path.exists(wav_filename):
        os.remove(wav_filename)

    return text


def download_file(bot, file_id):
    # Скачивание файла, который прислал пользователь
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_id + file_info.file_path
    filename = filename.replace('/', '_')
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    return filename

@bot.message_handler(commands=['start'])
def say_hi(message):
    bot.send_message(message.chat.id, 'Привет, Я конвертер вашего голоса в текст.\nОтправьте /help для просмотора доступных команд.')

@bot.message_handler(commands=['whoami'])
def say_whoami(message):
    bot.send_message(message.chat.id, 'Рад познакомиться.\nВаше имя - '+ message.chat.first_name +'\n'+"Ваша фамилия - "+message.chat.last_name)

@bot.message_handler(commands=['help'])
def say_help(message):
    bot.send_message(message.chat.id, '/start - Начало работы с ботом\n'+
                     '/help - Посмотреть список всех доступных команд\n'+
                     '/whoami - Вывести ваше имя и фамилию'+
                     'Отправь фото и я его обработаю и сожму')

@bot.message_handler(content_types=['voice'])
def transcript(message):
    # Функция, отправляющая текст в ответ на голосовое
    filename = download_file(bot, message.voice.file_id)
    text = recognize_speech(filename)
    bot.send_message(message.chat.id, text)

bot.polling()
