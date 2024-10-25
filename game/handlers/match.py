from shared.schema.messages.match import CreateMatchMessage


def handle_event_create_match(message: CreateMatchMessage):
    user_ids: list[int] = message["user_ids"]
    print("create room for user_ids ", user_ids)
    ## create room
