from collections import defaultdict

from telethon import TelegramClient, events

from config import TG_API_ID, TG_API_HASH, PHONE, FORWARDING_SCHEMA


def get_forwarding_schema():
    forwarding_schema = []
    for forwarding_item in FORWARDING_SCHEMA:
        item = defaultdict(list)
        for direction, names in forwarding_item.items():
            entities = [search_entities(name) for name in names if search_entities(name)]
            item[direction] = entities
        forwarding_schema.append(item)

    return forwarding_schema


def search_entities(name):
    name = name.strip('@')
    for dialog in user_dialogs:
        # print(dialog.entity, end='\n\n')
        if dialog.name == name:
            return dialog.entity
    for dialog in user_dialogs:
        # print(dialog.entity, end='\n\n')
        if getattr(dialog.entity, 'username', None) == name:
            return dialog.entity
        if getattr(dialog.entity, 'title', None) == name:
            return dialog.entity



def main():
    global client
    global user_dialogs
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

    user_dialogs = client.get_dialogs()

    forwarding_schema = get_forwarding_schema()

    @client.on(events.NewMessage)
    def handle_msg(event):
        source_entities = [entity for entity_id, entity
                           in event._entities.items()]

        for item in forwarding_schema:
            lol = item['SOURCE']
            print(set(**lol))
            if set(item['SOURCE']) & set(source_entities):
                for entity in item['DESTINATION']:
                    print(entity)
        # for i in event._entities:
        #     print(i, end='\n\n')
        # if event.is_channel:
        #
        #     channel = client.get_entity(event.message.to_id)
        #     if channel.username in FORWARDING_CHANNELS:
        #         msg_text = event.message.message
        #
        #         if is_trash(msg_text):
        #             return
        #
        #         client.send_message(DEST_CHANNEL, msg_text, file=event.message.media)

    client.idle()


if __name__ == '__main__':
    main()