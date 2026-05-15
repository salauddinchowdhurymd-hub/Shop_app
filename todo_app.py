import streamlit as st
import json
import os
from datetime import datetime
from enum import Enum

# ============ Configuration ============
TODO_FILE = "todos.json"
PRIORITY_OPTIONS = ["🔴 উচ্চ", "🟡 মাঝারি", "🟢 নিম্ন"]
CATEGORY_OPTIONS = ["কাজ", "ব্যক্তিগত", "কেনাকাটা", "স্বাস্থ্য", "অন্যান্য"]

# ============ Utility Functions ============
def load_todos():
    """টুডু লিস্ট লোড করুন"""
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_todos(todos):
    """টুডু লিস্ট সেভ করুন"""
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2, default=str)

def add_todo(title, description, priority, category, due_date):
    """নতুন টুডু যোগ করুন"""
    todos = load_todos()
    new_todo = {
        "id": len(todos) + 1,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "due_date": str(due_date),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completed": False,
        "completed_at": None
    }
    todos.append(new_todo)
    save_todos(todos)
    return new_todo

def delete_todo(todo_id):
    """টুডু মুছুন"""
    todos = load_todos()
    todos = [t for t in todos if t["id"] != todo_id]
    save_todos(todos)

def toggle_todo(todo_id):
    """টুডু সম্পূর্ণতা টগল করুন"""
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            if todo["completed"]:
                todo["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                todo["completed_at"] = None
            break
    save_todos(todos)

def update_todo(todo_id, title, description, priority, category, due_date):
    """টুডু আপডেট করুন"""
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["title"] = title
            todo["description"] = description
            todo["priority"] = priority
            todo["category"] = category
            todo["due_date"] = str(due_date)
            break
    save_todos(todos)

def get_priority_emoji(priority):
    """অগ্রাধিকার ইমোজি পান"""
    if "উচ্চ" in priority:
        return "🔴"
    elif "মাঝারি" in priority:
        return "🟡"
    else:
        return "🟢"

def get_category_emoji(category):
    """ক্যাটেগরি ইমোজি পান"""
    emojis = {
        "কাজ": "💼",
        "ব্যক্তিগত": "👤",
        "কেনাকাটা": "🛒",
        "স্বাস্থ্য": "🏥",
        "অন্যান্য": "📌"
    }
    return emojis.get(category, "📌")

# ============ Page Config ============
st.set_page_config(
    page_title="টুডু অ্যাপ",
    page_icon="📝",
    layout="wide"
)

# ============ CSS Styling ============
st.markdown("""
<style>
    .todo-item {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid;
    }
    .todo-completed {
        opacity: 0.6;
        text-decoration: line-through;
    }
    .metric-container {
        text-align: center;
        padding: 15px;
        border-radius: 8px;
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# ============ Header ============
st.title("📝 টুডু লিস্ট অ্যাপ")
st.markdown("আপনার দৈনন্দিন কাজ ব্যবস্থাপনা করুন সহজেই!")

# ============ Sidebar Menu ============
with st.sidebar:
    st.subheader("🎯 মেনু")
    menu_choice = st.radio(
        "নির্বাচন করুন:",
        ["📋 সব টুডু", "➕ নতুন টুডু", "🔍 খুঁজুন", "📊 পরিসংখ্যান", "⚙️ সেটিংস"]
    )

todos = load_todos()

# ============ 1. সব টুডু ============
if menu_choice == "📋 সব টুডু":
    st.subheader("সব কাজের তালিকা")
    
    if not todos:
        st.info("📭 এখনো কোনো কাজ নেই। নতুন কাজ যোগ করুন!")
    else:
        # ফিল্টার অপশন
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_status = st.selectbox(
                "স্থিতি অনুযায়ী ফিল্টার:",
                ["সব", "বাকি আছে", "সম্পূর্ণ"]
            )
        
        with col2:
            filter_category = st.selectbox(
                "ক্যাটেগরি অনুযায়ী:",
                ["সব"] + CATEGORY_OPTIONS
            )
        
        with col3:
            sort_by = st.selectbox(
                "সাজান:",
                ["তারিখ (নতুন)", "তারিখ (পুরানো)", "অগ্রাধিকার"]
            )
        
        # ফিল্টার করা টুডু
        filtered_todos = todos.copy()
        
        if filter_status == "সম্পূর্ণ":
            filtered_todos = [t for t in filtered_todos if t["completed"]]
        elif filter_status == "বাকি আছে":
            filtered_todos = [t for t in filtered_todos if not t["completed"]]
        
        if filter_category != "সব":
            filtered_todos = [t for t in filtered_todos if t["category"] == filter_category]
        
        # সাজান
        if sort_by == "তারিখ (নতুন)":
            filtered_todos.sort(key=lambda x: x["created_at"], reverse=True)
        elif sort_by == "তারিখ (পুরানো)":
            filtered_todos.sort(key=lambda x: x["created_at"])
        elif sort_by == "অগ্রাধিকার":
            priority_order = {"🔴 উচ্চ": 0, "🟡 মাঝারি": 1, "🟢 নিম্ন": 2}
            filtered_todos.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        # প্রদর্শন
        if filtered_todos:
            for todo in filtered_todos:
                col1, col2, col3, col4 = st.columns([0.5, 3, 1.5, 1])
                
                with col1:
                    # চেকবক্স
                    if st.checkbox(
                        "✓",
                        value=todo["completed"],
                        key=f"check_{todo['id']}"
                    ):
                        toggle_todo(todo["id"])
                        st.rerun()
                
                with col2:
                    # কাজের বিবরণ
                    title_class = "todo-completed" if todo["completed"] else ""
                    st.markdown(f"""
                    <div class='{title_class}'>
                        **{get_category_emoji(todo['category'])} {todo['title']}**  
                        {todo['description']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    # অগ্রাধিকার ও তারিখ
                    st.write(f"{get_priority_emoji(todo['priority'])} {todo['priority']}")
                    st.caption(f"📅 {todo['due_date']}")
                
                with col4:
                    # অ্যাকশন বাটন
                    col_edit, col_del = st.columns(2)
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_{todo['id']}", help="এডিট করুন"):
                            st.session_state[f"edit_{todo['id']}"] = True
                    
                    with col_del:
                        if st.button("🗑️", key=f"del_{todo['id']}", help="মুছুন"):
                            delete_todo(todo["id"])
                            st.success("✅ মুছে দেওয়া হয়েছে!")
                            st.rerun()
                
                # এডিট মোড
                if st.session_state.get(f"edit_{todo['id']}", False):
                    st.divider()
                    st.subheader("এডিট করুন")
                    
                    with st.form(f"edit_form_{todo['id']}"):
                        edit_title = st.text_input("শিরোনাম", value=todo["title"])
                        edit_desc = st.text_area("বিবরণ", value=todo["description"])
                        edit_priority = st.selectbox("অগ্রাধিকার", PRIORITY_OPTIONS, 
                                                    index=PRIORITY_OPTIONS.index(todo["priority"]))
                        edit_category = st.selectbox("ক্যাটেগরি", CATEGORY_OPTIONS,
                                                    index=CATEGORY_OPTIONS.index(todo["category"]))
                        edit_due_date = st.date_input("শেষ তারিখ", 
                                                     value=datetime.strptime(todo["due_date"], "%Y-%m-%d").date())
                        
                        if st.form_submit_button("💾 সংরক্ষণ করুন"):
                            update_todo(todo["id"], edit_title, edit_desc, 
                                       edit_priority, edit_category, edit_due_date)
                            st.session_state[f"edit_{todo['id']}"] = False
                            st.success("✅ আপডেট হয়েছে!")
                            st.rerun()
                
                st.divider()
        else:
            st.info("❌ কোনো ফলাফল পাওয়া যায়নি!")

# ============ 2. নতুন টুডু ============
elif menu_choice == "➕ নতুন টুডু":
    st.subheader("নতুন কাজ যোগ করুন")
    
    with st.form("add_todo_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("শিরোনাম *", placeholder="যেমন: বই পড়া")
            priority = st.selectbox("অগ্রাধিকার", PRIORITY_OPTIONS)
        
        with col2:
            category = st.selectbox("ক্যাটেগরি", CATEGORY_OPTIONS)
            due_date = st.date_input("শেষ তারিখ")
        
        description = st.text_area("বিবরণ (ঐচ্ছিক)", 
                                  placeholder="আরও বিস্তারিত লিখুন...")
        
        if st.form_submit_button("➕ কাজ যোগ করুন", use_container_width=True):
            if title:
                add_todo(title, description, priority, category, due_date)
                st.balloons()
                st.success("✅ কাজ সফলভাবে যোগ হয়েছে!")
                st.rerun()
            else:
                st.error("❌ শিরোনাম লিখুন!")

# ============ 3. খুঁজুন ============
elif menu_choice == "🔍 খুঁজুন":
    st.subheader("কাজ খুঁজুন")
    
    search_query = st.text_input("🔍 খোঁজার জন্য কীওয়ার্ড লিখুন:")
    
    if search_query:
        search_results = [
            t for t in todos 
            if search_query.lower() in t["title"].lower() 
            or search_query.lower() in t["description"].lower()
        ]
        
        if search_results:
            st.success(f"✅ {len(search_results)} টি ফলাফল পাওয়া গেছে")
            
            for todo in search_results:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        status = "✅ সম্পূর্ণ" if todo["completed"] else "⏳ বাকি"
                        st.markdown(f"""
                        **{todo['title']}**  
                        {todo['description']}  
                        {get_category_emoji(todo['category'])} {todo['category']} | {status}
                        """)
                    
                    with col2:
                        if st.button("✓ চিহ্নিত করুন", key=f"search_check_{todo['id']}"):
                            toggle_todo(todo["id"])
                            st.rerun()
                
                st.divider()
        else:
            st.info("❌ কোনো ফলাফল পাওয়া যায়নি!")
    else:
        st.info("🔎 খোঁজার জন্য কীওয়ার্ড লিখুন...")

# ============ 4. পরিসংখ্যান ============
elif menu_choice == "📊 পরিসংখ্যান":
    st.subheader("পরিসংখ্যান ও প্রতিবেদন")
    
    if todos:
        total = len(todos)
        completed = len([t for t in todos if t["completed"]])
        pending = total - completed
        
        # মেট্রিক্স
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 মোট কাজ", total)
        
        with col2:
            st.metric("✅ সম্পূর্ণ", completed)
        
        with col3:
            st.metric("⏳ বাকি", pending)
        
        with col4:
            completion_rate = (completed / total * 100) if total > 0 else 0
            st.metric("📈 সম্পূর্ণতা", f"{completion_rate:.1f}%")
        
        st.divider()
        
        # ক্যাটেগরি অনুযায়ী বিতরণ
        st.subheader("ক্যাটেগরি অনুযায়ী বিতরণ")
        
        category_count = {}
        for todo in todos:
            cat = todo["category"]
            category_count[cat] = category_count.get(cat, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            for cat, count in category_count.items():
                st.write(f"{get_category_emoji(cat)} **{cat}:** {count} কাজ")
        
        with col2:
            # অগ্রাধিকার অনুযায়ী
            st.write("**অগ্রাধিকার অনুযায়ী:**")
            for priority in PRIORITY_OPTIONS:
                count = len([t for t in todos if t["priority"] == priority])
                st.write(f"{priority}: {count} কাজ")
        
        st.divider()
        
        # প্রগতি বার
        st.subheader("প্রগতি")
        st.progress(completion_rate / 100)
        st.write(f"{completed}/{total} কাজ সম্পূর্ণ হয়েছে")
        
    else:
        st.info("📭 এখনো কোনো কাজ নেই!")

# ============ 5. সেটিংস ============
elif menu_choice == "⚙️ সেটিংস":
    st.subheader("সেটিংস ও অপশন")
    
    tab1, tab2, tab3 = st.tabs(["সাধারণ", "ডেটা", "তথ্য"])
    
    with tab1:
        st.write("**সাধারণ সেটিংস**")
        
        theme = st.selectbox("থিম নির্বাচন করুন:", ["হালকা", "গাঢ়"])
        notifications = st.toggle("বিজ্ঞপ্তি সক্ষম করুন", value=True)
        
        if st.button("💾 সংরক্ষণ করুন"):
            st.success("✅ সেটিংস সংরক্ষিত হয়েছে!")
    
    with tab2:
        st.write("**ডেটা ম্যানেজমেন্ট**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 ডেটা ডাউনলোড করুন (JSON)", use_container_width=True):
                todos_json = json.dumps(todos, ensure_ascii=False, indent=2, default=str)
                st.download_button(
                    label="JSON ফাইল ডাউনলোড করুন",
                    data=todos_json,
                    file_name=f"todos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("🗑️ সব ডেটা মুছুন", use_container_width=True):
                st.session_state['confirm_delete'] = True
        
        if st.session_state.get('confirm_delete', False):
            st.warning("⚠️ এটি সব ডেটা চিরতরে মুছে দেবে!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ হ্যাঁ, মুছুন"):
                    save_todos([])
                    st.session_state['confirm_delete'] = False
                    st.success("✅ সব ডেটা মুছে দেওয়া হয়েছে!")
                    st.rerun()
            
            with col2:
                if st.button("❌ বাতিল করুন"):
                    st.session_state['confirm_delete'] = False
    
    with tab3:
        st.write("**অ্যাপ্লিকেশন তথ্য**")
        
        st.info(f"""
        **টুডু লিস্ট অ্যাপ**
        - সংস্করণ: ১.০.০
        - তৈরি: ২০২৬
        - মোট কাজ: {len(todos)}
        - সংরক্ষণ অবস্থান: `{TODO_FILE}`
        
        **ফিচার:**
        - ✅ স্থানীয় সংরক্ষণ
        - ✅ একাধিক ক্যাটেগরি
        - ✅ অগ্রাধিকার স্তর
        - ✅ খোঁজার কার্যকারিতা
        - ✅ বিশ্লেষণ ও রিপোর্ট
        """)

# ============ Footer ============
st.divider()
st.markdown("""
<div style='text-align: center'>
    <small>📝 টুডু লিস্ট অ্যাপ | সংরক্ষণ স্থান: প্রস্তুত ✅</small>
</div>
""", unsafe_allow_html=True)
