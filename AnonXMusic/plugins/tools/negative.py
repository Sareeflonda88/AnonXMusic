from pyrogram import Client, filters
from pyrogram.types import Poll
from AnonXMusic import app 

# Store quiz data and user scores
quiz_data = {
    "questions": [],
    "poll_ids": {},  # Maps poll_id to question index
    "scores": {},  # user_id: score
    "current_question": 0,
    "group_id": None,
}

NEGATIVE_MARKING = -1  # Penalty for incorrect answers


@Client.on_message(filters.command("start_quiz") & filters.group)
async def start_quiz(client, message):
    """Start the quiz and send the first question."""
    if not quiz_data["questions"]:
        await message.reply("No questions are available to start the quiz. Add questions first!")
        return

    quiz_data["group_id"] = message.chat.id
    quiz_data["scores"].clear()
    quiz_data["current_question"] = 0

    await send_question(client)


@Client.on_message(filters.poll & filters.private)
async def add_question_via_poll(client, message):
    """
    Add a question using a poll sent in private chat.
    The poll must be a quiz with one correct answer.
    """
    poll = message.poll

    if not poll.type == Poll.QUIZ:
        await message.reply("Please send a quiz poll with a correct answer.")
        return

    if poll.correct_option_id is None:
        await message.reply("The quiz poll must have a correct answer set.")
        return

    # Add the question to the quiz database
    quiz_data["questions"].append({
        "question": poll.question,
        "options": [option.text for option in poll.options],
        "correct_option": poll.correct_option_id,
    })

    await message.reply("Question added successfully!")


async def send_question(client):
    """Send the current question as a poll."""
    question_data = quiz_data["questions"][quiz_data["current_question"]]
    poll_message = await client.send_poll(
        chat_id=quiz_data["group_id"],
        question=question_data["question"],
        options=question_data["options"],
        is_anonymous=False,
        type=Poll.QUIZ,
        correct_option_id=question_data["correct_option"],
    )
    # Map poll_id to the current question index
    quiz_data["poll_ids"][poll_message.poll.id] = quiz_data["current_question"]


@Client.on_raw_update()
async def handle_poll_answer(client, update, users, chats):
    """Handle raw updates to capture poll answers."""
    if update.get("poll_answer"):
        poll_answer = update.poll_answer
        poll_id = poll_answer.poll_id
        user_id = poll_answer.user_id
        selected_option = poll_answer.option_ids[0] if poll_answer.option_ids else None

        # Find the question index using poll_id
        question_index = quiz_data["poll_ids"].get(poll_id)
        if question_index is None:
            return  # Ignore if poll_id is not recognized

        question_data = quiz_data["questions"][question_index]

        # Initialize user's score if not already
        if user_id not in quiz_data["scores"]:
            quiz_data["scores"][user_id] = 0

        # Check if the answer is correct
        if selected_option == question_data["correct_option"]:
            quiz_data["scores"][user_id] += 1
        else:
            quiz_data["scores"][user_id] += NEGATIVE_MARKING

        # Move to the next question or end the quiz
        if quiz_data["current_question"] + 1 < len(quiz_data["questions"]):
            quiz_data["current_question"] += 1
            await send_question(client)
        else:
            await send_final_results(client)


async def send_final_results(client):
    """Send the final results to the group."""
    group_id = quiz_data["group_id"]
    scores = sorted(quiz_data["scores"].items(), key=lambda x: x[1], reverse=True)

    results = "**Quiz Results:**\n"
    for user_id, score in scores:
        user = await client.get_users(user_id)
        results += f"{user.first_name}: {score} points\n"

    await client.send_message(group_id, results)
            
