import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="ተስፋ የቁጠባ እና ብድር ሲስተም", layout="wide")
st.title("🏦 ተስፋ የገንዘብ ብድር እና ቁጠባ ማህበር")

# Initialize session state for data storage
if "members_db" not in st.session_state:
    st.session_state.members_db = {}

members_db = st.session_state.members_db

# Display current database status
st.sidebar.info(f"📊 አባላት በሲስተሙ: {len(members_db)}")

# የጎንዮሽ ማውጫ (Sidebar)
menu = st.sidebar.selectbox(
    "ያሉ አማራጮች", 
    ["👤 አባል መመዝገቢያ", "💰 የወር ቁጠባ ማስገቢያ", "💵 የብድር አገልግሎት", "📅 የብድር ክፍያ መመዝገቢያ", "📊 ጠቅላላ ሪፖርት"]
)

# --- 1. አባል መመዝገቢያ ገጽ ---
if menu == "👤 አባል መመዝገቢያ":
    st.header("👤 አዲስ አባል መመዝገቢያ ፎርም")
    
    col1, col2 = st.columns(2)
    
    with col1:
        m_id = st.text_input("የአባል መታወቂያ ቁጥር (ID):", key="member_id")
        # Validate that ID contains only numbers
        if m_id and not m_id.isdigit():
            st.error("❌ መታወቂያ ቁጥር ሙሉ በሙሉ ቁጥር ብቻ ሊሆን ይገባል!")
            m_id = ""
    
    with col2:
        m_name = st.text_input("የአባል ሙሉ ስም:", key="member_name")
        # Validate that name contains only letters and spaces (Amharic)
        if m_name and any(char.isdigit() for char in m_name):
            st.error("❌ ስም ቁጥር ሊያካትት አይችልም! ፊደሎች ብቻ ይጻፉ።")
            m_name = ""
    
    register_btn = st.button("አባል መዝግብ", key="register_btn")
    
    if register_btn:
        if m_id and m_name:
            if not m_id.isdigit():
                st.error("❌ መታወቂያ ቁጥር ሙሉ በሙሉ ቁጥር ብቻ ሊሆን ይገባል!")
            elif any(char.isdigit() for char in m_name):
                st.error("❌ ስም ቁጥር ሊያካትት አይችልም!")
            elif m_id in members_db:
                st.error(f"❌ ስህተት፦ መታወቂያ ቁጥር {m_id} ቀደም ብሎ ተመዝግቧል!")
            else:
                members_db[m_id] = {
                    "የአባል ስም": m_name,
                    "ጠቅላላ ቁጠባ (ብር)": 0.0,
                    "ብድር ሁኔታ": "የለበትም",
                    "የተበደረው ጠቅላላ (ብር)": 0.0,
                    "በእጅ የተሰጠ 90% (ብር)": 0.0,
                    "ቀሪ ዕዳ (ብር)": 0.0
                }
                st.session_state.members_db = members_db
                st.success(f"✅ አባል {m_name} በተሳካ ሁኔታ ተመዝግቧል!")
                st.balloons()
        else:
            st.warning("⚠️ እባክዎ ሁሉንም ሳጥኖች ይሙሉ!")
    
    # Display registered members
    if members_db:
        st.divider()
        st.subheader("📋 የተመዘገቡ አባላት")
        for mid, mdata in members_db.items():
            st.write(f"🆔 {mid} - {mdata['የአባል ስም']}")

# --- 2. የወር ቁጠባ ማስገቢያ ገጽ ---
elif menu == "💰 የወር ቁጠባ ማስገቢያ":
    st.header("💰 የወርሃዊ ቁጠባ መመዝገቢያ")
    
    if not members_db:
        st.warning("⚠️ በመጀመሪያ አባል መመዝገብ ያስፈልጋል!")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            s_id = st.selectbox("አባል ምረጥ:", list(members_db.keys()), key="savings_id")
        
        with col2:
            amount = st.number_input("የሚቆጥበው የገንዘብ መጠን (ብር):", min_value=0.0, step=100.0)
        
        save_btn = st.button("ቁጠባ መዝግብ", key="savings_btn")
        
        if save_btn:
            if s_id in members_db:
                members_db[s_id]["ጠቅላላ ቁጠባ (ብር)"] += amount
                st.session_state.members_db = members_db
                st.success(f"✅ ለ{members_db[s_id]['የአባል ስም']} {amount:,.2f} ብር ቁጠባ ተመዝግቧል።")
                st.balloons()
            else:
                st.error("❌ ይህ መታወቂያ በሲስተሙ ውስጥ አልተገኘም!")

# --- 3. የብድር አገልግሎት ገጽ ---
elif menu == "💵 የብድር አገልግሎት":
    st.header("💵 የብድር ማመልከቻ እና ስሌት")
    
    if not members_db:
        st.warning("⚠️ በመጀመሪያ አባል መመዝገብ ያስፈልጋል!")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            loan_id = st.selectbox("አባል ምረጥ:", list(members_db.keys()), key="loan_id")
        
        with col2:
            loan_amount = st.number_input("የሚጠይቀው የብድር መጠን (ብር):", min_value=0.0, step=1000.0)
        
        calculate_btn = st.button("ብድር አስላ እና ፍቀድ", key="loan_btn")
        
        if calculate_btn:
            if loan_id in members_db:
                member = members_db[loan_id]
                if member["ብድር ሁኔታ"] == "ያለበት":
                    st.error(f"❌ ስህተት፦ {member['የአባል ስም']} የድሮ ብድር ስላለበት ተጨማሪ መበደር አይችልም!")
                else:
                    upfront_fee = loan_amount * 0.10
                    net_payout = loan_amount - upfront_fee
                    monthly_principal = loan_amount / 36
                    monthly_interest = loan_amount * 0.02
                    total_monthly = monthly_principal + monthly_interest
                    
                    member["ብድር ሁኔታ"] = "ያለበት"
                    member["የተበደረው ጠቅላላ (ብር)"] = loan_amount
                    member["በእጅ የተሰጠ 90% (ብር)"] = net_payout
                    member["ቀሪ ዕዳ (ብር)"] = loan_amount
                    
                    st.session_state.members_db = members_db
                    st.success(f"🎉 ለ{member['የአባል ስም']} ብድር ተፈቅዷል!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("በእጅ የሚሰጠው (90%)", f"{net_payout:,.2f} ብር")
                    with col2:
                        st.metric("የወር ክፍያ", f"{total_monthly:,.2f} ብር")
                    
                    st.info(f"📅 **36 ወራት ክፍያ መርሕ:**\n\n"
                            f"- **ዋና ዓመታዊ**: {monthly_principal:,.2f} ብር\n"
                            f"- **ወለድ 2%**: {monthly_interest:,.2f} ብር\n"
                            f"- **ጠቅላላ**: {total_monthly:,.2f} ብር/ወር")
            else:
                st.error("❌ ይህ መታወቂያ በሲስተሙ ውስጥ አልተገኘም!")

# --- 4. የብድር ክፍያ መመዝገቢያ ገጽ ---
elif menu == "📅 የብድር ክፍያ መመዝገቢያ":
    st.header("📅 የወርሃዊ ብድር ክፍያ መቀበያ")
    
    if not members_db:
        st.warning("⚠️ በመጀመሪያ አባል መመዝገብ ያስፈልጋል!")
    else:
        p_id = st.selectbox("አባል ምረጥ:", list(members_db.keys()), key="payment_id")
        
        if p_id in members_db:
            member = members_db[p_id]
            if member["ብድር ሁኔታ"] == "ያለበት":
                st.warning(f"📌 {member['የአባል ስም']} ያለበት ጠቅላላ ዕዳ፦ {member['ቀሪ ዕዳ (ብር)']:,.2f} ብር")
                
                monthly_principal = member["የተበደረው ጠቅላላ (ብር)"] / 36
                monthly_interest = member["የተበደረው ጠቅላላ (ብር)"] * 0.02
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("ዋና ክፍያ", f"{monthly_principal:,.2f} ብር")
                with col2:
                    st.metric("ወለድ", f"{monthly_interest:,.2f} ብር")
                
                st.write(f"💡 **መደበኛ የወር ክፍያ: {monthly_principal + monthly_interest:,.2f} ብር**")
                
                pay_amount = st.number_input("አባል አሁን የከፈለው ጠቅላላ ብር:", min_value=0.0, key="pay_amount")
                pay_btn = st.button("ክፍያ መዝግብ", key="pay_btn")
                
                if pay_btn:
                    actual_principal_paid = pay_amount - monthly_interest
                    if actual_principal_paid < 0:
                        actual_principal_paid = 0
                    
                    member["ቀሪ ዕዳ (ብር)"] -= actual_principal_paid
                    if member["ቀሪ ዕዳ (ብር)"] <= 0:
                        member["ቀሪ ዕዳ (ብር)"] = 0.0
                        member["ብድር ሁኔታ"] = "የለበትም"
                        st.success(f"🎉 {member['የአባል ስም']} ብድሩን ሙሉ በሙሉ ከፍሎ ጨርሷል!")
                        st.balloons()
                    else:
                        st.success(f"✅ ክፍያ ተመዝግቧል።")
                        st.info(f"📊 ቀሪ ዕዳ: {member['ቀሪ ዕዳ (ብር)']:,.2f} ብር")
                    st.session_state.members_db = members_db
            else:
                st.info(f"💡 {member['የአባል ስም']} ላይ ምንም ዓይነት የብድር ዕዳ የለም።")

# --- 5. የሪፖርት ገጽ ---
elif menu == "📊 ጠቅላላ ሪፖርት":
    st.header("📊 ጠቅላላ ሪፖርት")
    
    if members_db:
        # Rename the column for display
        df = pd.DataFrame.from_dict(members_db, orient="index")
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 አጠቃላይ አባላት", len(members_db))
        with col2:
            total_savings = df["ጠቅላላ ቁጠባ (ብር)"].sum()
            st.metric("💰 ጠቅላላ ቁጠባ", f"{total_savings:,.2f}")
        with col3:
            active_loans = len(df[df["ብድር ሁኔታ"] == "ያለበት"])
            st.metric("📊 ጠቅላላ ብድር", active_loans)
        with col4:
            total_debt = df["ቀሪ ዕዳ (ብር)"].sum()
            st.metric("📈 ቀሪ ዕዳ", f"{total_debt:,.2f}")
        
        st.divider()
        st.subheader("📋 በዝርዝር ዝርዝር")
        st.dataframe(df, use_container_width=True)
        
        # Export option
        st.divider()
        csv = df.to_csv()
        st.download_button(
            label="📥 ሪፖርት CSV ውርጅ",
            data=csv,
            file_name="sacco_report.csv",
            mime="text/csv"
        )
    else:
        st.info("📌 እስካሁን በሲስተሙ ላይ የተመዘገበ መረጃ የለም።")

# Footer
st.divider()
st.caption("🏦 ተስፋ የገንዘብ ብድር እና ቁጠባ ማህበር | SACCO System v1.0")
