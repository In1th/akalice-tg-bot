import asyncio
import datetime
from exceptions import *
from settings import properties_dict
import telegram.ext as tg
import telegram.update


async def get_handlers(handler_class) -> dict:
    '''
    Otrzymaj wszystkie funkcje z klas zajmujących się handlerami

    Parameters
    ----------
    handler_class:
        klasa z handlerami
    
    Returns
    -------
    dict
        Słownik ze wszystkimi funkcjami
    '''
    handler_names = [func for func in dir(handler_class) if callable(getattr(handler_class, func)) and not func.startswith("__")]
    handler_dict = {}
    for name in handler_names:
        handler_dict[name] = handler_class.__dict__[name].__get__(handler_class)
    
    return handler_dict

def error(update: telegram.update.Update, context):
    print(f"{datetime.datetime.now()} ERR!》\n{update}\n caused error {context.error}!")
class CommandHandlers:

    @staticmethod
    def help(update: telegram.update.Update, context) -> None:
        update.message.reply_text("Nie ma!")
        print(update)
        print(f"{datetime.datetime.now()} 》Użytkownik {update.message.from_user['username']} użył komendy /help")

    @staticmethod
    def rules(update: telegram.update.Update, context) -> None:

        print(f"{datetime.datetime.now()} 》Użytkownik {update.message.from_user['username']} użył komendy /rules")
        with open("rules.txt") as rules:
           update.message.reply_text(rules.read())