import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
import io
import random
import os

# ===== ВСТАВЬТЕ ВАШ ТОКЕН СЮДА =====
TOKEN = "8752757389:AAHDzeKIEVzzYn7Xo1wfAWO7Qks74alhMiQ"
# ===================================

# Хранилище языков пользователей
user_languages = {}

LANGUAGES = {
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English',
    'uz': '🇺🇿 Oʻzbek',
    'kk': '🇰🇿 Қазақша'
}

TEXTS = {
    'ru': {
        'welcome': "✨ Добро пожаловать! Я создаю карточки товаров.\n\nОтправьте фото товара, и я сделаю 6 готовых карточек!",
        'send_photo': "📸 Отправьте фото товара",
        'processing': "⏳ Обрабатываю... 10-15 секунд",
        'done': "✅ Готово! Ваши карточки:",
        'error': "❌ Ошибка. Попробуйте другое фото",
        'select_lang': "🌐 Выберите язык:"
    },
    'en': {
        'welcome': "✨ Welcome! Send a product photo, I'll make 6 cards!",
        'send_photo': "📸 Send product photo",
        'processing': "⏳ Processing... 10-15 seconds",
        'done': "✅ Done! Your cards:",
        'error': "❌ Error. Try another photo",
        'select_lang': "🌐 Select language:"
    },
    'uz': {
        'welcome': "✨ Xush kelibsiz! Mahsulot rasmini yuboring, 6 ta karta tayyorlayman!",
        'send_photo': "📸 Mahsulot rasmini yuboring",
        'processing': "⏳ Qayta ishlanyapti... 10-15 soniya",
        'done': "✅ Tayyor! Sizning kartalaringiz:",
        'error': "❌ Xatolik. Boshqa rasm yuboring",
        'select_lang': "🌐 Tilni tanlang:"
    },
    'kk': {
        'welcome': "✨ Қош келдіңіз! Тауар суретін жіберіңіз, 6 карточка жасаймын!",
        'send_photo': "📸 Тауар суретін жіберіңіз",
        'processing': "⏳ Өңделуде... 10-15 секунд",
        'done': "✅ Дайын! Сіздің карточкаларыңыз:",
        'error': "❌ Қате. Басқа сурет жіберіңіз",
        'select_lang': "🌐 Тілді таңдаңыз:"
    }
}

def create_card(image_data, card_num):
    img = Image.open(io.BytesIO(image_data))
    no_bg = remove(img)
    
    card = Image.new('RGB', (1000, 1000), 'white')
    product = no_bg.resize((700, 700))
    card.paste(product, (150, 150), product)
    
    draw = ImageDraw.Draw(card)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
    except:
        font = ImageFont.load_default()
    
    prices = [1290, 1490, 990, 1990, 890, 1690]
    price = prices[card_num % 6]
    
    draw.text((100, 850), f"{price} ₽", fill='red', font=font)
    draw.rectangle((100, 920, 350, 970), fill='green')
    draw.text((130, 935), "Купить", fill='white', font=font)
    
    return card

async def start(update, context):
    keyboard = [[InlineKeyboardButton(text, callback_data=lang)] for lang, text in LANGUAGES.items()]
    await update.message.reply_text(TEXTS['ru']['select_lang'], reply_markup=InlineKeyboardMarkup(keyboard))

async def language_callback(update, context):
    query = update.callback_query
    await query.answer()
    lang = query.data
    user_languages[query.from_user.id] = lang
    await query.edit_message_text(TEXTS[lang]['welcome'])
    await query.message.reply_text(TEXTS[lang]['send_photo'])

async def handle_photos(update, context):
    user_id = update.message.from_user.id
    lang = user_languages.get(user_id, 'ru')
    
    await update.message.reply_text(TEXTS[lang]['processing'])
    
    photo_file = await update.message.photo[-1].get_file()
    image_data = await photo_file.download_as_bytearray()
    
    for i in range(6):
        card = create_card(image_data, i)
        img_bytes = io.BytesIO()
        card.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        await update.message.reply_photo(photo=img_bytes, caption=f"📦 Карточка {i+1}")
    
    await update.message.reply_text(TEXTS[lang]['done'])

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photos))
    print("🤖 Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
