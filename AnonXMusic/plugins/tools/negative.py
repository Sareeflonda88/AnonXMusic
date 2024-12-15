from pyrogram.types import InputPollOption
from AnonXMusic import app

await app.send_poll(
    chat_id=chat_id,
    question="Is this a poll question?",
    options=[
        InputPollOption(text="Yes"),
        InputPollOption(text="No"),
        InputPollOption(text= "Maybe"),
    ]
)
