# -*- coding: utf-8 -*-  
#!/usr/bin/env python3
from telethon import TelegramClient, events

from trash_filter import is_trash
from config import TG_API_ID, TG_API_HASH, TG_APP_TITLE, PHONE, FORWARDING_CHANNELS, DEST_CHANNEL
from config import SOURCE_DIALOGS, DEST_DIALOGS


def get_dialog_by_field(field, value):
	global client
	for dialog in client.get_dialogs():
		if getattr(dialog.entity, field, '') == value:
			return dialog.entity
	return None


def get_source_ids():
	source_ids = set()
	for source_type, identificators in SOURCE_DIALOGS.items():
		for identificator in identificators:
			try:
				if source_type == "titles":
					dialog = get_dialog_by_field('title', identificator)
					source_ids.add(dialog.id)

				if source_type == "names":
					dialog = get_dialog_by_field('name', identificator)
					source_ids.add(dialog.id)

				if source_type in {"aliases"}:
					dialog = client.get_entity(identificator)
					source_ids.add(dialog.id)
			except:
				pass

	return source_ids
					

def get_dest_ids():
	dest_ids = set()
	for dest_type, identificators in DEST_DIALOGS.items():
		for identificator in identificators:
			try:
				if dest_type == "titles":
					dialog = get_dialog_by_field('title', identificator)
					dest_ids.add(dialog.id)

				elif dest_type == "names":
					dialog = get_dialog_by_field('name', identificator)
					dest_ids.add(dialog.id)

				elif dest_type in {"aliases"}:
					dialog = client.get_entity(identificator)
					dest_ids.add(dialog.id)
			except:
				pass

	return dest_ids


def clear_chat(dialog_name): # TODO
	# dialog = get_dialog_by_field("name", dialog_name)
	pass


def main():
	global client
	global sources, destinations

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

	sources = get_source_ids()
	destinations = get_dest_ids()
	# print(sources)
	# print(destinations)

	@client.on(events.NewMessage)
	def handle_msg(event):
		if event.is_channel:
			source_id = event._chat_peer.channel_id
		elif event.is_private:
			source_id = event._chat_peer.user_id
		elif event.is_group:
			source_id = event._chat_peer.channel_id
		
		if source_id in sources:
			for destination in destinations:
				dialog = get_dialog_by_field('id', destination)
				source_dialog = get_dialog_by_field('id', source_id)
				text = "{}\n{}".format(source_dialog.title, event.message.message)
				client.send_message(dialog, text)
	client.idle()


if __name__ == '__main__':
	main()
