from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from AnonXMusic import app

@app.on_message(filters.command("poll"))
async def send_poll(client, message):
    question = "What is your favorite programming language?"
    options = ["Python", "JavaScript", "Java", "C++"]
    
    # Send a poll with options using the PollType enum for a quiz-style poll
    await message.reply_poll(
        question=question,
        options=options,
        is_anonymous=False,  # Set False for non-anonymous poll (participants' votes are visible)
        type=enums.PollType.QUIZ,  # Or use enums.PollType.REGULAR for a regular poll
        correct_option_id=0,  # Index of the correct option (0 for "Python" in this case)
        explanation="Python is known for being beginner-friendly and versatile.",
        explanation_parse_mode="markdown",  # You can use markdown or html here
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Try another poll", callback_data="another_poll")]
        ])
    )
