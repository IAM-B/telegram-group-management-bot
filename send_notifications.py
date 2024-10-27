#!/bin/env python3
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, UserIdInvalidError
import configparser
import os
import sys
import csv
import time

# Console colors for output
re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"
SLEEP_TIME = 30

class main():
    @staticmethod
    def banner():
        print(f"""
    {re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
    {re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬┘
    {re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─

                version : 3.1
            """)

    @staticmethod
    def send_sms():
        try:
            cpass = configparser.RawConfigParser()
            cpass.read('config.data')
            api_id = cpass['cred']['id']
            api_hash = cpass['cred']['hash']
            phone = cpass['cred']['phone']
        except KeyError:
            os.system('clear')
            main.banner()
            print(re + "[!] Please run python3 setup.py first!\n")
            sys.exit(1)

        client = TelegramClient(phone, api_id, api_hash)
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
            os.system('clear')
            main.banner()
            client.sign_in(phone, input(gr + '[+] Enter the code: ' + re))
        
        os.system('clear')
        main.banner()
        input_file = sys.argv[1]
        output_file = 'members_notified.csv'
        users = []

        # Read the input CSV file
        with open(input_file, encoding='UTF-8') as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)  # Skip header
            for row in rows:
                user = {
                    'username': row[0],
                    'id': int(row[1]),
                    'access_hash': int(row[2]),
                    'name': row[3]
                }
                users.append(user)

        # Initialize the output CSV file for notified members
        with open(output_file, 'w', encoding='UTF-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'id', 'access_hash', 'name'])  # Write header

        print(gr + "[1] Send SMS by user ID\n[2] Send SMS by username")
        mode = int(input(gr + "Input : " + re))
         
        message = """
Your_message
https://t.me/addlist/...
"""
        for user in users:
            # Select user based on chosen mode
            if mode == 2:
                if not user['username']:
                    continue
                try:
                    receiver = client.get_input_entity(user['username'])
                except UserIdInvalidError:
                    print(re + f"[!] Invalid User ID for {user['username']}. Skipping.")
                    continue
            elif mode == 1:
                try:
                    receiver = InputPeerUser(user['id'], user['access_hash'])
                except UserIdInvalidError:
                    print(re + f"[!] Invalid User ID or Access Hash for {user['name']}. Skipping.")
                    continue
            else:
                print(re + "[!] Invalid Mode. Exiting.")
                client.disconnect()
                sys.exit()

            try:
                print(gr + "[+] Sending Message to:", user['name'])
                client.send_message(receiver, message)

                # Record notified member in the output CSV
                with open(output_file, 'a', encoding='UTF-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([user['username'], user['id'], user['access_hash'], user['name']])

                print(gr + "[+] Waiting {} seconds".format(SLEEP_TIME))
                time.sleep(SLEEP_TIME)

            except PeerFloodError:
                print(re + "[!] Flood Error from Telegram. Stopping script. Please try again later.")
                client.disconnect()
                sys.exit()
            except UserPrivacyRestrictedError:
                print(re + f"[!] Privacy settings restrict messaging for {user['name']}. Skipping.")
            except Exception as e:
                print(re + "[!] Error:", e)
                print(re + "[!] Trying to continue...")
                continue

        client.disconnect()
        print("Done. Message sent to all users.")

if __name__ == "__main__":
    main.send_sms()
