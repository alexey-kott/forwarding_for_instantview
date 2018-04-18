# -*- coding: utf-8 -*-  
#!/usr/bin/env python3
from telethon import TelegramClient, events

from trash_filter import is_trash
from config import TG_API_ID, TG_API_HASH, TG_APP_TITLE, PHONE, FORWARDING_CHANNELS, DEST_CHANNEL





def main():
    client = TelegramClient(PHONE.strip('+'),
                            TG_API_ID,
                            TG_API_HASH,
                            proxy=None,
                            update_workers=4,
                            spawn_read_thread=False)

    client.start()

    if not client.is_user_authorized():
        client.send_code_request(PHONE)
        client.sign_in(PHONE, input("Enter code: "))

    @client.on(events.NewMessage)
    def handle_msg(event):
        if event.is_channel:

            channel = client.get_entity(event.message.to_id)
            if channel.username in FORWARDING_CHANNELS:
                msg_text = event.message.message
                
                if is_trash(msg_text):
                    return
                
                client.send_message(DEST_CHANNEL, msg_text, file=event.message.media)

    client.idle()


if __name__ == '__main__':
    main()