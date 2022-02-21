import datetime
from exceptions import *
from settings import Properties, VERSION_NO, AUTHORS, GITHUB
from telegram import ChatMember
from telegram.update import Update
from telegram.ext import CallbackContext


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
    handler_names = [func for func in dir(handler_class) if
                     callable(getattr(handler_class, func)) and not func.startswith("__")]
    handler_dict = {}
    for name in handler_names:
        handler_dict[name] = handler_class.__dict__[name].__get__(handler_class)

    return handler_dict


def check_credentials(user: ChatMember) -> bool:
    """
    Metoda sprawdza, czy dany użytkownik jest adminem.

    Parameters
    ----------
    user
        Klasa telegram.ChatMember, która zawiera informacji o użytkowniku w chacie.

    Returns
    -------
    bool
        Czy użytkownik jest adminem.

    """
    return user.status in ('creator', 'administrator')


def log_str(username: str, command_name: str) -> str:
    """
    Metoda zwraca sformatowany string do logów.

    Parameters
    ----------
    username
        Nazwa użytkownika.
    command_name
        Nazwa komendy.
    Returns
    -------

    """
    return f"{datetime.datetime.now()} 》Użytkownik {username} użył komendy /{command_name}"


def error(update: Update, context: CallbackContext) -> None:
    """
    Handler obsługujący błędy.

    Parameters
    ----------
    update
        Obiekt telegram.ext.Update posiadający informacje o requeście.
    context
        Obiekt telegram.ext.CallbackContext, który zawiera głównie podane argumenty.
    """

    print(f"{datetime.datetime.now()} ERR!》\n{update}\n caused error {context.error}!")


class CommandHandlers:
    """
    Klasa zawierająca statyczne metody handlujące komendy.
    """

    @staticmethod
    def help(update: Update, context: CallbackContext) -> None:
        """
        Handler obsługujący komendę /help

        Parameters
        ----------
        update
            Obiekt telegram.ext.Update posiadający informacje o requeście.
        context
            Nie używany.
        """

        user = update.message.bot.get_chat_member(update.message.chat.id, update.
                                                  message.from_user.id)
        print(log_str(update.message.from_user.username, 'help'))

        mess_str = '**Nie ma!**'
        if user.status == 'creator':
            mess_str += ' brudny ownerze'
        update.message.reply_text(mess_str)

    @staticmethod
    def rules(update: Update, context: CallbackContext) -> None:
        """
        Handler obsługujący komendę /rules

        Parameters
        ----------
        update
            Obiekt telegram.ext.Update posiadający informacje o requeście.
        context
            Nie używany.
        """

        print(log_str(update.message.from_user.username, 'rules'))
        with open(Properties.properties['rules']) as rules:
            mess_str = rules.read() + 'Do administracji grupy należą:\nZałożyciel - @DingoLisVaru\n'

            for admin in update.message.chat.get_administrators():
                if admin.status != 'creator':
                    mess_str += f'{admin.custom_title} - @{admin.user.username}'

            mess_str += f'\n\nLink do grupy: {Properties.properties["group_link"]}'

            update.message.reply_text(mess_str)

    @staticmethod
    def about(update: Update, context: CallbackContext) -> None:
        """
        Handler obsługujący komendę /about

        Parameters
        ----------
        update
            Obiekt telegram.ext.Update posiadający informacje o requeście.
        context
            Nie używany.
        """
        print(log_str(update.message.from_user.username, 'about'))

        mess_str = f'Akalice Bot (wersja {VERSION_NO})\n\nBot został stworzony dla grupy Białystok i Akalice w celu zarządzania tym serwerem.\n\nAutorzy:\n'

        for author in AUTHORS:
            mess_str += f'@{author}\n'

        mess_str += f'\nGithub: {GITHUB}'

        update.message.reply_text(mess_str)

    @staticmethod
    def update_rules(update: Update, context: CallbackContext) -> None:
        """
        Handler obsługujący komendę /update_rules

        Parameters
        ----------
        update
            Obiekt telegram.ext.Update posiadający informacje o requeście.
        context
            Nie używany.
        """

        print(log_str(update.message.from_user.username, 'update_rules'))

        if update.message.chat.type != 'private':
            update.message.reply_text(PMS_REQUIRED_MESS)
            return
        if not check_credentials(
                update.message.bot.get_chat_member(Properties.properties['chat_id'], update.message.from_user.id)):
            update.message.reply_text(INVALID_STATUS)
            return
        # następnie jakoś to uaktualnia


class MessageHandlers:
    """
    Klasa zawierające statyczne metody handlujące wiadomości.
    """

    @staticmethod
    def listen(update: Update, context: CallbackContext) -> None:
        """
        Handler słuchający chatu

        Parameters
        ----------
        update
            Obiekt telegram.ext.Update posiadający informacje o requeście.
        context
            Nie używany.

        """

        print(f'{datetime.datetime.now()} 》{update.message.text}')
