import asyncio
from pyrogram import Client, filters
from pyrogram.enums import PollType
from pyrogram.types import Message, PollOption, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.raw.types import MessageMediaPoll, UpdateMessagePoll
from googletrans import Translator
from AnonXMusic import app

# Initialize translator
translator = Translator()

# Store quiz data and user responses
quiz_data = {}
user_scores = {}

# Start quiz command with custom title and time limit
@app.on_message(filters.command("startquiz"))
async def start_quiz(client, message: Message):
    # Check if the user has provided the title and time limit
    args = message.text.split(" ", 2)
    if len(args) < 3:
        await message.reply("Please provide the title and time limit for the quiz. Example: `/startquiz <title> <time_limit_in_seconds>`")
        return

    quiz_title = args[1]  # Quiz title from the user
    try:
        time_limit = int(args[2])  # Time limit in seconds
    except ValueError:
        await message.reply("Please provide a valid time limit in seconds.")
        return
    
    # Save quiz data and user scores
    quiz_data[message.chat.id] = {"quiz_title": quiz_title, "questions": [], "current_question": 0, "time_limit": time_limit}
    user_scores[message.chat.id] = {}

    # Send confirmation message
    await message.reply(f"Quiz titled '{quiz_title}' is starting! Time limit for each question is {time_limit} seconds. Use `/quiz` command to add questions.")


# /quiz command to receive polls and add them as questions dynamically
@app.on_message(filters.command("quiz"))
async def add_question(client, message: Message):
    # Check if the message contains a poll
    if message.poll:
        poll = message.poll

        # Extract the question and options from the poll
        question_text = poll.question
        options = [option.text for option in poll.options]

        # For now, we will just set the first option as the correct answer (optional: you can implement a more complex system)
        correct_answer = options[0]  # Assume the first option is the correct answer

        # Add the new question to the quiz data
        quiz_data[message.chat.id]["questions"].append({
            "question": question_text,
            "answers": options,
            "correct": correct_answer
        })
        
        # Confirm that the question has been added
        await message.reply(f"Question added: {question_text}\nOptions: {', '.join(options)}")
    else:
        await message.reply("Please send a poll to add a question to the quiz.")


# Translate command for English to Hindi and vice versa
@app.on_message(filters.command("translate"))
async def translate(client, message: Message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply("Please provide text to translate.")
        return
    
    text_to_translate = args[1]
    translated_text = translator.translate(text_to_translate, src='en', dest='hi')
    
    await message.reply(f"Translated Text: {translated_text.text}")


# Evaluate quiz answers and give +4 for correct and -1 for incorrect answers
async def evaluate_quiz(client, chat_id, poll_message_id):
    # Get poll results
    poll_results = await client.get_poll_results(chat_id, poll_message_id)

    # Get correct answer from quiz data
    correct_answer = quiz_data[chat_id]["questions"][quiz_data[chat_id]["current_question"]]["correct"]
    
    for voter in poll_results:
        selected_answer = voter.answer
        if selected_answer == correct_answer:
            # +4 points for correct answer
            user_scores[chat_id][voter.user_id] = user_scores.get(voter.user_id, 0) + 4
        else:
            # -1 point for incorrect answer
            user_scores[chat_id][voter.user_id] = user_scores.get(voter.user_id, 0) - 1

    # Proceed to next question or finish quiz
    quiz_data[chat_id]["current_question"] += 1
    if quiz_data[chat_id]["current_question"] < len(quiz_data[chat_id]["questions"]):
        # Send next question
        question = quiz_data[chat_id]["questions"][quiz_data[chat_id]["current_question"]]["question"]
        answers = quiz_data[chat_id]["questions"][quiz_data[chat_id]["current_question"]]["answers"]
        
        # Create PollOptions dynamically for the next question
        poll_options = [PollOption(text=answer) for answer in answers]

        # Send a media poll (for illustration, can add media such as images)
        media_poll = MessageMediaPoll(question=question, options=answers)
        await client.send_media_group(chat_id, [media_poll])
    else:
        # End of quiz
        await end_quiz(client, chat_id)


# End quiz and display results
async def end_quiz(client, chat_id):
    result_text = "Quiz Finished! Here are the results:\n\n"
    for user_id, score in user_scores[chat_id].items():
        user = await client.get_users(user_id)
        result_text += f"{user.first_name}: {score} points\n"

    await client.send_message(chat_id, result_text)

    # Clean up
    del quiz_data[chat_id]
    del user_scores[chat_id]
