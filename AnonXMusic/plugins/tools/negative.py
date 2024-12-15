from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Poll
from pyrogram.enums import PollType
from AnonXMusic import app, LOGGER

# Add question handler
@app.on_message(filters.command("addquestion"))
async def add_question(client, message):
    await message.reply(
        "Please send the question for the quiz. For example: What is 2 + 2?"
    )
    await message.reply(
        "You can cancel the question addition process anytime by sending /cancel."
    )

    # Await the question input
    question_response = await client.listen(message.chat.id)
    question = question_response.text

    # Ask for possible answers
    await message.reply("Please send the options (e.g., A) 4, B) 5, C) 6).")

    options_response = await client.listen(message.chat.id)
    options = options_response.text.split(", ")

    # Ask for the correct answer
    await message.reply("Please send the correct option (e.g., A).")

    correct_answer_response = await client.listen(message.chat.id)
    correct_answer = correct_answer_response.text

    # Send the poll to the user
    poll_options = [InlineKeyboardButton(option, callback_data=option) for option in options]
    poll_keyboard = InlineKeyboardMarkup([[button] for button in poll_options])

    await message.reply(
        question,
        reply_markup=poll_keyboard,
        poll=Poll(type=PollType.QUIZ, options=options, correct_option_id=options.index(correct_answer)),
    )

    await message.reply("Your quiz question has been sent!")

# Cancel command handler
@app.on_message(filters.command("cancel"))
async def cancel(client, message):
    await message.reply("Question addition process has been canceled.")

# Handling Poll Answers with on_message instead of on_poll_answer
@app.on_message(filters.poll_answer)
async def handle_poll_answer(client, message):
    poll_answer = message.poll_answer
    user_id = poll_answer.user.id
    selected_option = poll_answer.option_ids[0]

    # You can store or use the results here
    await client.send_message(user_id, f"You selected option: {selected_option}")
