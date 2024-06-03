import asyncio
import json
from telethon.sync import TelegramClient
from telethon.tl.types import MessageService
class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)
    async def start(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))
            last_message_ids = {}  # Dictionary to store the last message ID for each chat
    async def list_chats(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))
        dialogs = await self.client.get_dialogs()
        chats_file = open(f"chats_of_{self.phone_number}.txt", "w", encoding="utf-8")
        for dialog in dialogs:
            print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
            chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")
        chats_file.close()
        print("List of groups printed successfully!")
    async def forward_messages_to_channel(self, source_chat_ids, destination_channel_id, keywords):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))
        last_message_ids = {}
        for chat_id in source_chat_ids:
            last_message_ids[chat_id] = (await self.client.get_messages(chat_id, limit=1))[0].id
        while True:
            print("Checking for messages and forwarding them...")
            for chat_id in source_chat_ids:
                messages = await self.client.get_messages(chat_id, min_id=last_message_ids[chat_id], limit=None)
                for message in reversed(messages):
                    if message.media:
                        await self.forward_media_message(destination_channel_id, message)
                        print("Message with media forwarded")
                    elif keywords and message.text and any(keyword in message.text.lower() for keyword in keywords):
                        await self.client.forward_messages(destination_channel_id, message)
                        print(f"Message containing keyword '{message.text}' forwarded")
                    else:
                        await self.client.forward_messages(destination_channel_id, message)
                        print("Message forwarded")
                    last_message_ids[chat_id] = max(last_message_ids[chat_id], message.id)
            await asyncio.sleep(1)
    async def forward_media_message(self, destination_channel_id, message):
        if message.photo:
            await self.client.send_file(destination_channel_id, message.photo, caption=message.text)
        elif message.video:
            await self.client.send_file(destination_channel_id, message.video, caption=message.text)
async def main():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        config = {}
    api_id = config.get("api_id") or input("Enter your API ID: ")
    api_hash = config.get("api_hash") or input("Enter your API Hash: ")
    phone_number = config.get("phone_number") or input("Enter your phone number: ")
    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    print("Choose an option:")
    print("1. List Chats")
    print("2. Forward Messages")
    choice = input("Enter your choice: ")
    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        source_chat_ids = input("Enter the source chat IDs (comma-separated): ").split(",")
        source_chat_ids = [int(chat_id.strip()) for chat_id in source_chat_ids]
        destination_channel_id = int(input("Enter the destination chat22111548 ID: "))
        print("Enter keywords if you want to forward messages with specific keywords, or leave blank to forward every message!")
        keywords = input("Put keywords (comma separated if multiple, or leave blank): ").split(",")
        await forwarder.forward_messages_to_channel(source_chat_ids, destination_channel_id, keywords)
    else:
        print("Invalid choice")
if __name__ == "__main__":
    asyncio.run(main())
