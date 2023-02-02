from imap_client import ImapClient
from datetime import date, datetime


def delete_old_emails(start_date: date, finish_date: date, folders: list = None):
    if (datetime.now().date() - finish_date).days < 90:
        raise ValueError('You are trying to delete emails that are less than 90 days old.')
    client: ImapClient = ImapClient('IMAP_SERVER', 'LOGIN', 'PASSWORD')
    client.delete((start_date, finish_date), folders)


if __name__ == "__main__":
    delete_old_emails(date(2022, 1, 1), date(2023, 1, 1))
