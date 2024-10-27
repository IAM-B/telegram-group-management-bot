from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os
import configparser
import csv
import time

# Console colors for output
re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"

def banner():
    print(f"""
{re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
{re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬┘
{re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─

            version : 3.1
    """)

def load_config():
    """Load API credentials from config file."""
    cpass = configparser.RawConfigParser()
    cpass.read('config.data')

    try:
        api_id = cpass['cred']['id']
        api_hash = cpass['cred']['hash']
        phone = cpass['cred']['phone']
        return api_id, api_hash, phone
    except KeyError:
        os.system('clear')
        banner()
        print(re + "[!] Please run python3 setup.py first !!\n")
        sys.exit(1)

def main():
    api_id, api_hash, phone = load_config()
    client = TelegramClient(phone, api_id, api_hash)

    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(phone)
        os.system('clear')
        banner()
        code = input(gr + '[+] Enter the code: ' + re)
        try:
            client.sign_in(phone, code)
        except telethon.errors.SessionPasswordNeededError:
            password = input(gr + '[+] Enter your password: ' + re)
            client.sign_in(phone, code, password=password)

    os.system('clear')
    banner()

    # Fetch all chats and filter to find groups
    chats = []
    chunk_size = 200
    result = client(GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)

    groups = [chat for chat in chats if getattr(chat, 'megagroup', False)]

    # Display available groups for selection
    print(gr + '[+] Choose a group to scrape members :' + re)
    for i, g in enumerate(groups):
        print(gr + '[' + cy + str(i) + gr + ']' + cy + ' - ' + g.title)

    print('')
    g_index = input(gr + "[+] Enter a Number : " + re)
    target_group = groups[int(g_index)]

    print(gr + '[+] Fetching Members...')
    time.sleep(1)
    all_participants = client.get_participants(target_group, aggressive=True)

    print(gr + '[+] Saving to file...')
    time.sleep(1)
    with open("members.csv", "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])
        for user in all_participants:
            username = user.username if user.username else ""
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])

    print(gr + '[+] Members scraped successfully.')

if __name__ == "__main__":
    main()
