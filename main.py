import asyncio
from collections import defaultdict
from typing import Union

from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerChat, PeerUser
from googletrans import Translator

from config import TG_API_ID, TG_API_HASH, PHONE
from forwarding_schema import FORWARDING_SCHEMA
import logging

logging.basicConfig(level=logging.ERROR)
translator = Translator()
forwarding_schema = []

client = TelegramClient(PHONE.strip('+'),
                        TG_API_ID,
                        TG_API_HASH)


def init_forwarding_schema():
    for forwarding_item in FORWARDING_SCHEMA:
        item = defaultdict(set)
        for direction, names in forwarding_item.items():
            entities = {search_entities(name) for name in names if search_entities(name)}
            item[direction] = entities
        if forwarding_item.get("TRANSLATE"):
            item['TRANSLATE'] = forwarding_item['TRANSLATE']
        forwarding_schema.append(item)


def search_entities(name: str) -> int:
    for dialog in user_dialogs:
        if name.startswith('@'):
            if getattr(dialog.entity, 'username', None) == name.strip('@'):
                return dialog.entity.id
        else:
            if getattr(dialog.entity, 'title', None) == name:
                return dialog.entity.id
            if dialog.name == name:
                return dialog.entity.id


def get_message_text(addressee: str,
                     msg_text: str, translate_schema=None) -> str:
    if translate_schema is None:
        return f"{msg_text}"
    else:
        translate = translator.translate(msg_text,
                                         src=translate_schema.get("FROM"),
                                         dest=translate_schema.get('TO'))
        return f"{addressee}\n {msg_text}\n\n{translate.text}"


def get_dialog(peer_entity: Union[PeerChannel, PeerChat, PeerUser]):
    try:
        entity_id = peer_entity.channel_id
    except AttributeError:
        entity_id = peer_entity.chat_id

    for dialog in user_dialogs:
        if dialog.entity.id == entity_id:
            return dialog.entity


@client.on(events.NewMessage)
async def handler(event):
    sender_ids = {entity.id for entity_id, entity in event._entities.items()}

    for item in forwarding_schema:
        intersection = item['SOURCE'] & sender_ids
        if intersection:
            entity = get_dialog(event.message.to_id)
            try:
                addressee = await client.get_entity(event.message.from_id)
                last_name = lambda name: name if None else ''
                addressee_name = f"{addressee.first_name} {last_name(addressee.last_name)}"
            except TypeError:
                addressee_name = f"{entity.title}"

            msg_text = get_message_text(addressee=addressee_name,
                                        msg_text=event.message.message,
                                        translate_schema=item.get('TRANSLATE'))

            for dest_id in item['DESTINATION']:
                await client.send_message(dest_id, msg_text, file=event.message.media)


async def main() -> None:
    global user_dialogs

    await client.start()

    user_dialogs = await client.get_dialogs()
    init_forwarding_schema()

    await client.run_until_disconnected()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
