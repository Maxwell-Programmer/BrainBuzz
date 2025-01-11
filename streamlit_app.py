import streamlit as st
import random
import time
from quiz_data import get_questions
from question_model import Question
from quiz_brain import QuizBrain

def get_random_light_color():
    """Generates a random light color in RGB format"""
    r = random.randint(200, 255)
    g = random.randint(200, 255)
    b = random.randint(200, 255)
    return f"rgb({r},{g},{b})"

def initialize_quiz():
    """Initializes the quiz with questions and sets state variables"""
    st.session_state.quiz_data = get_questions()

    if not st.session_state.quiz_data:
        st.error("No questions available. Please check the data source.")
        return

    question_bank = [
        Question(q['question'], q['incorrect_answers'] + [q['correct_answer']], q['correct_answer'])
        for q in st.session_state.quiz_data
    ]

    st.session_state.quiz = QuizBrain(question_bank)
    st.session_state.quiz.set_question_number(st.session_state.question_count)
    st.session_state.current_question = st.session_state.quiz.next_question()
    st.session_state.time_left = 30
    st.session_state.answered = False
    st.session_state.background_color = get_random_light_color()
    st.session_state.current_index = 0

def main():
    st.set_page_config(page_title="Neuroscience Quiz", page_icon="🧠")
    st.title("Brain Buzz")

    for key in ['quiz_started', 'question_count', 'quiz_data', 'current_index', 'quiz', 'timer_placeholder']:
        if key not in st.session_state:
            st.session_state[key] = None if key in ['quiz_data', 'quiz', 'timer_placeholder'] else False

    if not st.session_state.quiz_started:
        choose_question_count()
    else:
        if st.session_state.quiz is None:
            initialize_quiz()

        if st.session_state.quiz and st.session_state.quiz.has_questions():
            display_question()
        else:
            display_results()

def choose_question_count():
    """Displays a slider for the user to choose the number of quiz questions"""
    question_data = get_questions()
    max_questions = len(question_data)
    st.write(f"Total available questions: {max_questions}")

    question_count = st.slider(
        "Choose the number of questions:",
        min_value=1,
        max_value=min(max_questions, 100),
        step=1,
        value=10
    )

    if st.button("Start Quiz"):
        st.session_state.question_count = question_count
        st.session_state.quiz_started = True
        st.session_state.current_index = 0
        st.experimental_rerun()

def display_question():
    """Displays the current question and its answer choices"""
    set_background_color(st.session_state.background_color)

    st.write(f"Question {st.session_state.current_index + 1}/{st.session_state.question_count}")
    st.progress((st.session_state.current_index + 1) / st.session_state.question_count)
    st.write(st.session_state.current_question.text)

    # Create a placeholder for the timer
    if 'timer_placeholder' not in st.session_state:
        st.session_state.timer_placeholder = st.empty()

    # Display answer choices as buttons
    choice_buttons = []
    for i, choice in enumerate(st.session_state.current_question.choices):
        choice_buttons.append(st.button(choice, key=f"choice_{i}"))

    # Start the timer
    start_time = time.time()
    for remaining in range(30, 0, -1):
        if any(choice_buttons) or st.session_state.answered:
            break
        st.session_state.timer_placeholder.text(f"⏳ Time left: {remaining} seconds")
        time.sleep(1)
        if time.time() - start_time >= 30:
            st.session_state.timer_placeholder.text("⏰ Time's up!")
            check_answer(None)
            break

    # Check if any answer was selected
    for i, button_clicked in enumerate(choice_buttons):
        if button_clicked:
            check_answer(st.session_state.current_question.choices[i])
            break

    # Provide option to proceed to the next question
    if st.session_state.answered:
        if st.button("Next Question"):
            next_question()

def check_answer(user_answer):
    """Checks the user's answer and displays feedback"""
    st.session_state.answered = True
    if user_answer:
        is_correct = st.session_state.quiz.check_answer(user_answer)
        if is_correct:
            st.success("Correct!")
        else:
            st.error("Wrong!")
            st.write(f"The correct answer was: {st.session_state.quiz.get_correct_answer()}")
    else:
        st.error("Time's up!")
        st.write(f"The correct answer was: {st.session_state.quiz.get_correct_answer()}")

def next_question():
    """Loads the next question or marks the quiz as completed"""
    if st.session_state.quiz.has_questions():
        st.session_state.current_question = st.session_state.quiz.next_question()
        st.session_state.answered = False
        st.session_state.background_color = get_random_light_color()
        st.session_state.current_index += 1
        st.experimental_rerun()
    else:
        st.session_state.quiz_completed = True

def display_results():
    """Displays the final results of the quiz"""
    set_background_color("#FFFFFF")
    st.write("You've completed the quiz!")
    st.write(f"Your final score is: {st.session_state.quiz.score}/{st.session_state.question_count}")

    if st.button("Restart Quiz"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

def set_background_color(color):
    """Sets the background color of the app dynamically"""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
