import streamlit as st
from supabase import create_client, Client
from datetime import date

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="StudyPlanner",
    page_icon="📚",
    layout="wide"
)

# =========================================================
# SUPABASE CONNECTION
# =========================================================

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()

# =========================================================
# SESSION STATE
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = None


# =========================================================
# AUTHENTICATION
# =========================================================

if st.session_state.user is None:

    st.title("📚 StudyPlanner")
    st.subheader("Welcome!")

    login_tab, signup_tab = st.tabs(
        ["🔐 Log In", "👤 Create Account"]
    )

    # =====================================================
    # LOGIN
    # =====================================================

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
            "🔐 Log In",
            use_container_width=True
        ):

            if not email or not password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                try:

                    response = supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": password
                        }
                    )

                    st.session_state.user = response.user

                    st.success(
                        "Login successful! 🎉"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Login error: {e}"
                    )

    # =====================================================
    # SIGN UP
    # =====================================================

    with signup_tab:

        new_email = st.text_input(
            "Email",
            key="signup_email"
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            key="signup_confirm"
        )

        if st.button(
            "👤 Create Account",
            use_container_width=True
        ):

            if not new_email or not new_password:

                st.error(
                    "Please fill in all fields."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(new_password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            else:

                try:

                    response = supabase.auth.sign_up(
                        {
                            "email": new_email,
                            "password": new_password
                        }
                    )

                    st.success(
                        "Account created! 🎉"
                    )

                    st.info(
                        "Check your email if email confirmation "
                        "is enabled."
                    )

                except Exception as e:

                    st.error(
                        f"Signup error: {e}"
                    )

    st.stop()


# =========================================================
# CURRENT USER
# =========================================================

user = st.session_state.user


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📚 StudyPlanner")

st.sidebar.write(
    f"👤 {user.email}"
)

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Dashboard",
        "📝 Homework",
        "📅 Exams",
        "📊 Progress"
    ]
)

if st.sidebar.button(
    "🚪 Log Out",
    use_container_width=True
):

    supabase.auth.sign_out()

    st.session_state.user = None

    st.rerun()


# =========================================================
# SMART DATE FUNCTIONS
# =========================================================

def homework_status(due_date, completed):

    today = date.today()

    if isinstance(due_date, str):
        due_date = date.fromisoformat(due_date)

    days = (due_date - today).days

    if completed:
        return "✅ Completed"

    if days < 0:
        return f"🔴 OVERDUE by {abs(days)} day(s)"

    if days == 0:
        return "🔴 DUE TODAY"

    if days == 1:
        return "🟠 Due tomorrow"

    if days <= 3:
        return f"🟡 Due in {days} days"

    return f"🟢 Due in {days} days"


def exam_status(exam_date):

    today = date.today()

    if isinstance(exam_date, str):
        exam_date = date.fromisoformat(exam_date)

    days = (exam_date - today).days

    if days < 0:
        return f"✅ Exam passed {abs(days)} day(s) ago"

    if days == 0:
        return "🔴 EXAM TODAY!"

    if days == 1:
        return "🟠 EXAM TOMORROW!"

    if days <= 3:
        return f"🟡 Exam in {days} days"

    return f"🟢 Exam in {days} days"


# =========================================================
# GET USER DATA
# =========================================================

homework_response = (
    supabase
    .table("homework")
    .select("*")
    .eq("user_id", user.id)
    .order("due_date")
    .execute()
)

homework = homework_response.data


exams_response = (
    supabase
    .table("exams")
    .select("*")
    .eq("user_id", user.id)
    .order("exam_date")
    .execute()
)

exams = exams_response.data


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.title("📚 StudyPlanner")

    st.write(
        "Your personal homework and exam planner."
    )

    total_homework = len(homework)

    completed_homework = sum(
        1
        for task in homework
        if task["completed"]
    )

    remaining_homework = (
        total_homework - completed_homework
    )

    total_exams = len(exams)

    if total_homework > 0:

        progress = int(
            completed_homework /
            total_homework *
            100
        )

    else:

        progress = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📝 Homework",
            total_homework
        )

    with col2:

        st.metric(
            "⏳ Remaining",
            remaining_homework
        )

    with col3:

        st.metric(
            "📅 Exams",
            total_exams
        )

    with col4:

        st.metric(
            "📊 Progress",
            f"{progress}%"
        )

    st.divider()

    st.header("⚠️ Needs Attention")

    attention = False

    for task in homework:

        if task["completed"]:
            continue

        status = homework_status(
            task["due_date"],
            task["completed"]
        )

        if (
            "OVERDUE" in status
            or "TODAY" in status
            or "tomorrow" in status
        ):

            attention = True

            st.warning(
                f"📝 **{task['subject']}** — "
                f"{task['name']}  \n"
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

            attention = True

            st.warning(
                f"📅 **{exam['subject']}** — "
                f"{status}"
            )

    if not attention:

        st.success(
            "🎉 Nothing urgent!"
        )


# =========================================================
# HOMEWORK
# =========================================================

elif page == "📝 Homework":

    st.title("📝 Homework")

    st.subheader("➕ Add Homework")

    with st.form("homework_form"):

        subject = st.text_input(
            "Subject"
        )

        name = st.text_input(
            "Homework"
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
                    "Enter the homework."
                )

            else:

                try:

                    supabase.table(
                        "homework"
                    ).insert(
                        {
                            "user_id": user.id,
                            "subject": subject,
                            "name": name,
                            "due_date": str(due_date),
                            "priority": priority,
                            "completed": False
                        }
                    ).execute()

                    st.success(
                        "Homework saved! 💾"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not save homework: {e}"
                    )

    st.divider()

    st.subheader("📋 Your Homework")

    if not homework:

        st.info(
            "No homework yet."
        )

    else:

        for task in homework:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [4, 3, 1]
                )

                with col1:

                    if task["completed"]:

                        st.markdown(
                            f"~~**{task['subject']} — "
                            f"{task['name']}**~~"
                        )

                    else:

                        st.write(
                            f"**{task['subject']} — "
                            f"{task['name']}**"
                        )

                with col2:

                    st.write(
                        f"📅 {task['due_date']}"
                    )

                    st.write(
                        homework_status(
                            task["due_date"],
                            task["completed"]
                        )
                    )

                    st.write(
                        f"🔥 {task['priority']} priority"
                    )

                with col3:

                    if not task["completed"]:

                        if st.button(
                            "✅",
                            key=f"complete_{task['id']}"
                        ):

                            try:

                                supabase.table(
                                    "homework"
                                ).update(
                                    {
                                        "completed": True
                                    }
                                ).eq(
                                    "id",
                                    task["id"]
                                ).eq(
                                    "user_id",
                                    user.id
                                ).execute()

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"Could not update: {e}"
                                )

                    if st.button(
                        "🗑️",
                        key=f"delete_{task['id']}"
                    ):

                        try:

                            supabase.table(
                                "homework"
                            ).delete().eq(
                                "id",
                                task["id"]
                            ).eq(
                                "user_id",
                                user.id
                            ).execute()

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Could not delete: {e}"
                            )


# =========================================================
# EXAMS
# =========================================================

elif page == "📅 Exams":

    st.title("📅 Exam Planner")

    st.subheader("➕ Add Exam")

    with st.form("exam_form"):

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

                    supabase.table(
                        "exams"
                    ).insert(
                        {
                            "user_id": user.id,
                            "subject": subject,
                            "exam_date": str(exam_date),
                            "topics": topics
                        }
                    ).execute()

                    st.success(
                        "Exam saved! 💾"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not save exam: {e}"
                    )

    st.divider()

    st.subheader("📋 Your Exams")

    if not exams:

        st.info(
            "No exams yet."
        )

    else:

        for exam in exams:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 4, 1]
                )

                with col1:

                    st.write(
                        f"### 📚 {exam['subject']}"
                    )

                with col2:

                    st.write(
                        f"📅 {exam['exam_date']}"
                    )

                    st.write(
                        exam_status(
                            exam["exam_date"]
                        )
                    )

                    if exam["topics"]:

                        st.write(
                            f"📖 {exam['topics']}"
                        )

                with col3:

                    if st.button(
                        "🗑️",
                        key=f"delete_exam_{exam['id']}"
                    ):

                        try:

                            supabase.table(
                                "exams"
                            ).delete().eq(
                                "id",
                                exam["id"]
                            ).eq(
                                "user_id",
                                user.id
                            ).execute()

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Could not delete exam: {e}"
                            )


# =========================================================
# PROGRESS
# =========================================================

elif page == "📊 Progress":

    st.title("📊 Your Progress")

    total = len(homework)

    completed = sum(
        1
        for task in homework
        if task["completed"]
    )

    remaining = total - completed

    if total:

        percentage = completed / total

    else:

        percentage = 0

    st.subheader(
        "Homework Progress"
    )

    st.progress(
        percentage
    )

    st.write(
        f"**{completed} of {total} "
        f"homework tasks completed**"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📝 Total",
            total
        )

    with col2:

        st.metric(
            "✅ Completed",
            completed
        )

    with col3:

        st.metric(
            "⏳ Remaining",
            remaining
        )

    st.divider()

    st.subheader(
        "📅 Exams"
    )

    st.metric(
        "Total Exams",
        len(exams)
    )

    if total and completed == total:

        st.success(
            "🎉 You completed all your homework!"
        )

    elif total:

        st.info(
            "💪 Keep going!"
        )