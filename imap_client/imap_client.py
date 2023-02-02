import datetime
import imaplib
from imapclient import imap_utf7
import codetiming


class ImapClient:
    __session: imaplib.IMAP4_SSL
    __directories: list

    def __init__(self, server: str, login: str, password: str):
        self.__session = imaplib.IMAP4_SSL(server)
        self.__session.login(login, password)
        self.__session.enable('UTF8=ACCEPT')
        self.__directories = self.__get_directories()

    def __del__(self):
        self.__session.logout()

    def delete(self, date_range: tuple, directories: list = None):
        date_range[1] += datetime.timedelta(days=1)
        if directories is None:
            directories = self.__directories
            directories.remove('Trash')
        for directory in directories:
            print(f'Processing directory "{directory}"...\n')
            if not self.__directories.count(directory):
                raise ValueError(f'Directory "{directory}" does not exist.\nExisting directories: {self.__directories}')
            status, messages = self.__session.select(imap_utf7.encode(directory).decode('utf-8'))
            if status != 'OK':
                raise RuntimeError(f'Open directory request has status "{status}"')
            messages_count: int = int(messages[0])
            print(f'Found a total of {messages_count} messages.\n')
            status, messages = self.__session.search(None, f'(SINCE {date_range[0].strftime("%d-%b-%Y")} '
                                                           f'BEFORE {date_range[1].strftime("%d-%b-%Y")})')
            messages: list = messages[0].split()
            print(f'Found for removing of {len(messages)} messages.\n')
            timer = codetiming.Timer(text='Removal in {:0.4f} seconds.\n')
            timer.start()
            self.__session.store(f'{messages[0].decode("utf-8")}:{messages[-1].decode("utf-8")}', '+FLAGS', '\\Deleted')
            self.__session.expunge()
            self.__session.close()
            timer.stop()

    def __get_directories(self) -> list:
        directories: list = []
        status, directory_list = self.__session.list()
        if status != 'OK':
            raise RuntimeError(f'Directories request has status "{status}"')
        for directory in directory_list:
            directory: bytes
            directories.append(imap_utf7.decode(directory).split('"|"')[-1].strip().replace('"', ''))
        return directories
