import json
from pathlib import Path
from datetime import datetime
import uuid
import streamlit as st

DATA_PATH = Path(__file__).with_name("board.json")

st.set_page_config(page_title="Q&A Board", page_icon="💬", layout="wide")
st.title("💬 Q&A Board")
st.caption("Post questions and help others by replying. Data is stored locally in board.json next to this app.")


def load_data():
    if not DATA_PATH.exists():
        return {"threads": []}
    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"threads": []}


def save_data(data: dict):
    # Atomic-like write to reduce corruption risk
    tmp_path = DATA_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp_path.replace(DATA_PATH)


def new_thread(title: str, body: str, author: str):
    thread = {
        "id": uuid.uuid4().hex,
        "title": title.strip(),
        "body": body.strip(),
        "author": (author or "Anonymous").strip() or "Anonymous",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "replies": [],
    }
    data = load_data()
    data["threads"].insert(0, thread)  # newest first
    save_data(data)


def add_reply(thread_id: str, body: str, author: str):
    data = load_data()
    for t in data["threads"]:
        if t["id"] == thread_id:
            t["replies"].append(
                {
                    "id": uuid.uuid4().hex,
                    "body": body.strip(),
                    "author": (author or "Anonymous").strip() or "Anonymous",
                    "created_at": datetime.utcnow().isoformat() + "Z",
                }
            )
            break
    save_data(data)


# Sidebar: create a new question
with st.sidebar:
    st.header("Start a discussion")
    with st.form("new_thread_form", clear_on_submit=True):
        title = st.text_input("Title", help="Summarize your question")
        body = st.text_area("Question", height=140)
        author = st.text_input("Your name", placeholder="Optional")
        submitted = st.form_submit_button("Post Question")
    if submitted:
        if title.strip() and body.strip():
            new_thread(title, body, author)
            st.success("Question posted!")
            st.experimental_rerun()
        else:
            st.error("Please provide a title and question body.")


# Main: list threads and allow replies
data = load_data()
threads = data.get("threads", [])

if not threads:
    st.info("No questions yet. Be the first to post!")

for thread in threads:
    with st.expander(f"{thread['title']} — by {thread['author']}", expanded=False):
        st.write(thread["body"])  # question body
        st.caption(f"Posted {thread['created_at']}")

        # Replies list
        if thread["replies"]:
            st.subheader("Replies")
            for r in thread["replies"]:
                st.markdown(
                    f"- **{r['author']}**: {r['body']}\n\n"
                    f"  <span style='font-size:12px;color:gray'>— {r['created_at']}</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.write("No replies yet.")

        # Reply form
        with st.form(f"reply_form_{thread['id']}", clear_on_submit=True):
            reply_body = st.text_area("Your reply", height=120, key=f"rb_{thread['id']}")
            reply_author = st.text_input("Your name", placeholder="Optional", key=f"ra_{thread['id']}")
            reply_submit = st.form_submit_button("Reply")
        if reply_submit:
            if reply_body.strip():
                add_reply(thread["id"], reply_body, reply_author)
                st.success("Reply posted!")
                st.experimental_rerun()
            else:
                st.error("Reply cannot be empty.")
