from collections import defaultdict

from telethon import TelegramClient, events
from googletrans import Translator

from config import TG_API_ID, TG_API_HASH, PHONE
from forwarding_schema import FORWARDING_SCHEMA
import logging

logging.basicConfig(level=logging.ERROR)
translator = Translator()


def get_forwarding_schema():
    forwarding_schema = []
    for forwarding_item in FORWARDING_SCHEMA:
        item = defaultdict(set)
        for direction, names in forwarding_item.items():
            entities = {search_entities(name) for name in names if search_entities(name)}
            item[direction] = entities
        if forwarding_item.get("TRANSLATE"):
            item['TRANSLATE'] = forwarding_item['TRANSLATE']
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


def get_dialog_by_id(entity_id):
    for dialog in user_dialogs:
        if dialog.entity.id == entity_id:
            return dialog.entity


def get_message_text(addressee, msg_text, translate_schema=None):
    if translate_schema is None:
        return f"{addressee}\n {msg_text}"
    else:
        translate = translator.translate(msg_text,
                                         src=translate_schema.get("FROM"),
                                         dest=translate_schema.get('TO'))
        return f"{addressee}\n {translate.text}"


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
                entity = get_dialog_by_id(event.message.to_id.channel_id)
                try:
                    addressee = client.get_entity(event.message.from_id)
                    last_name = lambda name: name if None else ''
                    addressee_name = f"{addressee.first_name} {last_name(addressee.last_name)}"
                except TypeError:
                    addressee_name = f"{entity.title}"

                msg_text = get_message_text(addressee=addressee_name,
                                            msg_text=event.message.message,
                                            translate_schema=item.get('TRANSLATE'))

                for dest_id in item['DESTINATION']:
                    client.send_message(dest_id, msg_text, file=event.message.media)

    client.idle()


if __name__ == '__main__':
    main()
