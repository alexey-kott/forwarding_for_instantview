def is_trash(msg_text):
    trash = ['подписыва', 'подписаться']
    msg_text = msg_text.lower()
    for word in trash:
        if msg_text.find(word) != -1:
            return True

    return False