from collections import defaultdict

from telethon import TelegramClient, events

from config import TG_API_ID, TG_API_HASH, PHONE, FORWARDING_SCHEMA
import logging
logging.basicConfig(level=logging.ERROR)


def get_forwarding_schema():
    forwarding_schema = []
    for forwarding_item in FORWARDING_SCHEMA:
        item = defaultdict(set)
        for direction, names in forwarding_item.items():
            entities = {search_entities(name) for name in names if search_entities(name)}
            item[direction] = entities
        forwarding_schema.append(item)

    return forwarding_schema


def search_entities(name):
    name = name.strip('@')
    for dialog in user_dialogs:
        if dialog.name == name:
            return dialog.entity.id
    for dialog in user_dialogs:
        if getattr(dialog.entity, 'username', None) == name:
            return dialog.entity.id
        if getattr(dialog.entity, 'title', None) == name:
            return dialog.entity.id


def get_dialog(peer_entity):
    try:
        entity_id = peer_entity.channel_id
    except AttributeError:
        entity_id = peer_entity.chat_id

    for dialog in user_dialogs:
        if dialog.entity.id == entity_id:
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

        sender_ids = {entity.id for id, entity in event._entities.items()}

        for item in forwarding_schema:
            intersection = item['SOURCE'] & sender_ids
            if intersection:
                entity = get_dialog(event.message.to_id)
                try:
                    addressee = client.get_entity(event.message.from_id)
                    last_name = lambda name: name if None else ''
                    addressee_name = f"{addressee.first_name} {last_name(addressee.last_name)}"
                except TypeError:
                    addressee_name = f"{entity.title}"

                msg_text = f"{addressee_name}\n {event.message.message}"
                for dest_id in item['DESTINATION']:
                    client.send_message(dest_id, msg_text, file=event.message.media)

    client.idle()


if __name__ == '__main__':
    main()