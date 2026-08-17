import streamlit as st
from supabase import create_client, Client
from datetime import date, timedelta
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# ============================================================
# PAGE CONFIG
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
# GEMINI
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
# PUBLIC PRIVACY POLICY PAGE
# ============================================================

query_params = st.query_params

if query_params.get("page") == "privacy":

    st.set_page_config(
        page_title="StudyPlanner Privacy Policy",
        page_icon="🔒",
        layout="centered"
    )

    st.title("🔒 StudyPlanner Privacy Policy")

    st.write("Last updated: August 17, 2026")

    st.markdown("""
## 1. About StudyPlanner

StudyPlanner is a study-planning application designed to help
students organize homework, exams, study information, and
study-related tasks.

## 2. Information We Store

Depending on the features you use, StudyPlanner may store:

- Your account email address
- Homework and assignment information
- Exam information and exam dates
- Your Study Profile, such as curriculum, board/country,
  class/grade, and school
- Information required to provide the features of the application

## 3. Google Account and Google Calendar

StudyPlanner provides an optional Google Calendar integration.

If you choose to connect Google Calendar, StudyPlanner requests
the Google permissions necessary to provide the Calendar features
you use.

For example, StudyPlanner may use Calendar access to add your
StudyPlanner homework or exams to your Google Calendar.

StudyPlanner does not use Google Calendar access to sell your
information or for advertising.

You can disconnect your Google account from StudyPlanner at any
time through the Google Calendar section of the application.

## 4. AI Study Assistant

StudyPlanner includes an AI study assistant.

When you use the AI assistant, information from your StudyPlanner
account may be used to provide personalized answers, such as your
study profile, homework, and upcoming exams.

The AI assistant is intended to help with studying and organization.

## 5. How We Use Information

Information is used to:

- Provide StudyPlanner features
- Save and display your homework and exams
- Personalize your study experience
- Provide the AI study assistant
- Provide Google Calendar integration when you choose to use it

We do not sell your personal information.

## 6. Data Security

We take reasonable measures to protect information stored by
StudyPlanner.

Access to account-specific information is intended to be limited
to the authenticated user associated with that information.

## 7. Third-Party Services

StudyPlanner may use third-party services to provide its features,
including:

- Supabase for authentication and data storage
- Google services for Google authentication and Google Calendar
- Google Gemini for AI-powered study assistance

Each service may have its own privacy policies and terms.

## 8. Your Choices

You can choose whether to connect Google Calendar.

You can also use StudyPlanner's account features to manage your
study information.

If you want your account or stored information removed, contact
the StudyPlanner developer using the contact information below.

## 9. Children's Privacy

StudyPlanner is intended to be used with appropriate parental or
guardian supervision where required by applicable law.

We do not knowingly request unnecessary personal information from
children.

## 10. Contact

If you have questions about this Privacy Policy or StudyPlanner's
handling of information, contact:

**StudyPlanner Developer**

Email: shfiullahc@gmail.com

## 11. Changes to This Privacy Policy

This Privacy Policy may be updated when StudyPlanner's features
or data practices change. The latest version will be made available
on this page.
""")

    st.divider()

    st.caption(
        "© 2026 StudyPlanner"
    )

    st.stop()

# ============================================================
# PUBLIC TERMS OF SERVICE PAGE
# ============================================================

if query_params.get("page") == "terms":

    st.set_page_config(
        page_title="StudyPlanner Terms of Service",
        page_icon="📜",
        layout="centered"
    )

    st.title("📜 StudyPlanner Terms of Service")

    st.write("Last updated: August 17, 2026")

    st.markdown("""
## 1. Acceptance of Terms

By using StudyPlanner, you agree to these Terms of Service.
If you do not agree with these terms, please do not use the
application.

## 2. About StudyPlanner

StudyPlanner is a study-planning application designed to help
students organize homework, exams, study information, and
study-related tasks.

## 3. Use of the Service

You agree to use StudyPlanner only for lawful purposes.

You are responsible for the information you enter into your
StudyPlanner account.

You should not attempt to access another user's account or data.

## 4. Account

Some StudyPlanner features require you to sign in.

You are responsible for keeping access to your account secure.

You should not share your account credentials with other people.

## 5. Google Calendar

StudyPlanner provides an optional Google Calendar integration.

If you connect Google Calendar, you authorize StudyPlanner to
use the Google permissions you approve to provide Calendar
features.

You can disconnect Google Calendar from your account at any time.

## 6. AI Study Assistant

StudyPlanner may provide AI-generated study assistance.

AI-generated information may contain mistakes and should be
reviewed by the user.

StudyPlanner should not be treated as a replacement for teachers,
schools, textbooks, or other educational resources.

## 7. Educational Use

StudyPlanner is intended to assist with studying and organization.

Users remain responsible for their own schoolwork, assignments,
and academic decisions.

## 8. Availability

We try to keep StudyPlanner available and working properly, but
we cannot guarantee that the service will always be available,
error-free, or uninterrupted.

Features may be changed, updated, or removed over time.

## 9. Third-Party Services

StudyPlanner may use third-party services, including:

- Supabase for authentication and data storage
- Google services for authentication and Google Calendar
- Google Gemini for AI-powered study assistance

These services have their own terms and policies.

## 10. Prohibited Activities

You must not:

- Attempt to gain unauthorized access to StudyPlanner
- Attempt to access another user's information
- Abuse or interfere with the service
- Use the service for illegal activities
- Intentionally submit malicious content

## 11. Termination

Access to StudyPlanner may be suspended or terminated if the
service is misused or these Terms are violated.

## 12. Changes to These Terms

These Terms of Service may be updated when StudyPlanner's
features or policies change.

The latest version will be available on this page.

## 13. Contact

If you have questions about these Terms of Service, contact:

**StudyPlanner Developer**

Email: shfiullahc@gmail.com
""")

    st.divider()

    st.caption("© 2026 StudyPlanner")

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ============================================================
# LOGIN
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
# CURRENT USER
# ============================================================

user = st.session_state.user


# ============================================================
# LOAD HOMEWORK
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


# ============================================================
# LOAD EXAMS
# ============================================================

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
# LOAD STUDY PROFILE
# ============================================================

try:

    profile_response = (
        supabase
        .table("study_profiles")
        .select("*")
        .eq("user_id", user.id)
        .limit(1)
        .execute()
    )

    study_profile_data = profile_response.data or []

    if study_profile_data:
        study_profile = study_profile_data[0]
    else:
        study_profile = None

except Exception:

    study_profile = None


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
# AI CONTEXT
# ============================================================

def build_ai_context():

    profile_context = {
        "curriculum": "",
        "board_country": "",
        "class_grade": "",
        "school": ""
    }

    if study_profile:

        profile_context = {
            "curriculum": study_profile.get(
                "curriculum",
                ""
            ),
            "board_country": study_profile.get(
                "board_country",
                ""
            ),
            "class_grade": study_profile.get(
                "class_grade",
                ""
            ),
            "school": study_profile.get(
                "school",
                ""
            )
        }

    homework_context = []

    for item in homework:

        homework_context.append(
            {
                "subject": item.get(
                    "subject",
                    ""
                ),
                "name": item.get(
                    "name",
                    ""
                ),
                "due_date": str(
                    item.get(
                        "due_date",
                        ""
                    )
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

    exam_context = []

    for exam in exams:

        exam_context.append(
            {
                "subject": exam.get(
                    "subject",
                    ""
                ),
                "exam_date": str(
                    exam.get(
                        "exam_date",
                        ""
                    )
                ),
                "topics": exam.get(
                    "topics",
                    ""
                )
            }
        )

    return (
        profile_context,
        homework_context,
        exam_context
    )


def create_ai_prompt(user_message):

    (
        profile_context,
        homework_context,
        exam_context
    ) = build_ai_context()

    today = date.today().isoformat()

    return f"""
You are StudyPlanner AI.

You are a personal study assistant for the
currently logged-in StudyPlanner user.

Today's date:
{today}

==================================================
STUDENT STUDY PROFILE
==================================================

Curriculum:
{profile_context["curriculum"]}

Board / Country:
{profile_context["board_country"]}

Class / Grade:
{profile_context["class_grade"]}

School:
{profile_context["school"]}

==================================================
STUDENT HOMEWORK
==================================================

{homework_context}

==================================================
STUDENT EXAMS
==================================================

{exam_context}

==================================================
IMPORTANT RULES
==================================================

1. Use the student's Study Profile to personalize
   your explanations.

2. Use their actual homework and exams when
   creating study plans.

3. If an exam is tomorrow or today, prioritize it.

4. Do not invent exam topics.

5. If the student's exam has no topics listed,
   tell them that the topics are not available.

6. Do not claim to know information that was not
   provided.

7. Never reveal passwords, API keys, tokens, or
   private authentication information.

8. Only use information belonging to the currently
   logged-in user.

9. Give clear explanations suitable for the
   student's class/grade.

10. If the student's curriculum or class is known,
    adapt the explanation to that level.

==================================================
USER QUESTION
==================================================

{user_message}

==================================================
ANSWER
==================================================

Give a helpful, clear and personalized answer.
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

    try:

        if google_connected():
            st.logout()

    except Exception:
        pass

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
        if item.get(
            "completed",
            False
        )
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

        if item.get(
            "completed",
            False
        ):
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
                                "due_date": str(
                                    due_date
                                ),
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

                if item.get(
                    "completed",
                    False
                ):

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
                        item.get(
                            "completed",
                            False
                        )
                    )
                )

                st.write(
                    f"🔥 {item.get('priority', 'Medium')}"
                )

            with right:

                if not item.get(
                    "completed",
                    False
                ):

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
                                "exam_date": str(
                                    exam_date
                                ),
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
        if item.get(
            "completed",
            False
        )
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

            if st.button(
                "🔄 Reconnect Google"
            ):

                st.logout()
                st.rerun()

        else:

            st.subheader(
                "📝 Add Homework"
            )

            available_homework = [
                item
                for item in homework
                if not item.get(
                    "completed",
                    False
                )
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
                    list(
                        homework_choices.keys()
                    ),
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
                    list(
                        exam_choices.keys()
                    ),
                    key="calendar_exam"
                )

                if st.button(
                    "📅 Add Exam to Calendar"
                ):

                    exam = exam_choices[
                        selected_exam
                    ]

                    try:

                        event = add_calendar_event(
                            service,
                            f"EXAM: {exam['subject']}",
                            exam["exam_date"],
                            (
                                f"Topics: "
                                f"{exam.get('topics', '')}"
                            )
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
# AI STUDY CHATBOT
# ============================================================

elif page == "🤖 Study Chatbot":

    st.title("🤖 StudyPlanner AI")

    st.write(
        "Your personal study assistant using your "
        "Study Profile, homework and exams."
    )

    st.divider()

    if gemini_client is None:

        st.error(
            "Gemini AI is not configured."
        )

        st.info(
            "Make sure GEMINI_API_KEY is in "
            "Streamlit Secrets."
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
        # CHAT HISTORY
        # ----------------------------------------------------

        for message in st.session_state.chat_messages:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )

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
        # GENERATE RESPONSE
        # ----------------------------------------------------

        if (
            st.session_state.chat_messages
            and
            st.session_state.chat_messages[-1]["role"]
            == "user"
        ):

            last_message = (
                st.session_state
                .chat_messages[-1]
                ["content"]
            )

            with st.chat_message("assistant"):

                with st.spinner(
                    "🤔 StudyPlanner AI is thinking..."
                ):

                    try:

                        prompt_text = create_ai_prompt(
                            last_message
                        )

                        response = (
                            gemini_client
                            .models
                            .generate_content(
                                model="gemini-3.1-flash-lite",
                                contents=prompt_text
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

    # ========================================================
    # STUDY PROFILE
    # ========================================================

    st.subheader("🎓 Study Profile")

    st.write(
        "Save your curriculum and education details "
        "so StudyPlanner AI can personalize your "
        "study help."
    )

    # Current values
    current_curriculum = ""

    current_board = ""

    current_class = ""

    current_school = ""

    if study_profile:

        current_curriculum = study_profile.get(
            "curriculum",
            ""
        )

        current_board = study_profile.get(
            "board_country",
            ""
        )

        current_class = study_profile.get(
            "class_grade",
            ""
        )

        current_school = study_profile.get(
            "school",
            ""
        )

    with st.form("study_profile_form"):

        curriculum = st.text_input(
            "📚 Curriculum / Education System",
            value=current_curriculum,
            placeholder="e.g. CBSE, ICSE, British Curriculum"
        )

        board_country = st.text_input(
            "🌍 Board / Country",
            value=current_board,
            placeholder="e.g. India, Saudi Arabia, UK"
        )

        class_grade = st.text_input(
            "🎓 Class / Grade",
            value=current_class,
            placeholder="e.g. Class 8, Grade 10"
        )

        school = st.text_input(
            "🏫 School (optional)",
            value=current_school,
            placeholder="Enter your school name"
        )

        save_profile = st.form_submit_button(
            "💾 Save Study Profile",
            use_container_width=True
        )

        if save_profile:

            if not curriculum.strip():

                st.error(
                    "Please enter your curriculum."
                )

            elif not board_country.strip():

                st.error(
                    "Please enter your board/country."
                )

            elif not class_grade.strip():

                st.error(
                    "Please enter your class/grade."
                )

            else:

                profile_values = {
                    "user_id": user.id,
                    "curriculum": curriculum.strip(),
                    "board_country": board_country.strip(),
                    "class_grade": class_grade.strip(),
                    "school": school.strip()
                }

                try:

                    if study_profile:

                        (
                            supabase
                            .table("study_profiles")
                            .update(profile_values)
                            .eq(
                                "user_id",
                                user.id
                            )
                            .execute()
                        )

                        st.success(
                            "✅ Study Profile updated!"
                        )

                    else:

                        (
                            supabase
                            .table("study_profiles")
                            .insert(profile_values)
                            .execute()
                        )

                        st.success(
                            "✅ Study Profile saved!"
                        )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not save Study Profile: {e}"
                    )

    st.divider()

    # ========================================================
    # ACCOUNT
    # ========================================================

    st.subheader("👤 Account")

    st.write(
        f"Email: **{user.email}**"
    )

    st.divider()

    # ========================================================
    # CHANGE PASSWORD
    # ========================================================

    st.subheader("🔐 Change Password")

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

                # Verify old password
                supabase.auth.sign_in_with_password(
                    {
                        "email": user.email,
                        "password": old_password
                    }
                )

                # Update password
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

    # ========================================================
    # PASSWORD RECOVERY
    # ========================================================

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