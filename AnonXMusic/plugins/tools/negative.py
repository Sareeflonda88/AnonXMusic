import logging
from pyrogram import Client, filters
from pyrogram.enums import PollType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)


# Define some quiz questions
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct_answer": "Paris"
    },
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "correct_answer": "4"
    },
    {
        "question": "Who is the CEO of Tesla?",
        "options": ["Elon Musk", "Jeff Bezos", "Bill Gates", "Mark Zuckerberg"],
        "correct_answer": "Elon Musk"
    }
]

# Command to start the quiz
@app.on_message(filters.command("quiz"))
def send_quiz(client, message):
    for q in questions:
        options = q["options"]
        question_text = q["question"]

        # Create Inline keyboard for answers
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(option, callback_data=option) for option in options]
        ])

        # Send the quiz
        app.send_poll(
            chat_id=message.chat.id,
            question=question_text,
            options=options,
            type=PollType.QUIZ,
            correct_option_id=options.index(q["correct_answer"]),
            explanation=f"The correct answer is: {q['correct_answer']}",
            explanation_parse_mode="Markdown",
            reply_markup=reply_markup
        )

# Handle quiz responses
@app.on_poll_answer()
def handle_poll_answer(client, poll_answer):
    user_answer = poll_answer.option_ids[0]  # the user's selected option
    correct_answer = questions[poll_answer.poll_id]["correct_answer"]
    if user_answer == correct_answer:
        client.send_message(poll_answer.user.id, "Correct!")
    else:
        client.send_message(poll_answer.user.id, f"Wrong! The correct answer is {correct_answer}.")
