import streamlit as st
import pandas as pd
import json
import os
import hashlib
import datetime
from datetime import datetime as dt
import plotly.express as px
import io

# ============ কনফিগুরেশন ============
DATA_FOLDER = "data"
USERS_FILE = "users.json"
BACKUP_FOLDER = "backup"

# ফোল্ডার তৈরি করুন
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# ============ ইউটিলিটি ফাংশন ============
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        default_users = {
            "দোকান१": {"password": hash_password("pass1"), "created": str(datetime.date.today())},
            "দোকান२": {"password": hash_password("pass2"), "created": str(datetime.date.today())}
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=2)
        return default_users
    
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_shop_data(shop_name, data_type):
    file_path = f"{DATA_FOLDER}/{shop_name}_{data_type}.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

def save_shop_data(df, shop_name, data_type):
    file_path = f"{DATA_FOLDER}/{shop_name}_{data_type}.csv"
    df.to_csv(file_path, index=False, encoding='utf-8')

# ============ স্টেট ইনিশিয়ালাইজেশন ============
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['shop_name'] = ''

# ============ লগইন/লজআউট ============
if not st.session_state['logged_in']:
    st.set_page_config(page_title="দোকান - লগইন", layout="centered")
    st.markdown("""
    <style>
        .login-container {text-align: center; padding: 50px;}
        .title {font-size: 48px; color: #1f77b4; margin-bottom: 30px;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='title'>🛍️ দোকান অ্যাপ</div>", unsafe_allow_html=True)
    
    users = load_users()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("লগইন করুন")
        with st.form("login_form"):
            shop = st.text_input("দোকানের নাম")
            pwd = st.text_input("পাসওয়ার্ড", type='password')
            login_button = st.form_submit_button("🔓 লগইন", use_container_width=True)
            
            if login_button:
                if shop in users:
                    if users[shop]['password'] == hash_password(pwd):
                        st.session_state['logged_in'] = True
                        st.session_state['shop_name'] = shop
                        st.success(f"স্বাগতম, {shop}!")
                        st.rerun()
                    else:
                        st.error("❌ ভুল পাসওয়ার্ড!")
                else:
                    st.error("❌ দোকানের নাম পাওয়া যায়নি!")
        
        st.divider()
        st.subheader("নতুন দোকান যোগ করুন")
        with st.form("register_form"):
            new_shop = st.text_input("নতুন দোকানের নাম")
            new_pwd = st.text_input("পাসওয়ার্ড সেট করুন", type='password')
            confirm_pwd = st.text_input("পাসওয়ার্ড নিশ্চিত করুন", type='password')
            register_button = st.form_submit_button("✅ রেজিস্টার করুন", use_container_width=True)
            
            if register_button:
                if new_shop in users:
                    st.error("❌ এই নাম ইতিমধ্যে আছে!")
                elif new_pwd != confirm_pwd:
                    st.error("❌ পাসওয়ার্ড মিলছে না!")
                elif len(new_pwd) < 4:
                    st.error("❌ পাসওয়ার্ড কমপক্ষে ৪ অক্ষর হতে হবে!")
                else:
                    users[new_shop] = {
                        "password": hash_password(new_pwd),
                        "created": str(datetime.date.today())
                    }
                    save_users(users)
                    st.success(f"✅ {new_shop} সফলভাবে যুক্ত হয়েছে! এখন লগইন করুন।")
else:
    # ============ মেইন অ্যাপ ============
    st.set_page_config(page_title="দোকান অ্যাপ", layout="wide")
    
    # হেডার
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title(f"🛍️ {st.session_state['shop_name']}")
    with col3:
        if st.button("🚪 লজআউট", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['shop_name'] = ''
            st.rerun()
    
    shop_name = st.session_state['shop_name']
    
    # ডেটা লোড করুন
    sales_df = load_shop_data(shop_name, 'sales')
    supplier_df = load_shop_data(shop_name, 'supplier')
    customer_df = load_shop_data(shop_name, 'customer')
    
    # সাইডবার মেনু
    menu = [
        "📊 ড্যাশবোর্ড",
        "💰 লেনদেন",
        "🤝 মহাজন",
        "👤 কাস্টমার",
        "🏦 ব্যালেন্স",
        "📈 রিপোর্ট",
        "⚙️ সেটিংস"
    ]
    choice = st.sidebar.selectbox("মেনু", menu)
    
    # ============ ১. ড্যাশবোর্ড ============
    if choice == "📊 ড্যাশবোর্ড":
        st.subheader("সার্বিক অবস্থা")
        
        if len(sales_df) == 0:
            st.info("এখনো কোনো লেনদেন নেই")
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            total_in = sales_df['ইন (টাকা)'].sum() if 'ইন (টাকা)' in sales_df.columns else 0
            total_out = sales_df['আউট (টাকা)'].sum() if 'আউট (টাকা)' in sales_df.columns else 0
            net = total_in - total_out
            
            col1.metric("💵 মোট ক্যাশ ইন", f"{total_in:,.0f} টাকা")
            col2.metric("💸 মোট ক্যাশ আউট", f"{total_out:,.0f} টাকা")
            col3.metric("🏦 বর্তমান ব্যালেন্স", f"{net:,.0f} টাকা", delta=net)
            
            supplier_due = supplier_df['পাওনা'].sum() if 'পাওনা' in supplier_df.columns else 0
            col4.metric("💳 মহাজনকে দেওয়া", f"{supplier_due:,.0f} টাকা")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 সাম্প্রতিক লেনদেন")
            if len(sales_df) > 0:
                display_sales = sales_df.tail(10).copy()
                st.dataframe(display_sales, use_container_width=True, hide_index=True)
            else:
                st.info("কোনো লেনদেন নেই")
        
        with col2:
            st.subheader("⚠️ বকেয়া তালিকা")
            
            if len(supplier_df) > 0 and (supplier_df['পাওনা'] > 0).any():
                due_suppliers = supplier_df[supplier_df['পাওনা'] > 0][['মহাজনের নাম', 'পাওনা']].tail(5)
                for idx, row in due_suppliers.iterrows():
                    st.warning(f"🔴 {row['মহাজনের নাম']}: {row['পাওনা']:,.0f} টাকা")
            
            if len(customer_df) > 0 and (customer_df['বাকি'] > 0).any():
                due_customers = customer_df[customer_df['বাকি'] > 0][['কাস্টমারের নাম', 'বাকি']].tail(5)
                for idx, row in due_customers.iterrows():
                    st.info(f"🟢 {row['কাস্টমারের নাম']}: {row['বাকি']:,.0f} টাকা")
    
    # ============ ២. লেনদেন ============
    elif choice == "💰 লেনদেন":
        st.subheader("নতুন লেনদেন যোগ করুন")
        
        tab1, tab2, tab3 = st.tabs(["নতুন যোগ করুন", "সব লেনদেন", "এডিট/ডিলিট"])
        
        with tab1:
            with st.form("cash_form"):
                date = st.date_input("তারিখ", datetime.date.today())
                desc = st.text_input("বিবরণ", placeholder="যেমন: ৫টি শার্ট বিক্রি")
                method = st.selectbox("মাধ্যম", ["ক্যাশ", "ব্যাংক", "বিকাশ", "নগদ"])
                t_type = st.radio("ধরণ", ["টাকা আসছে (In)", "টাকা গেছে (Out)"])
                amount = st.number_input("টাকার পরিমাণ", min_value=0.0, step=10.0)
                
                if st.form_submit_button("✅ সেভ করুন", use_container_width=True):
                    if amount <= 0:
                        st.error("❌ টাকার পরিমাণ ০ এর চেয়ে বেশি হতে হবে")
                    elif not desc:
                        st.error("❌ বিবরণ লিখুন")
                    else:
                        v_in = amount if t_type == "টাকা আসছে (In)" else 0
                        v_out = amount if t_type == "টাকা গেছে (Out)" else 0
                        
                        new_row = pd.DataFrame([{
                            'তারিখ': date,
                            'বিবরণ': desc,
                            'পেমেন্ট মেথড': method,
                            'ইন (টাকা)': v_in,
                            'আউট (টাকা)': v_out
                        }])
                        
                        sales_df = pd.concat([sales_df, new_row], ignore_index=True)
                        save_shop_data(sales_df, shop_name, 'sales')
                        st.balloons()
                        st.success("✅ লেনদেন সেভ হয়েছে!")
        
        with tab2:
            if len(sales_df) > 0:
                st.dataframe(sales_df.sort_values('তারিখ', ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("কোনো লেনদেন নেই")
        
        with tab3:
            if len(sales_df) > 0:
                st.warning("⚠️ মুছে ফেলার সময় সাবধান!")
                
                delete_index = st.selectbox(
                    "মুছতে চান এমন লেনদেন নির্বাচন করুন:",
                    range(len(sales_df)),
                    format_func=lambda i: f"{sales_df.iloc[i]['তারিখ']} - {sales_df.iloc[i]['বিবরণ']}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ মুছে দিন", key="delete_sales", use_container_width=True):
                        sales_df = sales_df.drop(delete_index).reset_index(drop=True)
                        save_shop_data(sales_df, shop_name, 'sales')
                        st.success("✅ মুছে দেওয়া হয়েছে!")
                        st.rerun()
            else:
                st.info("কোনো লেনদেন নেই")
    
    # ============ ३. মহাজন ============
    elif choice == "🤝 মহাজন":
        st.subheader("মহাজন/পার্টি হিসাব")
        
        tab1, tab2, tab3 = st.tabs(["নতুন যোগ করুন", "সব হিসাব", "এডিট/ডিলিট"])
        
        with tab1:
            with st.form("sup_form"):
                date = st.date_input("তারিখ", datetime.date.today())
                name = st.text_input("মহাজনের নাম", placeholder="যেমন: করিম সাহেব")
                bill = st.number_input("মোট বিল", min_value=0.0, step=100.0)
                paid = st.number_input("পরিশোধ করেছেন", min_value=0.0, step=100.0)
                
                if st.form_submit_button("✅ সেভ করুন", use_container_width=True):
                    if not name:
                        st.error("❌ নাম লিখুন")
                    elif bill <= 0:
                        st.error("❌ বিল ০ এর চেয়ে বেশি হতে হবে")
                    else:
                        new_row = pd.DataFrame([{
                            'তারিখ': date,
                            'মহাজনের নাম': name,
                            'মোট বিল': bill,
                            'পরিশোধিত': paid,
                            'পাওনা': bill - paid
                        }])
                        
                        supplier_df = pd.concat([supplier_df, new_row], ignore_index=True)
                        save_shop_data(supplier_df, shop_name, 'supplier')
                        st.balloons()
                        st.success("✅ হিসাব সেভ হয়েছে!")
        
        with tab2:
            if len(supplier_df) > 0:
                st.dataframe(supplier_df.sort_values('তারিখ', ascending=False), use_container_width=True, hide_index=True)
                
                st.divider()
                st.subheader("📊 মহাজন সারসংক্ষেপ")
                total_bill = supplier_df['মোট বিল'].sum()
                total_paid = supplier_df['পরিশোধিত'].sum()
                total_due = supplier_df['পাওনা'].sum()
                
                col1, col2, col3 = st.columns(3)
                col1.metric("মোট বিল", f"{total_bill:,.0f} টাকা")
                col2.metric("মোট পরিশোধিত", f"{total_paid:,.0f} টাকা")
                col3.metric("মোট পাওনা", f"{total_due:,.0f} টাকা")
            else:
                st.info("কোনো মহাজন হিসাব নেই")
        
        with tab3:
            if len(supplier_df) > 0:
                delete_index = st.selectbox(
                    "মুছতে চান এমন হিসাব:",
                    range(len(supplier_df)),
                    format_func=lambda i: f"{supplier_df.iloc[i]['মহাজনের নাম']} - {supplier_df.iloc[i]['পাওনা']:,.0f} টাকা"
                )
                
                if st.button("🗑️ মুছে দিন", key="delete_supplier", use_container_width=True):
                    supplier_df = supplier_df.drop(delete_index).reset_index(drop=True)
                    save_shop_data(supplier_df, shop_name, 'supplier')
                    st.success("✅ মুছে দেওয়া হয়েছে!")
                    st.rerun()
            else:
                st.info("কোনো হিসাব নেই")
    
    # ============ 4. কাস্টমার ============
    elif choice == "👤 কাস্টমার":
        st.subheader("কাস্টমার বাকি হিসাব")
        
        tab1, tab2, tab3 = st.tabs(["নতুন যোগ করুন", "সব হিসাব", "এডিট/ডিলিট"])
        
        with tab1:
            with st.form("cust_form"):
                date = st.date_input("তারিখ", datetime.date.today())
                name = st.text_input("কাস্টমারের নাম/মোবাইল", placeholder="যেমন: আবুল - ০১৭xxxx")
                price = st.number_input("মালের মোট দাম", min_value=0.0, step=50.0)
                cash = st.number_input("নগদ দিয়েছে", min_value=0.0, step=50.0)
                
                if st.form_submit_button("✅ সেভ করুন", use_container_width=True):
                    if not name:
                        st.error("❌ নাম লিখুন")
                    elif price <= 0:
                        st.error("❌ দাম ০ এর চেয়ে বেশি হতে হবে")
                    else:
                        new_row = pd.DataFrame([{
                            'তারিখ': date,
                            'কাস্টমারের নাম': name,
                            'মালের দাম': price,
                            'জমা দিয়েছে': cash,
                            'বাকি': price - cash
                        }])
                        
                        customer_df = pd.concat([customer_df, new_row], ignore_index=True)
                        save_shop_data(customer_df, shop_name, 'customer')
                        st.balloons()
                        st.success("✅ হিসাব সেভ হয়েছে!")
        
        with tab2:
            if len(customer_df) > 0:
                st.dataframe(customer_df.sort_values('তারিখ', ascending=False), use_container_width=True, hide_index=True)
                
                st.divider()
                st.subheader("📊 কাস্টমার সারসংক্ষেপ")
                total_price = customer_df['মালের দাম'].sum()
                total_paid = customer_df['জমা দিয়েছে'].sum()
                total_due = customer_df['বাকি'].sum()
                
                col1, col2, col3 = st.columns(3)
                col1.metric("মোট বিক্রয়", f"{total_price:,.0f} টাকা")
                col2.metric("মোট পেমেন্ট", f"{total_paid:,.0f} টাকা")
                col3.metric("মোট বাকি", f"{total_due:,.0f} টাকা")
            else:
                st.info("কোনো কাস্টমার হিসাব নেই")
        
        with tab3:
            if len(customer_df) > 0:
                delete_index = st.selectbox(
                    "মুছতে চান এমন হিসাব:",
                    range(len(customer_df)),
                    format_func=lambda i: f"{customer_df.iloc[i]['কাস্টমারের নাম']} - {customer_df.iloc[i]['বাকি']:,.0f} টাকা"
                )
                
                if st.button("🗑️ মুছে দিন", key="delete_customer", use_container_width=True):
                    customer_df = customer_df.drop(delete_index).reset_index(drop=True)
                    save_shop_data(customer_df, shop_name, 'customer')
                    st.success("✅ মুছে দেওয়া হয়েছে!")
                    st.rerun()
            else:
                st.info("কোনো হিসাব নেই")
    
    # ============ 5. ব্যালেন্স ============
    elif choice == "🏦 ব্যালেন্স":
        st.subheader("ওয়ালেট ও ব্যাংক ব্যালেন্স")
        
        if len(sales_df) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            for i, method in enumerate(["ক্যাশ", "ব্যাংক", "বিকাশ", "নগদ"]):
                m_in = sales_df[sales_df['পেমেন্ট মেথড'] == method]['ইন (টাকা)'].sum()
                m_out = sales_df[sales_df['পেমেন্ট মেথড'] == method]['আউট (টাকা)'].sum()
                balance = m_in - m_out
                
                cols = [col1, col2, col3, col4]
                with cols[i]:
                    st.metric(f"💳 {method}", f"{balance:,.0f} টাকা", delta=balance)
            
            st.divider()
            
            st.subheader("বিস্তারিত")
            method_filter = st.selectbox("মাধ্যম নির্বাচন করুন", ["সব"] + ["ক্যাশ", "ব্যাংক", "বিকাশ", "নগদ"])
            
            if method_filter == "সব":
                display_df = sales_df
            else:
                display_df = sales_df[sales_df['পেমেন্ট মেথড'] == method_filter]
            
            st.dataframe(display_df.sort_values('তারিখ', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("কোনো লেনদেন নেই")
    
    # ============ 6. রিপোর্ট ============
    elif choice == "📈 রিপোর্ট":
        st.subheader("বিশ্লেষণ ও রিপোর্ট")
        
        tab1, tab2, tab3 = st.tabs(["সারসংক্ষেপ", "গ্রাফ", "রপ্তানি"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("💰 **লেনদেন সংক্ষেপ**")
                if len(sales_df) > 0:
                    total_in = sales_df['ইন (টাকা)'].sum()
                    total_out = sales_df['আউট (টাকা)'].sum()
                    net = total_in - total_out
                    
                    st.metric("মোট ইনকাম", f"{total_in:,.0f} টাকা")
                    st.metric("মোট খরচ", f"{total_out:,.0f} টাকা")
                    st.metric("লাভ/লোকসান", f"{net:,.0f} টাকা")
            
            with col2:
                st.warning("⚠️ **বকেয়া তথ্য**")
                supplier_due = supplier_df['পাওনা'].sum() if len(supplier_df) > 0 else 0
                customer_due = customer_df['বাকি'].sum() if len(customer_df) > 0 else 0
                
                st.metric("মহাজনকে দেওয়া", f"{supplier_due:,.0f} টাকা")
                st.metric("কাস্টমারদের কাছ থেকে পাবার", f"{customer_due:,.0f} টাকা")
        
        with tab2:
            if len(sales_df) > 0:
                # মাসিক লেনদেন
                sales_df['তারিখ'] = pd.to_datetime(sales_df['তারিখ'])
                sales_df['মাস'] = sales_df['তারিখ'].dt.to_period('M')
                
                monthly = sales_df.groupby('মাস')[['ইন (টাকা)', 'আউট (টাকা)']].sum().reset_index()
                monthly['মাস'] = monthly['মাস'].astype(str)
                
                fig = px.bar(monthly, x='মাস', y=['ইন (টাকা)', 'আউট (টাকা)'], 
                            title="মাসিক ইনকাম ও খরচ", barmode='group')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("রিপোর্ট তৈরির জন্য ডেটা নেই")
        
        with tab3:
            st.subheader("📥 ডেটা এক্সপোর্ট করুন")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 লেনদেন (CSV)", use_container_width=True):
                    csv = sales_df.to_csv(index=False, encoding='utf-8')
                    st.download_button("ডাউনলোড", csv, "sales.csv", "text/csv")
            
            with col2:
                if st.button("🤝 মহাজন (CSV)", use_container_width=True):
                    csv = supplier_df.to_csv(index=False, encoding='utf-8')
                    st.download_button("ডাউনলোড", csv, "supplier.csv", "text/csv")
            
            with col3:
                if st.button("👤 কাস্টমার (CSV)", use_container_width=True):
                    csv = customer_df.to_csv(index=False, encoding='utf-8')
                    st.download_button("ডাউনলোড", csv, "customer.csv", "text/csv")
    
    # ============ 7. সেটিংস ============
    elif choice == "⚙️ সেটিংস":
        st.subheader("সেটিংস ও অপশন")
        
        tab1, tab2, tab3 = st.tabs(["পাসওয়ার্ড", "ডেটা", "তথ্য"])
        
        with tab1:
            st.subheader("🔐 পাসওয়ার্ড পরিবর্তন করুন")
            with st.form("pwd_form"):
                old_pwd = st.text_input("পুরাতন পাসওয়ার্ড", type='password')
                new_pwd = st.text_input("নতুন পাসওয়ার্ড", type='password')
                confirm_pwd = st.text_input("নতুন পাসওয়ার্ড নিশ্চিত করুন", type='password')
                
                if st.form_submit_button("✅ পরিবর্তন করুন", use_container_width=True):
                    users = load_users()
                    
                    if users[shop_name]['password'] != hash_password(old_pwd):
                        st.error("❌ পুরাতন পাসওয়ার্ড ভুল!")
                    elif new_pwd != confirm_pwd:
                        st.error("❌ নতুন পাসওয়ার্ড মিলছে না!")
                    elif len(new_pwd) < 4:
                        st.error("❌ পাসওয়ার্ড কমপক্ষে ৪ অক্ষর হতে হবে!")
                    else:
                        users[shop_name]['password'] = hash_password(new_pwd)
                        save_users(users)
                        st.success("✅ পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে!")
        
        with tab2:
            st.subheader("🗑️ ডেটা পরিচালনা")
            
            st.warning("⚠️ সাবধান: এই অ্যাকশন পূর্ববর্তী করা যাবে না!")
            
            if st.button("🗑️ সব ডেটা মুছে দিন", use_container_width=True):
                st.session_state['show_confirm'] = True
            
            if st.session_state.get('show_confirm', False):
                st.error("আপনি কি নিশ্চিত? এটি সব ডেটা মুছে দেবে!")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("হ্যাঁ, মুছে দিন"):
                        os.remove(f"{DATA_FOLDER}/{shop_name}_sales.csv") if os.path.exists(f"{DATA_FOLDER}/{shop_name}_sales.csv") else None
                        os.remove(f"{DATA_FOLDER}/{shop_name}_supplier.csv") if os.path.exists(f"{DATA_FOLDER}/{shop_name}_supplier.csv") else None
                        os.remove(f"{DATA_FOLDER}/{shop_name}_customer.csv") if os.path.exists(f"{DATA_FOLDER}/{shop_name}_customer.csv") else None
                        st.session_state['show_confirm'] = False
                        st.success("✅ সব ডেটা মুছে দেওয়া হয়েছে!")
                        st.rerun()
                
                with col2:
                    if st.button("না, বাতিল করুন"):
                        st.session_state['show_confirm'] = False
                        st.rerun()
        
        with tab3:
            st.subheader("ℹ️ অ্যাপ তথ্য")
            st.info(f"""
            **দোকান:** {shop_name}
            
            **সংস্করণ:** ১.০.০
            
            **তৈরি:** ২০২৬
            
            **স্টোরেজ অবস্থান:** `{DATA_FOLDER}/`
            """)
