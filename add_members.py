import os
import sys
import csv
import random
import time
import traceback
import datetime
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, UserIdInvalidError
from telethon.tl.functions.channels import InviteToChannelRequest
import configparser

# Console colors for output
re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"

def banner():
    print(f"""
{re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
{re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬┘
{re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─

            version : 1.1
    """)

def load_config():
    """Loads Telegram API credentials from config.data"""
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
        print(re + "[!] Run python3 setup.py first to configure the bot.\n")
        sys.exit(1)

async def reconnect_client(client, phone):
    """Reconnects the Telegram client in case of a disconnection."""
    try:
        print(gr + "[+] Reconnecting to Telegram...")
        await client.disconnect()
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            await client.sign_in(phone, input(gr + '[+] Enter the code: ' + re))
        print(gr + "[+] Reconnected successfully.")
    except Exception as e:
        print(re + f"[!] Error while reconnecting: {str(e)}")
        sys.exit(1)

async def main():
    api_id, api_hash, phone = load_config()
    client = TelegramClient(phone, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        os.system('clear')
        banner()
        await client.sign_in(phone, input(gr + '[+] Enter the code: ' + re))

    os.system('clear')
    banner()
    input_file = sys.argv[1]
    output_file = 'membersAdded.csv'
    users = []

    # Read the CSV file and shuffle users
    with open(input_file, encoding='UTF-8') as f:
        rows = csv.reader(f, delimiter=",", lineterminator="\n")
        next(rows, None)  # Skip header
        for row in rows:
            try:
                user_id = int(row[1]) if row[1].isdigit() else None
                access_hash = int(row[2]) if row[2].isdigit() else None
                user = {
                    'username': row[0] if row[0] else None,
                    'id': user_id,
                    'access_hash': access_hash,
                    'name': row[3]
                }
                if user['id'] and user['access_hash']:
                    users.append(user)
                else:
                    print(f"{re}Skipping invalid user data in row: {row}")
            except ValueError:
                print(f"{re}Error: Invalid data in row: {row}. Skipping.")
                continue

    # Shuffle users list for random order
    random.shuffle(users)

    chats = []
    result = await client(GetDialogsRequest(
        offset_date=None,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=500,
        hash=0
    ))
    chats.extend(result.chats)

    groups = [chat for chat in chats if getattr(chat, 'megagroup', False)]

    # Group selection
    for i, group in enumerate(groups):
        print(gr + '[' + cy + str(i) + gr + ']' + cy + ' - ' + group.title)

    print(gr + '[+] Choose a group to add members')
    g_index = input(gr + "[+] Enter a Number : " + re)
    target_group = groups[int(g_index)]
    target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

    # Member addition
    print(gr + "[1] Add member by user ID\n[2] Add member by username ")
    mode = int(input(gr + "Input : " + re))

    with open(output_file, 'w', encoding='UTF-8') as file:
        writer = csv.writer(file, delimiter=",", lineterminator="\n")
        writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])

    for n, user in enumerate(users, start=1):
        if n % 50 == 0:
            time.sleep(random.randrange(30, 600))

        try:
            user_id = user.get('id')
            access_hash = user.get('access_hash')
            username = user.get('username')
            user_name = user.get('name')

            if not user_id or not access_hash:
                print(re + f"[!] Skipping user with missing id or access_hash: {user}")
                continue

            if not username:
                print(gr + f"[+] Adding by user ID: {user_id} and access hash: {access_hash}")
                user_to_add = InputPeerUser(int(user_id), int(access_hash))
            else:
                print(gr + f"[+] Adding by username: {username}")
                try:
                    user_to_add = await client.get_input_entity(username)
                except Exception as e:
                    print(re + f"[!] Unable to fetch entity for username: {username}. Error: {str(e)}")
                    continue

            await client(InviteToChannelRequest(target_group_entity, [user_to_add]))

            print(gr + f"[+] User added successfully: ID={user_id}, Username={username}, Name={user_name}")

            with open(output_file, 'a', encoding='UTF-8') as file:
                writer = csv.writer(file, delimiter=",", lineterminator="\n")
                writer.writerow([username, user_id, access_hash, user_name, target_group.title, target_group.id])

            print(gr + "[+] Waiting for 30-600 Seconds...")
            time.sleep(random.randrange(30, 600))

        except PeerFloodError:
            print(re + "[!] Flood Error from Telegram. Stopping script. Try again later.")
            break
        except UserPrivacyRestrictedError:
            print(re + "[!] User's privacy settings prevent adding. Skipping.")
        except errors.FloodWaitError as e:
            wait_time = e.seconds
            wait_until = datetime.datetime.now() + datetime.timedelta(seconds=wait_time)
            print(re + f"[!] FloodWaitError: Wait for {wait_time} seconds until {wait_until}.")
            time.sleep(wait_time)
        except UserIdInvalidError:
            print(re + f"[!] Invalid user ID or access hash for user: {user}. Skipping.")
        except errors.SecurityError as e:
            print(re + f"[!] SecurityError: {str(e)}. Attempting to reconnect.")
            await reconnect_client(client, phone)
        except Exception as e:
            if "Server sent a very old message" in str(e):
                print(re + f"[!] Old message from server: {str(e)}. Ignoring...")
                continue
            elif "Too many messages had to be ignored consecutively" in str(e):
                print(re + f"[!] Too many ignored messages: {str(e)}. Reconnecting client.")
                await reconnect_client(client, phone)
            else:
                traceback.print_exc()
                print(re + f"[!] Unexpected Error: {str(e)}")
                continue

if __name__ == "__main__":
    asyncio.run(main())
