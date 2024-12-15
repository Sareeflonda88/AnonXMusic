import asyncio
import pickle
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, Poll
from AnonXMusic import app


ADMIN_IDS = [6644859358]  # Replace with your Telegram user ID(s)

# Load data (scores, quiz progress, and questions)
try:
    with open("data.pkl", "rb") as f:
        data = pickle.load(f)
except FileNotFoundError:
    data = {"scores": {}, "progress": {}, "questions": {}, "titles": {}, "time_limits": {}}

# Save data
def save_data():
    with open("data.pkl", "wb") as f:
        pickle.dump(data, f)

# Quiz Command with Title, Time, and Poll
@app.on_message(filters.command("quiz"))
async def quiz_command(client, message: Message):
    user_id = message.from_user.id

    # Step 1: Ask for the quiz title
    await message.reply("🎯 Let's start by setting a title for your quiz. Please send the quiz title:")
    try:
        title_message = await app.listen(message.chat.id, timeout=60)
        title = title_message.text
        data["titles"][user_id] = title
        data["questions"][user_id] = []
        save_data()
        await message.reply(f"✅ Quiz title set to: {title}\n\nNow, let's set a time limit for each question.")

        # Step 2: Ask for time limit
        await message.reply("⏱ Please specify the time limit for each question (in seconds, e.g., 30 for 30 seconds):")
        time_message = await app.listen(message.chat.id, timeout=60)

        if not time_message.text.isdigit():
            await message.reply("❌ Invalid input! The time limit must be a number. Operation canceled.")
            return

        time_limit = int(time_message.text)
        data["time_limits"][user_id] = time_limit
        save_data()
        await message.reply(f"✅ Time limit set to: {time_limit} seconds\n\nNow, let's add questions to your quiz.")

        # Step 3: Add questions using polls
        while True:
            await message.reply(
                "Send the question text as a poll with options.\n\n"
                "Once you're done adding all questions, send /done."
            )

            question_message = await app.listen(message.chat.id, timeout=300)

            # Handle the /done command
            if question_message.text and question_message.text.lower() == "/done":
                break

            # Check if the message contains a poll
            if question_message.poll:
                poll = question_message.poll
                question_text = poll.question
                options = poll.options
                correct_option_id = poll.correct_option_id

                # Store the question data
                data["questions"][user_id].append(
                    {
                        "question": question_text,
                        "options": [option.text for option in options],
                        "answer": correct_option_id,
                    }
                )
                save_data()
                await message.reply(f"✅ Question added: {question_text}")
            else:
                await message.reply("❌ Please send a valid poll with options.")
    except asyncio.TimeoutError:
        await message.reply("❌ Timeout! Operation canceled.")
        return

    # Step 4: Confirm quiz creation
    if data["questions"][user_id]:
        await message.reply(
            f"✅ Quiz '{data['titles'][user_id]}' created successfully with {len(data['questions'][user_id])} questions!"
            f"\n\nTime limit per question: {data['time_limits'][user_id]} seconds"
        )
    else:
        await message.reply("❌ No questions were added. Operation canceled.")
      



@app.on_message(filters.command("play_quiz"))
async def play_quiz(client, message: Message):
    user_id = message.from_user.id
    if user_id not in data["questions"] or not data["questions"][user_id]:
        await message.reply("❌ You haven't created any quizzes yet. Use /quiz to create one.")
        return

    questions = data["questions"][user_id]
    time_limit = data["time_limits"][user_id]
    score = 0

    for i, q in enumerate(questions):
        # Prepare poll options
        options = q["options"]
        correct_answer = q["answer"]
        
        # Send the poll to the user
        poll_message = await message.reply_poll(
            question=f"Question {i + 1}/{len(questions)}:\n{q['question']}",
            options=options,
            is_anonymous=False,  # Allows user to see who voted for what
            type="quiz",  # This will make the poll behave as a quiz
            correct_option_id=correct_answer,  # Set the correct answer
            explanation=f"The correct answer was option {correct_answer + 1}.",  # Explanation after poll
        )
        
        # Set a timeout for answering the poll
        try:
            # Wait for the user response within the time limit
            answer_message = await app.listen(message.chat.id, timeout=time_limit)
            if answer_message.text.isdigit():
                selected_option = int(answer_message.text) - 1
                if selected_option == correct_answer:
                    score += 4
                    await message.reply("✅ Correct! You earned +4 points.")
                else:
                    score -= 0.25
                    await message.reply(f"❌ Wrong! The correct answer was option {correct_answer + 1}. You lost 0.25 points.")
            else:
                await message.reply("❌ Invalid response! No points deducted.")
        except asyncio.TimeoutError:
            await message.reply("⏰ Time's up! Moving to the next question.")

    # Display final score
    await message.reply(f"🎉 Quiz completed! Your final score is: {score} points.")
      
