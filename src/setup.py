import asyncio
from json import load
import datetime
import handlers
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler


async def load_properties(name: str) -> dict:
    """
    Załaduj properties z JSONa o podanej nazwie

    Parameters
    ----------
    name: str
        Nazwa JSONa

    Returns
    -------
    dict
        Słownik z danymi
    """

    try:
        with open(name) as file:
            data = load(file)
            return data
    except FileNotFoundError:
        print(f"{datetime.datetime.now()} ERR!》Nie znaleziono pliku properties!")
        return dict()


def init_api_con(api_key: str) -> tuple[Updater, Dispatcher]:
    """
    Połącz się z API Telegrama po kluczu

    Parameters
    ----------
    api_key: str
        klucz API

    Returns
    -------
    tuple[telegram.ext.Updater, telegram.ext.Dispatcher]
        Krotka zawierająca obiekty Updater i Dispatcher z telegram.ext
    """

    updater = Updater(api_key, use_context=True)
    discpacher = updater.dispatcher
    return updater, discpacher


async def load_handlers(ds: Dispatcher) -> None:
    """
    Załaduj wszystkie handlery do Dispatchera
    """

    command_handlers_task = asyncio.create_task(handlers.get_handlers(handlers.CommandHandlers))

    command_handlers = await command_handlers_task

    for command_name, command_func in command_handlers.items():
        ds.add_handler(CommandHandler(command_name, command_func, run_async=True))

    ds.add_handler(MessageHandler(Filters.status_update.new_chat_members,
                                  handlers.MessageHandlers.listen_new_members, run_async=True))
    
    ds.add_handler(MessageHandler(Filters.update.message,
                                  handlers.MessageHandlers.listen_phrase, run_async=True))

    ds.add_handler(CommandHandler('start', handlers.Verify.verify, filters= Filters.regex('weryfikacja'), run_async=True))

    ds.add_handler(CallbackQueryHandler(handlers.QueryHandler.query, run_async=True))

    ds.add_error_handler(handlers.error)
