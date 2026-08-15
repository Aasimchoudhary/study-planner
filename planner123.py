import streamlit as st
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
# DATA
# =========================================================

if "homework" not in st.session_state:
    st.session_state.homework = []

if "exams" not in st.session_state:
    st.session_state.exams = []


# =========================================================
# SMART DATE FUNCTIONS
# =========================================================

def homework_status(due_date, completed):
    today = date.today()
    days = (due_date - today).days

    if completed:
        return "✅ Completed", "success"

    if days < 0:
        return f"🔴 OVERDUE by {abs(days)} day(s)", "error"

    if days == 0:
        return "🔴 DUE TODAY", "error"

    if days == 1:
        return "🟠 Due tomorrow", "warning"

    if days <= 3:
        return f"🟡 Due in {days} days", "warning"

    return f"🟢 Due in {days} days", "success"


def exam_status(exam_date):
    today = date.today()
    days = (exam_date - today).days

    if days < 0:
        return f"✅ Exam passed {abs(days)} day(s) ago", "success"

    if days == 0:
        return "🔴 EXAM TODAY!", "error"

    if days == 1:
        return "🟠 EXAM TOMORROW!", "warning"

    if days <= 3:
        return f"🟡 Exam in {days} days", "warning"

    return f"🟢 Exam in {days} days", "success"


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📚 StudyPlanner")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Dashboard",
        "📝 Homework",
        "📅 Exams",
        "📊 Progress"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.title("📚 StudyPlanner")
    st.write("Your smart homework and exam planner.")

    total_homework = len(st.session_state.homework)

    completed_homework = sum(
        1
        for task in st.session_state.homework
        if task["completed"]
    )

    remaining_homework = total_homework - completed_homework

    total_exams = len(st.session_state.exams)

    if total_homework > 0:
        progress = int(
            (completed_homework / total_homework) * 100
        )
    else:
        progress = 0

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # NEEDS ATTENTION
    # -----------------------------------------------------

    st.header("⚠️ Needs Attention")

    attention_found = False

    # Homework alerts

    for task in st.session_state.homework:

        if task["completed"]:
            continue

        status, status_type = homework_status(
            task["due"],
            task["completed"]
        )

        if status_type in ["error", "warning"]:

            attention_found = True

            st.warning(
                f"📝 **{task['subject']}** — "
                f"{task['name']}  \n"
                f"{status}"
            )

    # Exam alerts

    for exam in st.session_state.exams:

        status, status_type = exam_status(
            exam["date"]
        )

        if status_type in ["error", "warning"]:

            # Don't treat passed exams as urgent
            if "passed" not in status:

                attention_found = True

                st.warning(
                    f"📅 **{exam['subject']}** — "
                    f"{status}"
                )

    if not attention_found:

        st.success(
            "🎉 Nothing urgent! You're all caught up."
        )

    st.divider()

    # -----------------------------------------------------
    # HOMEWORK
    # -----------------------------------------------------

    st.header("📝 Homework")

    if not st.session_state.homework:

        st.info("No homework added yet.")

    else:

        for i, task in enumerate(
            st.session_state.homework
        ):

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

                    status, status_type = homework_status(
                        task["due"],
                        task["completed"]
                    )

                    st.write(f"📅 {task['due']}")
                    st.write(status)
                    st.write(
                        f"🔥 {task['priority']} priority"
                    )

                with col3:

                    if not task["completed"]:

                        if st.button(
                            "✅",
                            key=f"dash_complete_{i}"
                        ):

                            task["completed"] = True
                            st.rerun()

                    if st.button(
                        "🗑️",
                        key=f"dash_delete_{i}"
                    ):

                        st.session_state.homework.pop(i)
                        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # EXAMS
    # -----------------------------------------------------

    st.header("📅 Exams")

    if not st.session_state.exams:

        st.info("No exams added yet.")

    else:

        for i, exam in enumerate(
            st.session_state.exams
        ):

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 4, 1]
                )

                with col1:

                    st.write(
                        f"### 📚 {exam['subject']}"
                    )

                with col2:

                    status, status_type = exam_status(
                        exam["date"]
                    )

                    st.write(
                        f"📅 **{exam['date']}**"
                    )

                    st.write(status)

                    if exam["topics"]:
                        st.write(
                            f"📖 Topics: {exam['topics']}"
                        )

                with col3:

                    if st.button(
                        "🗑️",
                        key=f"dash_exam_delete_{i}"
                    ):

                        st.session_state.exams.pop(i)
                        st.rerun()


# =========================================================
# HOMEWORK PAGE
# =========================================================

elif page == "📝 Homework":

    st.title("📝 Homework")

    st.subheader("➕ Add Homework")

    with st.form("homework_form"):

        subject = st.text_input(
            "Subject",
            placeholder="Mathematics"
        )

        homework_name = st.text_input(
            "Homework",
            placeholder="Complete Chapter 5"
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

        add_homework = st.form_submit_button(
            "➕ Add Homework"
        )

        if add_homework:

            if not subject.strip():

                st.error(
                    "Please enter a subject."
                )

            elif not homework_name.strip():

                st.error(
                    "Please enter the homework."
                )

            else:

                st.session_state.homework.append(
                    {
                        "subject": subject,
                        "name": homework_name,
                        "due": due_date,
                        "priority": priority,
                        "completed": False
                    }
                )

                st.success(
                    "Homework added! 🎉"
                )

    st.divider()

    st.subheader("📋 Your Homework")

    if not st.session_state.homework:

        st.info(
            "You haven't added any homework yet."
        )

    else:

        for i, task in enumerate(
            st.session_state.homework
        ):

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

                    status, status_type = homework_status(
                        task["due"],
                        task["completed"]
                    )

                    st.write(
                        f"📅 Due: {task['due']}"
                    )

                    st.write(status)

                    st.write(
                        f"🔥 {task['priority']} priority"
                    )

                with col3:

                    if not task["completed"]:

                        if st.button(
                            "✅",
                            key=f"home_complete_{i}"
                        ):

                            task["completed"] = True
                            st.rerun()

                    if st.button(
                        "🗑️",
                        key=f"home_delete_{i}"
                    ):

                        st.session_state.homework.pop(i)
                        st.rerun()


# =========================================================
# EXAMS PAGE
# =========================================================

elif page == "📅 Exams":

    st.title("📅 Exam Planner")

    st.subheader("➕ Add Exam")

    with st.form("exam_form"):

        subject = st.text_input(
            "Subject",
            placeholder="Science"
        )

        exam_date = st.date_input(
            "Exam date",
            value=date.today()
        )

        topics = st.text_area(
            "Topics",
            placeholder=(
                "Cells, Genetics, Human Body"
            )
        )

        add_exam = st.form_submit_button(
            "➕ Add Exam"
        )

        if add_exam:

            if not subject.strip():

                st.error(
                    "Please enter the subject."
                )

            else:

                st.session_state.exams.append(
                    {
                        "subject": subject,
                        "date": exam_date,
                        "topics": topics
                    }
                )

                st.success(
                    "Exam added! 📚"
                )

    st.divider()

    st.subheader("📋 Your Exams")

    if not st.session_state.exams:

        st.info(
            "You haven't added any exams yet."
        )

    else:

        for i, exam in enumerate(
            st.session_state.exams
        ):

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [3, 4, 1]
                )

                with col1:

                    st.write(
                        f"### 📚 {exam['subject']}"
                    )

                with col2:

                    status, status_type = exam_status(
                        exam["date"]
                    )

                    st.write(
                        f"📅 {exam['date']}"
                    )

                    st.write(status)

                    if exam["topics"]:

                        st.write(
                            f"📖 {exam['topics']}"
                        )

                with col3:

                    if st.button(
                        "🗑️",
                        key=f"exam_delete_{i}"
                    ):

                        st.session_state.exams.pop(i)
                        st.rerun()


# =========================================================
# PROGRESS PAGE
# =========================================================

elif page == "📊 Progress":

    st.title("📊 Your Progress")

    total = len(
        st.session_state.homework
    )

    completed = sum(
        1
        for task in st.session_state.homework
        if task["completed"]
    )

    remaining = total - completed

    if total > 0:

        percentage = completed / total

    else:

        percentage = 0

    st.subheader("Homework Progress")

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

    st.subheader("📅 Exams")

    st.metric(
        "Total Exams",
        len(st.session_state.exams)
    )

    if total > 0 and completed == total:

        st.success(
            "🎉 You completed all your homework!"
        )

    elif total > 0:

        st.info(
            "💪 Keep going! You're making progress."
        )

    else:

        st.info(
            "Add some homework to start tracking "
            "your progress."
        )