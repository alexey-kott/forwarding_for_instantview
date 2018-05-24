# -*- coding: utf-8 -*-  
#!/usr/bin/env python3
from telethon import TelegramClient, events

from trash_filter import is_trash
from config import TG_API_ID, TG_API_HASH, TG_APP_TITLE, PHONE, FORWARDING_CHANNELS, DEST_CHANNEL
from config import SOURCE_DIALOGS, DEST_DIALOGS


def get_dialog_by_field(field, value):
	global client
	for dialog in client.get_dialogs():
		if getattr(dialog, field) == value:
			return dialog
	return None


def get_source_ids():
	source_ids = set()
	for source_type, identificators in SOURCE_DIALOGS.items():
		for identificator in identificators:
			if source_type == "names":
				dialog = get_dialog_by_field('name', identificator)
				source_ids.add(dialog.id)

			if source_type in {"aliases"}:
				dialog = client.get_entity(identificator)
				source_ids.add(dialog.id)

	return source_ids
					

def get_dest_ids():
	dest_ids = set()
	for dest_type, identificators in DEST_DIALOGS.items():
		for identificator in identificators:
			if dest_type == "names":
				dialog = get_dialog_by_field('name', identificator)
				dest_ids.add(dialog.id)

			if dest_type in {"aliases"}:
				dialog = client.get_entity(identificator)
				dest_ids.add(dialog.id)

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


	@client.on(events.NewMessage)
	def handle_msg(event):
		if event.is_channel:
			dialog_id = event.message.to_id.channel_id
		elif event.is_private:
			dialog_id = event.message.to_id.user_id
		elif event.is_group:
			dialog_id = event.message.to_id.group_id

		if dialog_id in sources:
			for destination in destinations:
				dialog = get_dialog_by_field('id', destination)
				text = "{}\n{}".format(dialog.name, event.message.message)
				dialog.send_message(message=text)


	client.idle()


if __name__ == '__main__':
	main()
