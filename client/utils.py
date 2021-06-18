def parse_message(message):
    return (str(message[1:3]), str(message[4:] if len(message) > 4 else ''))
