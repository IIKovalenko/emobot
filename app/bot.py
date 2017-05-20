import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from emotions import process_file
from settings import BOT_API_KEY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename=os.path.join(BASE_DIR, 'bot.log')
                    )

logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('Отправь мне фотографию.')


def echo(bot, update):
    update.message.reply_text('Отправьте мне фотографию {}'.format(update.message.from_user.first_name))


def get_emotion(bot, update):
    update.message.reply_text("Обрабатываю")
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join(BASE_DIR, 'downloads', '%s.jpg' % photo_file.file_id)
    photo_file.download(filename)
    logger.info("Photo from %s - %s" % (update.message.from_user.first_name, filename))
    process_file(filename, saveto=filename)
    bot.sendPhoto(chat_id=update.message.chat_id, photo=open(filename, 'rb'))


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(BOT_API_KEY)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.photo, get_emotion))
    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    logger.info('Starting bot')
    main()
