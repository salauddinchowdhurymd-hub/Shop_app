import streamlit as st
import json
import os
from datetime import datetime
import hashlib

# ============ Config ============
SHOP_FILE = "shops.json"
USERS_FILE = "users.json"

# ============ Load/Save Functions ============
def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ============ Page Config ============
st.set_page_config(
    page_title="দোকান অ্যাপ",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ Initialize Users ============
users = load_json(USERS_FILE)
if not users:
    users = {
        "দোকান१": {"password": hash_password("pass1"), "name": "দোকান१"},
        "দোকান२": {"password": hash_password("pass2"), "name": "দোকান२"}
    }
    save_json(USERS_FILE, users)

# ============ Authentication ============
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.current_shop = None

if not st.session_state.authenticated:
    st.title("🛍️ দোকান অ্যাপ - লগইন")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### লগইন করুন")
        
        shop_name = st.selectbox("দোকানের নাম নির্বাচন করুন:", list(users.keys()))
        password = st.text_input("পাসওয়ার্ড লিখুন:", type="password")
        
        if st.button("লগইন করুন", use_container_width=True):
            if shop_name in users:
                if hash_password(password) == users[shop_name]["password"]:
                    st.session_state.authenticated = True
                    st.session_state.current_shop = shop_name
                    st.success("✅ লগইন সফল!")
                    st.rerun()
                else:
                    st.error("❌ পাসওয়ার্ড ভুল!")
            else:
                st.error("❌ দোকান খুঁজে পাওয়া যায়নি!")
    
    st.stop()

# ============ Main App ============
st.sidebar.title(f"🛍️ {st.session_state.current_shop}")

if st.sidebar.button("🚪 লগ আউট", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.current_shop = None
    st.rerun()

# Load shop data
shops = load_json(SHOP_FILE)
current_shop = st.session_state.current_shop

if current_shop not in shops:
    shops[current_shop] = {
        "transactions": [],
        "customers": {},
        "suppliers": {},
        "wallet": 0
    }

# ============ Sidebar Menu ============
menu = st.sidebar.radio(
    "নেভিগেশন:",
    ["📊 ড্যাশবোর্ড", "💰 লেনদেন", "👥 কাস্টমার", "🤝 মহাজন", "🏦 ওয়ালেট", "📈 রিপোর্ট", "⚙️ সেটিংস"]
)

# ============ 1. Dashboard ============
if menu == "📊 ড্যাশবোর্ড":
    st.title("📊 ড্যাশবোর্ড")
    
    data = shops[current_shop]
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_transactions = len(data["transactions"])
    total_customers = len(data["customers"])
    total_suppliers = len(data["suppliers"])
    wallet_balance = data["wallet"]
    
    with col1:
        st.metric("📝 মোট লেনদেন", total_transactions)
    with col2:
        st.metric("👥 কাস্টমার", total_customers)
    with col3:
        st.metric("🤝 মহাজন", total_suppliers)
    with col4:
        st.metric("💵 ওয়ালেট", f"৳{wallet_balance}")
    
    st.divider()
    st.success("✅ সব কিছু চলছে ঠিকঠাক!")

# ============ 2. Transactions ============
elif menu == "💰 লেনদেন":
    st.title("💰 লেনদেন")
    
    data = shops[current_shop]
    
    with st.form("add_transaction"):
        col1, col2 = st.columns(2)
        
        with col1:
            trans_type = st.selectbox("ধরণ:", ["আয়", "খরচ"])
            amount = st.number_input("পরিমাণ:", min_value=0, step=100)
        
        with col2:
            category = st.selectbox("ক্যাটেগরি:", ["বিক্রয়", "কেনাকাটা", "খরচ", "অন্যান্য"])
            description = st.text_input("বিবরণ:")
        
        if st.form_submit_button("➕ যোগ করুন", use_container_width=True):
            data["transactions"].append({
                "type": trans_type,
                "amount": amount,
                "category": category,
                "description": description,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Update wallet
            if trans_type == "আয়":
                data["wallet"] += amount
            else:
                data["wallet"] -= amount
            
            save_json(SHOP_FILE, shops)
            st.success("✅ লেনদেন যোগ হয়েছে!")
            st.rerun()
    
    st.divider()
    
    if data["transactions"]:
        st.subheader("সাম্প্রতিক লেনদেন")
        for trans in reversed(data["transactions"][-10:]):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{trans['description']}** ({trans['category']})")
                with col2:
                    color = "🟢" if trans['type'] == "আয়" else "🔴"
                    st.write(f"{color} {trans['type']}: ৳{trans['amount']}")
                with col3:
                    st.caption(trans['date'])
            st.divider()

# ============ 3. Customers ============
elif menu == "👥 কাস্টমার":
    st.title("👥 কাস্টমার")
    
    data = shops[current_shop]
    
    with st.form("add_customer"):
        col1, col2 = st.columns(2)
        
        with col1:
            cust_name = st.text_input("নাম:")
            cust_phone = st.text_input("ফোন:")
        
        with col2:
            cust_balance = st.number_input("বাকি পরিমাণ:", min_value=0)
            cust_note = st.text_input("নোট:")
        
        if st.form_submit_button("➕ কাস্টমার যোগ করুন", use_container_width=True):
            if cust_name:
                data["customers"][cust_name] = {
                    "phone": cust_phone,
                    "balance": cust_balance,
                    "note": cust_note,
                    "created": datetime.now().strftime("%Y-%m-%d")
                }
                save_json(SHOP_FILE, shops)
                st.success("✅ কাস্টমার যোগ হয়েছে!")
                st.rerun()
            else:
                st.error("❌ নাম লিখুন!")
    
    st.divider()
    
    if data["customers"]:
        st.subheader("কাস্টমার লিস্ট")
        for name, info in data["customers"].items():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{name}**")
                    st.caption(f"📞 {info['phone']}")
                with col2:
                    st.write(f"বাকি: ৳{info['balance']}")
                with col3:
                    if st.button("🗑️", key=f"del_cust_{name}"):
                        del data["customers"][name]
                        save_json(SHOP_FILE, shops)
                        st.rerun()
            st.divider()

# ============ 4. Suppliers ============
elif menu == "🤝 মহাজন":
    st.title("🤝 মহাজন")
    
    data = shops[current_shop]
    
    with st.form("add_supplier"):
        col1, col2 = st.columns(2)
        
        with col1:
            sup_name = st.text_input("নাম:")
            sup_phone = st.text_input("ফোন:")
        
        with col2:
            sup_balance = st.number_input("ঋণ পরিমাণ:", min_value=0)
            sup_note = st.text_input("নোট:")
        
        if st.form_submit_button("➕ মহাজন যোগ করুন", use_container_width=True):
            if sup_name:
                data["suppliers"][sup_name] = {
                    "phone": sup_phone,
                    "balance": sup_balance,
                    "note": sup_note,
                    "created": datetime.now().strftime("%Y-%m-%d")
                }
                save_json(SHOP_FILE, shops)
                st.success("✅ মহাজন যোগ হয়েছে!")
                st.rerun()
            else:
                st.error("❌ নাম লিখুন!")
    
    st.divider()
    
    if data["suppliers"]:
        st.subheader("মহাজন লিস্ট")
        for name, info in data["suppliers"].items():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{name}**")
                    st.caption(f"📞 {info['phone']}")
                with col2:
                    st.write(f"ঋণ: ৳{info['balance']}")
                with col3:
                    if st.button("🗑️", key=f"del_sup_{name}"):
                        del data["suppliers"][name]
                        save_json(SHOP_FILE, shops)
                        st.rerun()
            st.divider()

# ============ 5. Wallet ============
elif menu == "🏦 ওয়ালেট":
    st.title("🏦 ওয়ালেট")
    
    data = shops[current_shop]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💵 ব্যালেন্স", f"৳{data['wallet']}")
    
    with col2:
        if st.button("➕ টাকা যোগ করুন"):
            st.session_state.show_add_wallet = True
    
    with col3:
        if st.button("➖ টাকা বের করুন"):
            st.session_state.show_remove_wallet = True
    
    if st.session_state.get("show_add_wallet"):
        amount = st.number_input("কত টাকা যোগ করবেন?", min_value=0)
        if st.button("✅ নিশ্চিত করুন"):
            data["wallet"] += amount
            save_json(SHOP_FILE, shops)
            st.success(f"✅ ৳{amount} যোগ হয়েছে!")
            st.session_state.show_add_wallet = False
            st.rerun()

# ============ 6. Reports ============
elif menu == "📈 রিপোর্ট":
    st.title("📈 রিপোর্ট")
    
    data = shops[current_shop]
    
    if data["transactions"]:
        income = sum([t["amount"] for t in data["transactions"] if t["type"] == "আয়"])
        expense = sum([t["amount"] for t in data["transactions"] if t["type"] == "খরচ"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🟢 মোট আয়", f"৳{income}")
        with col2:
            st.metric("🔴 মোট খরচ", f"৳{expense}")
        with col3:
            st.metric("💰 লাভ/ক্ষতি", f"৳{income - expense}")
    else:
        st.info("📭 এখনো কোনো লেনদেন নেই!")

# ============ 7. Settings ============
elif menu == "⚙️ সেটিংস":
    st.title("⚙️ সেটিংস")
    
    tab1, tab2 = st.tabs(["সাধারণ", "ডেটা"])
    
    with tab1:
        st.write("**সাধারণ সেটিংস**")
        if st.button("🔑 পাসওয়ার্ড পরিবর্তন করুন"):
            st.info("পাসওয়ার্ড পরিবর্তনের জন্য অ্যাডমিন সাথে যোগাযোগ করুন")
    
    with tab2:
        st.write("**ডেটা ব্যবস্থাপনা**")
        
        data = shops[current_shop]
        
        if st.button("📥 ডেটা ডাউনলোড করুন"):
            data_json = json.dumps(data, ensure_ascii=False, indent=2, default=str)
            st.download_button(
                label="JSON ডাউনলোড করুন",
                data=data_json,
                file_name=f"{current_shop}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        if st.button("🗑️ সব ডেটা মুছুন"):
            if st.checkbox("নিশ্চিত করুন"):
                shops[current_shop] = {
                    "transactions": [],
                    "customers": {},
                    "suppliers": {},
                    "wallet": 0
                }
                save_json(SHOP_FILE, shops)
                st.success("✅ সব ডেটা মুছে দেওয়া হয়েছে!")

st.divider()
st.markdown("<div style='text-align: center'><small>🛍️ দোকান অ্যাপ v1.0 | তৈরি: ২০২৬</small></div>", unsafe_allow_html=True)
