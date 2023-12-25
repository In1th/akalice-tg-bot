import asyncio
import datetime
import random
from exceptions import *
from settings import Properties, VERSION_NO, AUTHORS, GITHUB
from telegram import ChatMember, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from telegram.update import Update
from telegram.ext import CallbackContext
from telegram.utils import helpers
import requests

new_users = list()
papaj_used = []

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
        wyświetla tą listę

        Parameters
        ----------
        update
            Obiekt telegram.ext.Update posiadający informacje o requeście.
        context
            Nie używany.
        """

        commands = asyncio.run(get_handlers(CommandHandlers))

        non_admin = []
        admin = []

        mess_str = 'Lista dostępnych komend: \n'

        for command_name in commands.keys():
            doc = commands[command_name].__doc__.split('\n')
            if doc[1][8:] == 'Admin':
                admin.append((command_name, doc[2][8:]))
            else:
                non_admin.append((command_name, doc[1][8:]))

        for command in non_admin:
            mess_str += f'/{command[0]} - {command[1]}\n'

        mess_str += '\nKomendy dostępne tylko dla administracji chatu:\n'

        for command in admin:
            mess_str += f'/{command[0]} - {command[1]}\n'

        update.message.reply_text(mess_str)

    @staticmethod
    def rules(update: Update, context: CallbackContext) -> None:
        """
        zasady panujące na kanale

        Parameters
        ----------
        update
            Obiekt telegram.ext.Update posiadający informacje o requeście.
        context
            Nie używany.
        """

        print(log_str(update.message.from_user.username, 'rules'))
        with open(Properties.properties['rules']) as rules:
            mess_str = rules.read() + 'Do administracji grupy należą:\nZałożyciel - @Dingo_LisVaru\n'

            for admin in update.message.chat.get_administrators():
                if admin.status != 'creator' and admin.custom_title not in ('Bot', 'Barbuz'):
                    mess_str += f'{admin.custom_title} - @{admin.user.username}\n'

            mess_str += f'\nLink do grupy: {Properties.properties["group_link"]}'

            update.message.reply_text(mess_str)

    @staticmethod
    def about(update: Update, context: CallbackContext) -> None:
        """
        informacje o bocie

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

        button = InlineKeyboardButton('Github', url=GITHUB)

        update.message.reply_text(mess_str, reply_markup=InlineKeyboardMarkup([[button]]))

    @staticmethod
    def update_rules(update: Update, context: CallbackContext) -> None:
        """
        Admin
        aktualizuje zasady kanału

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

    @staticmethod
    def mute(update: Update, context: CallbackContext) -> None:
        '''
        Admin
        wycisz użytkownika

        Parameters
        ----------
        update
        context

        Returns
        -------

        '''
        pass

    @staticmethod
    def warn(update: Update, context: CallbackContext) -> None:
        '''
        Admin
        daj ostrzeżenie dla użytkownika

        Parameters
        ----------
        update
        context

        Returns
        -------

        '''
        pass

    @staticmethod
    def kick(update: Update, context: CallbackContext) -> None:
        '''
        Admin
        wyrzuć użytkownika

        Parameters
        ----------
        update
        context

        Returns
        -------

        '''
        pass

    @staticmethod
    def ban(update: Update, context: CallbackContext) -> None:
        '''
        Admin
        zbanuj użytkownika

        Parameters
        ----------
        update
        context

        Returns
        -------

        '''
        pass

    @staticmethod
    def papaj(update: Update, context: CallbackContext) -> None:
        """
        komenda papieska z memami

        Parameters
        ----------
        update
            Obiekt telegram.ext.Update posiadający informacje o requeście.
        context
            Nie używany.
        """
        papaj_ok = True
        for elem in papaj_used:
            if elem == update.message.from_user.id:
                papaj_ok = False
                break

        if papaj_ok:
            print(log_str(update.message.from_user.username, 'papaj'))
            time = datetime.datetime.now()
            if time.hour == 21 and time.minute == 37:
                response = requests.get(Properties.properties["cenzopapa_memes_index"])
                if response.status_code == 200:
                    image_urls = [url.strip() for url in response.text.splitlines() if url.strip()]
                    random_image_url = random.choice(image_urls)
                    if random_image_url.lower().endswith('.gif'):
                        update.message.reply_animation(random_image_url)
                    else:
                        update.message.reply_photo(random_image_url)
                    papaj_used.append(update.message.from_user.id)
                else:
                    update.message.reply_text(f"HTTP 2137 ERROR - PAPAJ MEMES NOT FOUND")
            else:
                update.message.reply_text("Dokładnie o 21:37 możesz tego użyć!")
        else:
            update.message.reply_text("Tylko raz dziennie możesz tego użyć!")

class MessageHandlers:
    """
    Klasa zawierające statyczne metody handlujące wiadomości.
    """

    @staticmethod
    def listen_new_members(update: Update, context: CallbackContext) -> None:
        """
        Handler słuchający czy nie ma nowych członków

        Parameters
        ----------
        update
            Obiekt telegram.ext.Update posiadający informacje o requeście.
        context
            Nie używany.

        """

        permissions = ChatPermissions(can_send_messages=False,
                                      can_send_media_messages=False,
                                      can_send_polls=False,
                                      can_send_other_messages=False,
                                      can_add_web_page_previews=False,
                                      can_change_info=False,
                                      can_invite_users=False,
                                      can_pin_messages=False)

        for member in update.message.new_chat_members:
            new_users.append(member.id)
            update.message.bot.restrict_chat_member(update.message.chat_id, member.id, permissions)
            button = InlineKeyboardButton('Weryfikacja', url=helpers.create_deep_linked_url(update.message.bot.username,
                                                                                            'weryfikacja'))
            update.message.reply_text(
                f'Witamy @{update.message.new_chat_members[0].username} na grupie Białystok i Akalice!\n\nAby móc pisać na tym czacie musisz przejść weryfikację poniżej:',
                reply_markup=InlineKeyboardMarkup([[button]]))


class Verify:

    @staticmethod
    def verify(update: Update, context: CallbackContext) -> None:

        answers = [('Białystok', 'correct'), ('Warszawa', 'incorrect'), ('Kraków', 'incorrect'), ('Łódź', 'incorrect')]
        random.shuffle(answers)
        buttons = [[], []]
        i = 0

        for answer in answers:
            buttons[i % 2].append(InlineKeyboardButton(answer[0], callback_data=answer[1]))
            i += 1

        update.message.reply_text('Witaj!\n\nAby zweryfikować się i odzyskać dostęp do czatu, kliknij proszę '
                                  'odpowiedź na pytanie: "Bo moje miasto to..."',
                                  reply_markup=InlineKeyboardMarkup(buttons))


class QueryHandler:

    @staticmethod
    def query(update: Update, context: CallbackContext) -> None:
        token = update.callback_query.data

        if token == 'correct':

            permissions = ChatPermissions(can_send_messages=True,
                                          can_send_media_messages=True,
                                          can_send_polls=True,
                                          can_send_other_messages=True,
                                          can_add_web_page_previews=False,
                                          can_change_info=False,
                                          can_invite_users=False)

            if update.callback_query.from_user.id not in new_users:
                update.callback_query.answer('Weryfikacja przebiegła pomyślnie! Jesteś już zweryfikowany, więc nie '
                                             'musisz tego robić jeszcze raz.')
                return

            update.callback_query.bot.restrict_chat_member(Properties.properties['chat_id'],
                                                           update.callback_query.from_user.id,
                                                           permissions)

            new_users.remove(update.callback_query.from_user.id)

            update.callback_query.answer('Weryfikacja przebiegła pomyślnie! Możesz już pisać na chacie.')

        elif token == 'incorrect':
            update.callback_query.answer('Zła odpowiedź! Spróbuj ponownie!')
