"""
Simple To-Do List app built with Streamlit + HuggingFace Inference API.
The AI tool suggests task priority (Low/Medium/High) using a free HuggingFace model.
Deploy: Streamlit Community Cloud or Replit.
"""

import streamlit as st
import sqlite3
from datetime import datetime
import requests

# -------- Database helpers --------
DB_PATH = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            notes TEXT,
            priority TEXT DEFAULT 'Medium',
            done INTEGER DEFAULT 0,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def add_task(title, notes, priority):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (title, notes, priority, created_at) VALUES (?, ?, ?, ?)",
        (title, notes, priority, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_tasks(show_done=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if show_done:
        c.execute("SELECT id, title, notes, priority, done FROM tasks ORDER BY done, priority DESC, created_at DESC")
    else:
        c.execute("SELECT id, title, notes, priority, done FROM tasks WHERE done=0 ORDER BY priority DESC, created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def set_done(task_id, done=1):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE tasks SET done=? WHERE id=?", (done, task_id))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def update_priority(task_id, priority):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE tasks SET priority=? WHERE id=?", (priority, task_id))
    conn.commit()
    conn.close()

# -------- AI helper (HuggingFace) --------
HF_MODEL = "facebook/bart-large-mnli"  # zero-shot classification model
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# Works without API key for light usage; set HUGGINGFACEHUB_API_TOKEN for reliability.
headers = {}
try:
    import os
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
except Exception:
    pass


def ai_suggest_priority(title, notes=''):
    """Return 'Low', 'Medium', or 'High' using HuggingFace zero-shot classification."""
    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={
                "inputs": f"Task: {title}. Notes: {notes}",
                "parameters": {"candidate_labels": ["Low", "Medium", "High"]},
            },
            timeout=10,
        )
        data = response.json()
        if "labels" in data:
            return data["labels"][0]
    except Exception:
        pass
    return "Medium"

# -------- Streamlit UI --------

st.set_page_config(page_title="AI To-Do List", page_icon="🗒️")
init_db()

st.title("🗒️ To-Do List — AI priority suggestion")
st.write("Add tasks, mark them done, delete, and let AI suggest priority (powered by HuggingFace).")

with st.expander("➕ Add a new task"):
    col1, col2 = st.columns([3,1])
    title = col1.text_input("Task title")
    priority_select = col2.selectbox("Priority", ['Low','Medium','High'])
    notes = st.text_area("Notes (optional)")
    ai_button = st.button("Suggest priority with AI")
    if ai_button and title:
        suggested = ai_suggest_priority(title, notes)
        st.success(f"Suggested priority: {suggested}")
        priority_select = suggested
    if st.button("Add task") and title:
        add_task(title, notes, priority_select)
        st.success("Task added!")

st.markdown("---")

show_done = st.checkbox("Show completed tasks", value=False)
rows = get_tasks(show_done=show_done)

if not rows:
    st.info("No tasks found — add a task above.")
else:
    for r in rows:
        task_id, t_title, t_notes, t_priority, t_done = r
        cols = st.columns([0.05, 1, 2, 0.3, 0.3])
        done_chk = cols[0].checkbox("", value=bool(t_done), key=f"done_{task_id}")
        cols[1].markdown(f"**{t_title}**")
        cols[2].markdown(t_notes or "_no notes_")
        cols[3].selectbox("Priority", options=['Low','Medium','High'], index=['Low','Medium','High'].index(t_priority), key=f"pri_{task_id}")
        if cols[4].button("Delete", key=f"del_{task_id}"):
            delete_task(task_id)
            st.experimental_rerun()
        # handle changes
        if done_chk != bool(t_done):
            set_done(task_id, 1 if done_chk else 0)
            st.experimental_rerun()
        # priority update
        new_pri = st.session_state.get(f"pri_{task_id}", t_priority)
        if new_pri != t_priority:
            update_priority(task_id, new_pri)
            st.experimental_rerun()

st.markdown("---")
st.write("**Tip:** HuggingFace model suggests priority. You can override it manually.")

