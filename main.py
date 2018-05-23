# -*- coding: utf-8 -*-  
#!/usr/bin/env python3
from telethon import TelegramClient, events

from trash_filter import is_trash
from config import TG_API_ID, TG_API_HASH, TG_APP_TITLE, PHONE, FORWARDING_CHANNELS, DEST_CHANNEL
from config import SOURCE_DIALOGS, DEST_DIALOGS


def get_dialog_by_name(name):
	global client
	for dialog in client.get_dialogs():
		if dialog.name == name:
			return dialog
	return None

def get_source_ids(sources):
	source_ids = set()
	for source_type, sources in SOURCE_DIALOGS.items():
		for source in sources:
			if source_type == "names":
				dialog = get_dialog_by_name(source)
				source_ids.add(dialog.id)

			if source_type in {"aliases"}:
				# dialog = client.get_entity(source)
				print(dialog)
				# source_ids.add(dialog)
					


def main():
	global client
	global sources
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

	sources = get_source_ids(SOURCE_DIALOGS)

	@client.on(events.NewMessage)
	def handle_msg(event):
		message = event.message
		# print(event.message)
		flag = False
		# for source_type, sources in SOURCE_DIALOGS.items():
		# 	for source in sources:
		# 		if source_type == "names":
		# 			# if get_dialog_by_name(source) is not None:
		# 			# 	flag = True

		# 			pass
				# if source_type in {"aliases"}:
				# 	if client.get_entity(source):
				# 		flag = True
					
		# print(flag)

				# print(message)
				# chat.send_message(message=message)

		# if event.is_channel:
		# 	for dest_name in DEST_NAMES:
		# 		dest_dialog = get_dest(client, "name", dest_name)
				
		# 		dest_dialog.send_message(message=event.message)
				
		# 	return
		# 	channel = client.get_entity(event.message.to_id)
		# 	if channel.username in FORWARDING_CHANNELS:
		# 		msg_text = event.message.message
				
		# 		# if is_trash(msg_text):
		# 		#     return
				
		# 		client.send_message(DEST_CHANNEL, msg_text, file=event.message.media)

	client.idle()


if __name__ == '__main__':
	main()
