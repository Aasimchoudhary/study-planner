import streamlit as st
from supabase import create_client, Client
from datetime import date, timedelta
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="StudyPlanner",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# SUPABASE
# ============================================================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()


# ============================================================
# GEMINI AI
# ============================================================

@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


try:
    gemini_client = get_gemini_client()
except Exception:
    gemini_client = None


# ============================================================
# SESSION
# ============================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ============================================================
# LOGIN / SIGNUP
# ============================================================

if st.session_state.user is None:

    st.title("📚 StudyPlanner")
    st.subheader("Your personal study planner")

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Sign Up"]
    )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    with login_tab:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                try:

                    response = (
                        supabase.auth
                        .sign_in_with_password(
                            {
                                "email": email,
                                "password": password
                            }
                        )
                    )

                    st.session_state.user = response.user

                    st.success(
                        "Logged in successfully! 🎉"
                    )

                    st.rerun()

                except Exception:

                    st.error(
                        "Invalid login credentials."
                    )

    # --------------------------------------------------------
    # SIGN UP
    # --------------------------------------------------------

    with signup_tab:

        email = st.text_input(
            "Email",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm = st.text_input(
            "Confirm password",
            type="password",
            key="signup_confirm"
        )

        if st.button(
            "📝 Create Account",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                try:

                    supabase.auth.sign_up(
                        {
                            "email": email,
                            "password": password
                        }
                    )

                    st.success(
                        "Account created! 🎉"
                    )

                    st.info(
                        "You can now log in."
                    )

                except Exception as e:

                    st.error(
                        f"Signup error: {e}"
                    )

    st.stop()


# ============================================================
# USER
# ============================================================

user = st.session_state.user


# ============================================================
# DATA
# ============================================================

try:

    homework_response = (
        supabase
        .table("homework")
        .select("*")
        .eq("user_id", user.id)
        .order("due_date")
        .execute()
    )

    homework = homework_response.data or []

except Exception as e:

    st.error(
        f"Could not load homework: {e}"
    )

    homework = []


try:

    exams_response = (
        supabase
        .table("exams")
        .select("*")
        .eq("user_id", user.id)
        .order("exam_date")
        .execute()
    )

    exams = exams_response.data or []

except Exception as e:

    st.error(
        f"Could not load exams: {e}"
    )

    exams = []


# ============================================================
# HELPERS
# ============================================================

def homework_status(due_date, completed):

    if completed:
        return "✅ Completed"

    if isinstance(due_date, str):
        due_date = date.fromisoformat(due_date)

    days = (due_date - date.today()).days

    if days < 0:
        return f"🔴 Overdue by {abs(days)} day(s)"

    if days == 0:
        return "🔴 Due today"

    if days == 1:
        return "🟠 Due tomorrow"

    if days <= 3:
        return f"🟡 Due in {days} days"

    return f"🟢 Due in {days} days"


def exam_status(exam_date):

    if isinstance(exam_date, str):
        exam_date = date.fromisoformat(exam_date)

    days = (exam_date - date.today()).days

    if days < 0:
        return f"✅ Passed {abs(days)} day(s) ago"

    if days == 0:
        return "🔴 EXAM TODAY"

    if days == 1:
        return "🟠 EXAM TOMORROW"

    if days <= 3:
        return f"🟡 Exam in {days} days"

    return f"🟢 Exam in {days} days"


# ============================================================
# GOOGLE CALENDAR
# ============================================================

def google_connected():

    try:
        return bool(st.user.is_logged_in)
    except Exception:
        return False


def get_calendar_service():

    try:

        if not google_connected():
            return None

        access_token = st.user.tokens["access"]

        if not access_token:
            return None

        credentials = Credentials(
            token=access_token
        )

        return build(
            "calendar",
            "v3",
            credentials=credentials,
            cache_discovery=False
        )

    except Exception:

        return None


def add_calendar_event(
    service,
    title,
    event_date,
    description=""
):

    if isinstance(event_date, str):
        event_date = date.fromisoformat(event_date)

    end_date = event_date + timedelta(days=1)

    event = {
        "summary": title,
        "description": description,
        "start": {
            "date": event_date.isoformat()
        },
        "end": {
            "date": end_date.isoformat()
        }
    }

    return (
        service.events()
        .insert(
            calendarId="primary",
            body=event
        )
        .execute()
    )


# ============================================================
# CHATBOT HELPERS
# ============================================================

def build_study_context():

    homework_data = []

    for item in homework:

        homework_data.append(
            {
                "subject": item.get("subject", ""),
                "name": item.get("name", ""),
                "due_date": str(
                    item.get("due_date", "")
                ),
                "priority": item.get(
                    "priority",
                    "Medium"
                ),
                "completed": item.get(
                    "completed",
                    False
                )
            }
        )

    exam_data = []

    for exam in exams:

        exam_data.append(
            {
                "subject": exam.get(
                    "subject",
                    ""
                ),
                "exam_date": str(
                    exam.get("exam_date", "")
                ),
                "topics": exam.get(
                    "topics",
                    ""
                )
            }
        )

    return homework_data, exam_data


def create_ai_prompt(user_message):

    homework_data, exam_data = build_study_context()

    today = date.today().isoformat()

    return f"""
You are StudyPlanner AI, a personal study assistant.

Today's date is {today}.

You are helping the currently logged-in StudyPlanner user.

IMPORTANT PRIVACY RULES:
- Only use the homework and exam information supplied below.
- This information belongs only to the current logged-in user.
- Never reveal or guess information about another user.
- Never ask for passwords, API keys, or authentication tokens.
- Never reveal the Gemini API key.
- Do not claim that you accessed information that is not supplied here.

YOUR PURPOSE:
Help the student study effectively.

You can:
- Explain school subjects.
- Help prepare for exams.
- Create revision plans.
- Identify important topics.
- Make practice questions.
- Make quizzes.
- Help prioritize homework.
- Help organize study time.
- Explain difficult concepts step-by-step.
- Recommend what to study first.

EXAM PREPARATION:
If the user has an exam today or tomorrow:
1. Identify the relevant exam.
2. Look at its actual topics.
3. Prioritize those topics.
4. Give important concepts to revise.
5. Create a realistic study plan.
6. Offer practice questions or a quiz.

Do NOT invent exam topics.

If an exam has no topics listed, tell the student that the topics are not available in StudyPlanner and ask what topics they need help with.

HOMEWORK:
Use homework due dates and priorities when helping create study plans.

USER'S HOMEWORK:
{homework_data}

USER'S EXAMS:
{exam_data}

USER QUESTION:
{user_message}

Give a clear, helpful answer suitable for a student.
"""


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📚 StudyPlanner")

st.sidebar.write(
    f"👤 {user.email}"
)

page = st.sidebar.radio(
    "Menu",
    [
        "🏠 Dashboard",
        "📝 Homework",
        "📅 Exams",
        "📊 Progress",
        "📆 Google Calendar",
        "🤖 Study Chatbot",
        "⚙️ Account Settings"
    ]
)

st.sidebar.divider()

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.chat_messages = []

    if google_connected():
        st.logout()

    st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.title("🏠 Dashboard")

    total_homework = len(homework)

    completed_homework = sum(
        1
        for item in homework
        if item.get("completed", False)
    )

    remaining_homework = (
        total_homework -
        completed_homework
    )

    total_exams = len(exams)

    if total_homework > 0:

        progress = (
            completed_homework /
            total_homework
        )

    else:

        progress = 0

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "📝 Homework",
            total_homework
        )

    with c2:

        st.metric(
            "⏳ Remaining",
            remaining_homework
        )

    with c3:

        st.metric(
            "📅 Exams",
            total_exams
        )

    with c4:

        st.metric(
            "📊 Progress",
            f"{round(progress * 100)}%"
        )

    st.progress(progress)

    st.divider()

    st.subheader("⚠️ Upcoming")

    found = False

    for item in homework:

        if item.get("completed", False):
            continue

        status = homework_status(
            item["due_date"],
            False
        )

        if (
            "Overdue" in status
            or "today" in status
            or "tomorrow" in status
        ):

            found = True

            st.warning(
                f"📝 **{item['subject']}** — "
                f"{item['name']}  \n"
                f"{status}"
            )

    for exam in exams:

        status = exam_status(
            exam["exam_date"]
        )

        if (
            "TODAY" in status
            or "TOMORROW" in status
        ):

            found = True

            st.warning(
                f"📅 **{exam['subject']}** — "
                f"{status}"
            )

    if not found:

        st.success(
            "🎉 Nothing urgent!"
        )


# ============================================================
# HOMEWORK
# ============================================================

elif page == "📝 Homework":

    st.title("📝 Homework")

    with st.form("add_homework"):

        subject = st.text_input(
            "Subject"
        )

        name = st.text_input(
            "Homework name"
        )

        due_date = st.date_input(
            "Due date",
            value=date.today()
        )

        priority = st.selectbox(
            "Priority",
            [
                "Low",
                "Medium",
                "High"
            ]
        )

        submit = st.form_submit_button(
            "➕ Add Homework"
        )

        if submit:

            if not subject.strip():

                st.error(
                    "Enter a subject."
                )

            elif not name.strip():

                st.error(
                    "Enter homework name."
                )

            else:

                try:

                    (
                        supabase
                        .table("homework")
                        .insert(
                            {
                                "user_id": user.id,
                                "subject": subject,
                                "name": name,
                                "due_date": str(due_date),
                                "priority": priority,
                                "completed": False
                            }
                        )
                        .execute()
                    )

                    st.success(
                        "Homework added! 🎉"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not save homework: {e}"
                    )

    st.divider()

    if not homework:

        st.info(
            "No homework yet."
        )

    for item in homework:

        with st.container(border=True):

            left, middle, right = st.columns(
                [4, 3, 1]
            )

            with left:

                if item.get("completed", False):

                    st.markdown(
                        f"~~**{item['subject']} — "
                        f"{item['name']}**~~"
                    )

                else:

                    st.write(
                        f"**{item['subject']} — "
                        f"{item['name']}**"
                    )

            with middle:

                st.write(
                    f"📅 {item['due_date']}"
                )

                st.write(
                    homework_status(
                        item["due_date"],
                        item.get("completed", False)
                    )
                )

                st.write(
                    f"🔥 {item.get('priority', 'Medium')}"
                )

            with right:

                if not item.get("completed", False):

                    if st.button(
                        "✅",
                        key=f"complete_{item['id']}"
                    ):

                        (
                            supabase
                            .table("homework")
                            .update(
                                {
                                    "completed": True
                                }
                            )
                            .eq(
                                "id",
                                item["id"]
                            )
                            .eq(
                                "user_id",
                                user.id
                            )
                            .execute()
                        )

                        st.rerun()

                if st.button(
                    "🗑️",
                    key=f"delete_hw_{item['id']}"
                ):

                    (
                        supabase
                        .table("homework")
                        .delete()
                        .eq(
                            "id",
                            item["id"]
                        )
                        .eq(
                            "user_id",
                            user.id
                        )
                        .execute()
                    )

                    st.rerun()


# ============================================================
# EXAMS
# ============================================================

elif page == "📅 Exams":

    st.title("📅 Exams")

    with st.form("add_exam"):

        subject = st.text_input(
            "Subject"
        )

        exam_date = st.date_input(
            "Exam date",
            value=date.today()
        )

        topics = st.text_area(
            "Topics"
        )

        submit = st.form_submit_button(
            "➕ Add Exam"
        )

        if submit:

            if not subject.strip():

                st.error(
                    "Enter a subject."
                )

            else:

                try:

                    (
                        supabase
                        .table("exams")
                        .insert(
                            {
                                "user_id": user.id,
                                "subject": subject,
                                "exam_date": str(exam_date),
                                "topics": topics
                            }
                        )
                        .execute()
                    )

                    st.success(
                        "Exam added! 🎉"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not save exam: {e}"
                    )

    st.divider()

    if not exams:

        st.info(
            "No exams yet."
        )

    for exam in exams:

        with st.container(border=True):

            left, middle, right = st.columns(
                [3, 4, 1]
            )

            with left:

                st.subheader(
                    f"📚 {exam['subject']}"
                )

            with middle:

                st.write(
                    f"📅 {exam['exam_date']}"
                )

                st.write(
                    exam_status(
                        exam["exam_date"]
                    )
                )

                if exam.get("topics"):

                    st.write(
                        f"📖 {exam['topics']}"
                    )

            with right:

                if st.button(
                    "🗑️",
                    key=f"delete_exam_{exam['id']}"
                ):

                    (
                        supabase
                        .table("exams")
                        .delete()
                        .eq(
                            "id",
                            exam["id"]
                        )
                        .eq(
                            "user_id",
                            user.id
                        )
                        .execute()
                    )

                    st.rerun()


# ============================================================
# PROGRESS
# ============================================================

elif page == "📊 Progress":

    st.title("📊 Progress")

    total = len(homework)

    completed = sum(
        1
        for item in homework
        if item.get("completed", False)
    )

    if total:

        percentage = completed / total

    else:

        percentage = 0

    st.progress(percentage)

    st.write(
        f"### {completed} / {total} homework completed"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "📝 Total",
            total
        )

    with c2:

        st.metric(
            "✅ Completed",
            completed
        )

    with c3:

        st.metric(
            "⏳ Remaining",
            total - completed
        )

    if total and completed == total:

        st.success(
            "🎉 You completed everything!"
        )


# ============================================================
# GOOGLE CALENDAR
# ============================================================

elif page == "📆 Google Calendar":

    st.title("📆 Google Calendar")

    st.write(
        "Connect your Google account to add "
        "StudyPlanner homework and exams to "
        "your primary Google Calendar."
    )

    st.divider()

    if not google_connected():

        st.info(
            "Google Calendar is not connected."
        )

        if st.button(
            "🔗 Connect Google Calendar",
            use_container_width=True
        ):

            st.login("google")

    else:

        google_email = st.user.get(
            "email",
            "Google account"
        )

        st.success(
            f"🟢 Connected: {google_email}"
        )

        service = get_calendar_service()

        if service is None:

            st.error(
                "Google Calendar access token is unavailable."
            )

            st.write(
                "Try reconnecting your Google account."
            )

            if st.button(
                "🔄 Reconnect Google"
            ):

                st.logout()

                st.rerun()

        else:

            # ------------------------------------------------
            # HOMEWORK
            # ------------------------------------------------

            st.subheader(
                "📝 Add Homework"
            )

            available_homework = [
                item
                for item in homework
                if not item.get("completed", False)
            ]

            if available_homework:

                homework_choices = {
                    (
                        f"{item['subject']} — "
                        f"{item['name']} — "
                        f"{item['due_date']}"
                    ): item
                    for item in available_homework
                }

                selected_hw = st.selectbox(
                    "Select homework",
                    list(homework_choices.keys()),
                    key="calendar_homework"
                )

                if st.button(
                    "📅 Add Homework to Calendar"
                ):

                    item = homework_choices[
                        selected_hw
                    ]

                    try:

                        event = add_calendar_event(
                            service,
                            (
                                f"Homework: "
                                f"{item['subject']} — "
                                f"{item['name']}"
                            ),
                            item["due_date"],
                            (
                                f"Priority: "
                                f"{item.get('priority', 'Medium')}"
                            )
                        )

                        st.success(
                            "✅ Homework added to Google Calendar!"
                        )

                        if event.get("htmlLink"):

                            st.link_button(
                                "📅 Open Calendar Event",
                                event["htmlLink"]
                            )

                    except HttpError as e:

                        st.error(
                            f"Google Calendar error: {e}"
                        )

            else:

                st.info(
                    "No incomplete homework available."
                )

            st.divider()

            # ------------------------------------------------
            # EXAMS
            # ------------------------------------------------

            st.subheader(
                "📚 Add Exam"
            )

            if exams:

                exam_choices = {
                    (
                        f"{exam['subject']} — "
                        f"{exam['exam_date']}"
                    ): exam
                    for exam in exams
                }

                selected_exam = st.selectbox(
                    "Select exam",
                    list(exam_choices.keys()),
                    key="calendar_exam"
                )

                if st.button(
                    "📅 Add Exam to Calendar"
                ):

                    exam = exam_choices[
                        selected_exam
                    ]

                    description = (
                        f"Topics: "
                        f"{exam.get('topics', '')}"
                    )

                    try:

                        event = add_calendar_event(
                            service,
                            f"EXAM: {exam['subject']}",
                            exam["exam_date"],
                            description
                        )

                        st.success(
                            "✅ Exam added to Google Calendar!"
                        )

                        if event.get("htmlLink"):

                            st.link_button(
                                "📅 Open Calendar Event",
                                event["htmlLink"]
                            )

                    except HttpError as e:

                        st.error(
                            f"Google Calendar error: {e}"
                        )

            else:

                st.info(
                    "No exams available."
                )

            st.divider()

            if st.button(
                "🔌 Disconnect Google Calendar"
            ):

                st.logout()


# ============================================================
# STUDY CHATBOT - V3.2
# ============================================================

elif page == "🤖 Study Chatbot":

    st.title("🤖 StudyPlanner AI")

    st.write(
        "Your personal study assistant using your "
        "StudyPlanner homework and exams."
    )

    st.divider()

    if gemini_client is None:

        st.error(
            "Gemini AI is not configured correctly."
        )

        st.info(
            "Make sure GEMINI_API_KEY is present "
            "in Streamlit Secrets."
        )

    else:

        # ----------------------------------------------------
        # QUICK ACTIONS
        # ----------------------------------------------------

        st.subheader("⚡ Quick Help")

        q1, q2, q3 = st.columns(3)

        with q1:

            if st.button(
                "📅 What's coming up?",
                use_container_width=True
            ):

                st.session_state.chat_messages.append(
                    {
                        "role": "user",
                        "content":
                            "What homework and exams "
                            "do I have coming up?"
                    }
                )

        with q2:

            if st.button(
                "🎯 Help me prepare",
                use_container_width=True
            ):

                st.session_state.chat_messages.append(
                    {
                        "role": "user",
                        "content":
                            "Look at my upcoming exams "
                            "and help me decide what "
                            "I should study first."
                    }
                )

        with q3:

            if st.button(
                "🧠 Make me a quiz",
                use_container_width=True
            ):

                st.session_state.chat_messages.append(
                    {
                        "role": "user",
                        "content":
                            "Look at my most upcoming "
                            "exam and make me a practice "
                            "quiz based only on its topics."
                    }
                )

        # ----------------------------------------------------
        # DISPLAY CHAT HISTORY
        # ----------------------------------------------------

        for message in st.session_state.chat_messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )

        # ----------------------------------------------------
        # CHAT INPUT
        # ----------------------------------------------------

        prompt = st.chat_input(
            "Ask your StudyPlanner AI..."
        )

        if prompt:

            st.session_state.chat_messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

        # ----------------------------------------------------
        # PROCESS NEW MESSAGE
        # ----------------------------------------------------

        if (
            st.session_state.chat_messages
            and st.session_state.chat_messages[-1]["role"]
            == "user"
        ):

            last_message = (
                st.session_state.chat_messages[-1]
                ["content"]
            )

            # Prevent regenerating the same response
            # on every Streamlit rerun.
            if (
                len(st.session_state.chat_messages) == 1
                or st.session_state.chat_messages[-2]["role"]
                != "assistant"
            ):

                with st.chat_message("assistant"):

                    with st.spinner(
                        "🤔 StudyPlanner AI is thinking..."
                    ):

                        try:

                            current_prompt = (
                                create_ai_prompt(
                                    last_message
                                )
                            )

                            response = (
                                gemini_client
                                .models
                                .generate_content(
                                    model="gemini-3.1-flash-lite",
                                    contents=current_prompt
                                )
                            )

                            answer = (
                                response.text
                                if response.text
                                else
                                "I couldn't generate a response."
                            )

                            st.markdown(answer)

                            st.session_state.chat_messages.append(
                                {
                                    "role": "assistant",
                                    "content": answer
                                }
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"AI error: {e}"
                            )

        st.divider()

        if st.button(
            "🗑️ Clear Chat"
        ):

            st.session_state.chat_messages = []

            st.rerun()


# ============================================================
# ACCOUNT SETTINGS
# ============================================================

elif page == "⚙️ Account Settings":

    st.title("⚙️ Account Settings")

    st.subheader("👤 Account")

    st.write(
        f"Email: **{user.email}**"
    )

    st.divider()

    # --------------------------------------------------------
    # CHANGE PASSWORD
    # --------------------------------------------------------

    st.subheader("🔐 Change Password")

    st.info(
        "Enter your current password first."
    )

    old_password = st.text_input(
        "Current password",
        type="password",
        key="settings_old_password"
    )

    new_password = st.text_input(
        "New password",
        type="password",
        key="settings_new_password"
    )

    confirm_password = st.text_input(
        "Confirm new password",
        type="password",
        key="settings_confirm_password"
    )

    if st.button(
        "🔐 Change Password"
    ):

        if not old_password:

            st.error(
                "Enter your current password."
            )

        elif not new_password:

            st.error(
                "Enter a new password."
            )

        elif new_password != confirm_password:

            st.error(
                "New passwords do not match."
            )

        elif len(new_password) < 6:

            st.error(
                "New password must contain at least 6 characters."
            )

        elif new_password == old_password:

            st.error(
                "New password must be different."
            )

        else:

            try:

                # Verify old password first.
                supabase.auth.sign_in_with_password(
                    {
                        "email": user.email,
                        "password": old_password
                    }
                )

                # Change password.
                supabase.auth.update_user(
                    {
                        "password": new_password
                    }
                )

                st.success(
                    "✅ Password changed successfully!"
                )

            except Exception:

                st.error(
                    "❌ Current password is incorrect."
                )

    st.divider()

    # --------------------------------------------------------
    # PASSWORD RECOVERY
    # --------------------------------------------------------

    st.subheader(
        "📨 Password Recovery"
    )

    if st.button(
        "📨 Send Password Recovery Email"
    ):

        try:

            supabase.auth.reset_password_for_email(
                user.email
            )

            st.success(
                "📨 Password recovery email sent."
            )

        except Exception as e:

            st.error(
                f"Could not send recovery email: {e}"
            )

    st.divider()

    st.subheader("🚪 Session")

    st.write(
        "Use the Logout button in the sidebar "
        "to sign out of StudyPlanner."
    )