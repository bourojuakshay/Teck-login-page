import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Student CRUD App", layout="wide", initial_sidebar_state="expanded")

# ================= TITLE =================
st.title("📚 Student Management System")
st.markdown("---")

# ================= DB CONFIG =================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "VFFarmy@123"
DB_NAME = "Student_db"
DB_TABLE = "Student"

# ================= DB CONNECTION =================
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=True
        )
        return conn
    except Error as e:
        st.error(f"❌ Database connection error: {e}")
        return None

# ================= AUTO CREATE TABLE =================
def create_student_table():
    conn = get_db_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DB_TABLE} (
            id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT NOT NULL
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        st.error(f"❌ Error creating table: {e}")

# ================= QUERY FUNCTIONS =================
def execute_query(query, data=None):
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"❌ Query error: {e}")
        return False


def fetch_all_students():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {DB_TABLE}")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Error as e:
        st.error(f"❌ Fetch error: {e}")
        return []


def fetch_student_by_id(student_id):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {DB_TABLE} WHERE id=%s", (student_id,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        return data
    except Error as e:
        st.error(f"❌ Fetch error: {e}")
        return None

# ================= INIT =================
create_student_table()

# ================= SIDEBAR =================
st.sidebar.title("🎯 Navigation")
operation = st.sidebar.radio("Select Operation", ["📖 Read", "➕ Create", "✏️ Update", "❌ Delete"])

st.sidebar.markdown("---")
st.sidebar.info("Manage student records using CRUD operations")

# ================= READ =================
if operation == "📖 Read":
    st.header("📖 View Students")
    students = fetch_all_students()

    if students:
        df = pd.DataFrame(students)
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📊 Total Students: {len(students)}")
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
    else:
        st.warning("No students found")

    st.markdown("---")
    st.subheader("🔍 Search Student by ID")
    search_id = st.number_input("Enter Student ID", min_value=1, step=1)
    if st.button("Search"):
        student = fetch_student_by_id(search_id)
        if student:
            st.success("✅ Student Found")
            st.json(student)
        else:
            st.error("❌ Student not found")

# ================= CREATE =================
elif operation == "➕ Create":
    st.header("➕ Add Student")

    with st.form("create_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            student_id = st.number_input("ID", min_value=1, step=1)
        with col2:
            student_name = st.text_input("Name")
        with col3:
            student_age = st.number_input("Age", min_value=1, max_value=100, step=1)

        submit = st.form_submit_button("Add Student", use_container_width=True)

    if submit:
        if student_id and student_name and student_age:
            if fetch_student_by_id(student_id):
                st.error("❌ ID already exists")
            else:
                q = f"INSERT INTO {DB_TABLE} (id,name,age) VALUES(%s,%s,%s)"
                if execute_query(q, (student_id, student_name, student_age)):
                    st.success("✅ Student added")
                    st.balloons()
        else:
            st.warning("⚠ Fill all fields")

# ================= UPDATE =================
elif operation == "✏️ Update":
    st.header("✏️ Update Student")
    students = fetch_all_students()

    if students:
        ids = [s['id'] for s in students]
        sid = st.selectbox("Select ID", ids)
        student = fetch_student_by_id(sid)

        with st.form("update_form"):
            new_name = st.text_input("New Name", value=student['name'])
            new_age = st.number_input("New Age", min_value=1, max_value=100, value=student['age'])
            submit = st.form_submit_button("Update", use_container_width=True)

        if submit:
            q = f"UPDATE {DB_TABLE} SET name=%s, age=%s WHERE id=%s"
            if execute_query(q, (new_name, new_age, sid)):
                st.success("✅ Student updated")
                st.balloons()
    else:
        st.warning("No students available")

# ================= DELETE =================
elif operation == "❌ Delete":
    st.header("❌ Delete Student")
    students = fetch_all_students()

    if students:
        ids = [s['id'] for s in students]
        sid = st.selectbox("Select ID", ids)
        student = fetch_student_by_id(sid)

        st.warning(f"Delete student: {student['name']} (ID {sid})")

        if st.button("🗑 Delete", use_container_width=True):
            q = f"DELETE FROM {DB_TABLE} WHERE id=%s"
            if execute_query(q, (sid,)):
                st.success("✅ Student deleted")
                st.balloons()
    else:
        st.warning("No students to delete")

# ================= FOOTER =================
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:gray;'>
    <p>Student Management System | Streamlit + MySQL</p>
</div>
""", unsafe_allow_html=True)
