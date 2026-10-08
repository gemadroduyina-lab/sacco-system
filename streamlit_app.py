import streamlit as st
import pandas as pd
import os
import base64
import math
from io import StringIO, BytesIO
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ተስፋ የገንዘብ ቁጠባና ብድር ማህበር",
    page_icon="🏦",
    layout="wide"
)

DB_FILE = "sacco_database.xlsx"

# 12 months - Ethiopian fiscal/year cycle requested
MONTHS = [
    "መስከረም",
    "ጥቅምት",
    "ኅዳር",
    "ታኅሣሥ",
    "ጥር",
    "የካቲት",
    "መጋቢት",
    "ሚያዝያ",
    "ግንቦት",
    "ሰኔ",
    "ሐምሌ",
    "ነሐሴ"
]

SEED_VERSION = "fixed136-v1"

REGISTRATION_FEE = 500.0
LOAN_FEE_RATE = 0.10
INTEREST_RATE = 0.02

LOAN_TERMS = [3, 6, 9, 12, 24, 36]  # 9 ወር የአጭር ጊዜ አማራጭ ተጨምሯል

# ============================================================
# 136 MEMBERS
# ============================================================

MEMBER_DATA = """
1	ወርቅነህ ጉታ	1000	1000	1000
2	ኢሳያስ አይሳ	0	0	0
3	ፍቅራለም ዳኪቶ	1500	1500	1500
4	ትክክል ከበደ	2000	2000	2000
5	መስታውት ወንድሙ	2000	2000	2000
6	አምባው መዳረሻ	1500	1500	1500
7	አቻምየለሽ ገሪቶ	8000	8000	8000
8	መስከረም አያሌው	1000	1000	1000
9	አዲሳለም ገዛኸኝ	1000	1000	1000
10	አሰቴር ጋሪፎ	500	500	500
11	ወልዴ ታደሰ	1000	2250	1000
12	መስፍን ኃይሌ	500	500	500
13	አድማሱ ሙላቱ	500	500	500
14	ዋሲሁን አድነው	1000	1000	1000
15	ስኳሬ ማሞ	1100	1100	1100
16	ተሸለ አንጉሎ	13000	13000	13000
17	ታደለች ሰይድ	700	700	700
18	አበበ ዳጫቸው	1000	1000	1000
19	አዲሱ አቡዬ	1000	1000	1000
20	ገለታ ጌታቸው	6000	6000	6000
21	ጌታቸው ታደሰ	500	500	500
22	ቡዛለም ጸሀይ	500	500	500
23	ሽብሩ ዳዲሞ	500	6000	500
24	ይልቃል ካሳ	1000	1000	1000
25	አበበች ደሳለኝ	500	500	500
26	ሙሉቀን ታዬ	6000	6000	6000
27	ግርማ ገ/ሚካኤል	1000	1000	1000
28	ሥጋቱ አሰፋ	1000	1000	1000
29	ልኡል ሰገድ ሙንዬ	0	0	0
30	ሀብታሙ ኃይሌ	500	500	500
31	ግዛው አርሰኖ	300	300	300
32	ክፍሌ አበበ	1000	1000	1000
33	እምሩ እሚቶ	500	500	500
34	መከተ ማሞ	1000	1000	1000
35	ጀመረ ቆጭቶ	500	500	500
36	ዳግም ደምሴ	2000	2000	2000
37	ገነት ኃይሌ	500	500	500
38	አዲሱ አገሎ	1000	1000	1000
39	አክሊሉ አቾሞ	500	0	0
40	ቆጭቶ ወ/ሥላሴ	500	500	500
41	ትግሌ ታምሩ	500	1000	1000
42	ታሪኳ አንገሎ	600	600	600
43	ዮሐንስ ታከለ	1000	1000	1000
44	ታምሩ ጋሎ	500	500	500
45	ታምሩ ደስኖ	5000	5000	5000
46	ኬሮ ማሞ	700	700	0
47	አክሊሉ ሻረው	500	500	500
48	አጦ አምቦ	500	500	500
49	አክሊሉ ገበዬሁ	500	500	500
50	መሠረት መቹሎ	1000	1000	1000
51	ማዘንጊያሽ በፍቃዱ	500	500	500
52	ሽመልስ ይመር	500	500	500
53	ሙሉጌታ ሃይሌ	0	0	0
54	መላኩ ወ/ሚካኤል	1000	1000	1000
55	አባተ ገብሬ	0	0	0
56	አክሊሉ ኃይሌ	500	500	500
57	አስረስ አደም	1000	1000	1000
58	የሺዋስ ሙላቱ	500	500	500
59	ግዛው ደንበል	0	0	0
60	ኪሮስ ምትኩ	10000	10000	2000
61	ዘሪቱ ይማም	3000	3000	3000
62	ኤሊያስ አዳሾ	500	500	500
63	ትዕግስት ዓለሙ	1000	1000	1000
64	አዲሱ ደመቀ	1000	1000	1000
65	አበበ ቦጋለ	1000	1000	1000
66	እሸቱ በዛብህ	500	500	500
67	ዳርጌ እሸቱ	500	500	500
68	ቡዛዬሁ ኃይሌ	500	500	500
69	ካሳሁን ወ/ጻድቅ	1000	1000	1000
70	አልማዝ ኃይሌ	0	0	0
71	ለገሰ ዘውዴ	200	200	200
72	እህታለም ታዬ	2000	2000	2000
73	አያሌው ከልክሌ	0	0	0
74	ሀብታሙ አሰፋ	0	0	0
75	ዘሪሁን ዲላሞ	300	300	300
76	ባህሩ ገባቦ	0	0	0
77	ገሰሰ ገበዬሁ	2000	2000	2000
78	ጀመረ አድራሮ	600	600	600
79	ይታይህ ቁምላቸው	400	400	400
80	መንግሥቱ መጫሎ	500	500	500
81	አስራት በዛብህ	2000	2000	2000
82	ጌታቸው ገ/ማሪያም	300	1133.33	300
83	ይድነቃቸው አበበ	3000	3000	3000
84	አህመድ የሱፍ	1000	1000	1000
85	ጀማል መሃመድ	0	0	0
86	አምንቴ አዳሾ	500	500	500
87	ምንትዋብ አምበሎ	1000	1000	1000
88	ቢሻሽ በቃሉ	1000	1000	1000
89	ሰለሞን ሾደኖ	2000	2000	2000
90	ቡዛዬሁ ጋሪፎ	2000	2000	2000
91	እምቢበል ቆጭቶ	1000	1000	1000
92	የሺጥላ ገላን	1000	1000	1000
93	ዮናስ ካዳኔ	1000	1000	1000
94	ቃላአብ ጥኡም	0	0	0
95	ዓለሙ ብርሃኑ	1000	1000	1000
96	ሠላሙ ዳሪቆ	500	500	500
97	ሞሲሳ ቤኛ	2000	2000	2000
98	ተካልኝ አደሞ	500	500	500
99	ወርቅነሽ አንገሎ	1000	1000	1000
100	ባሳዝነው በላይ	2000	3000	3000
101	ፍቃዱ ጉታ	1000	1000	1000
102	ውድነሽ ቀጸላ	1000	1000	1000
103	አመለወርቅ መስፍን	1000	1000	1000
104	የኋላእሸት በቃሉ	500	500	500
105	ሙሴ ካሳሁን	0	0	0
106	ሳልልሽ ጸዳ	2000	2000	2000
107	ተራመድ ገረመው	1000	1000	1000
108	ሚሊዮን አትርሴ	1000	1000	1000
109	ዓለሙ ገ/ማሪያም	1000	1000	1000
110	ዘካሪያስ ቶላ	2000	2000	2000
111	አለማዬሁ ተስፋዬ	2000	2000	2000
112	አጥናፉ ገይቶ	500	500	500
113	ተናኜ አንገሎ	500	500	500
114	ሻመቶ እንደሻው	1000	1000	1000
115	ማርታ አበበ	1000	1000	1000
116	አስናቀች ነገዎ	1000	1000	1000
117	አዲስዓለም አደዮ	1000	1000	1000
118	ታፈሰ ታምሩ	0	0	0
119	ወርቁ ጋዎቶ	700	700	700
120	አንዱዓለም ተስፋዬ	1000	1000	1000
121	አጥናፉ አዴሎ	5000	5000	5000
122	አሸናፊ አበበ	1000	1000	1000
123	ደስታ ሙላት	2000	2000	2000
124	ገዛኸኝ ገደኖ	2000	2000	2000
125	ታደሰ ወ/ሚካኤል	1000	1000	1000
126	አማኑኤል አድነው	1000	1000	1000
127	ሽብሩ ሻወኖ	3000	3000	3000
128	ዳንኤል መስፍን	0	0	0
129	መስፍን ማሞ	1000	1000	1000
130	ባይለየኘ ክብረት	1000	1000	1000
131	ጠና ደጋጋ	0	1000	0
132	ኤርሚያስ ግዛው	0	1000	1000
133	መብራቴ ሻረው	0	500	500
134	ፍጹም ፍስሃ	0	10000	10000
135	ይከበር አለምነህ	0	0	7000
136	ግርማ ግዛው	0	0	1000
"""

# ============================================================
# HELPERS
# ============================================================

def money(value):
    try:
        return f"{float(value):,.2f}"
    except Exception:
        return "0.00"

def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default

def safe_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except Exception:
        return default

def normalize_member(member):
    for month in MONTHS:
        member[month] = safe_float(member.get(month, 0))
    member["የአባል ቁጥር"] = safe_int(member.get("የአባል ቁጥር", 0))
    member["ስም"] = str(member.get("ስም", "") or "")
    member["ብሔራዊ መታወቂያ"] = str(member.get("ብሔራዊ መታወቂያ", "") or "")
    member["ፎቶ"] = str(member.get("ፎቶ", "") or "")
    member["የመመዝገቢያ ክፍያ (ብር)"] = safe_float(member.get("የመመዝገቢያ ክፍያ (ብር)", REGISTRATION_FEE))
    member["የተበደረ ብር"] = safe_float(member.get("የተበደረ ብር", 0))
    member["10% የብድር ክፍያ (ብር)"] = safe_float(member.get("10% የብድር ክፍያ (ብር)", 0))
    member["በእጅ የተሰጠ 90% (ብር)"] = safe_float(member.get("በእጅ የተሰጠ 90% (ብር)", 0))
    member["የብድር ጊዜ (ወር)"] = safe_int(member.get("የብድር ጊዜ (ወር)", 0))
    member["የብድር ወርሃዊ ክፍያ (ብር)"] = safe_float(member.get("የብድር ወርሃዊ ክፍያ (ብር)", 0))
    member["የቀረው ዋና ብድር (ብር)"] = safe_float(member.get("የቀረው ዋና ብድር (ብር)", member.get("የቀረው ዕዳ (ብር)", 0)))
    member["የቀረው ዕዳ (ብር)"] = safe_float(member.get("የቀረው ዕዳ (ብር)", member.get("የቀረው ዋና ብድር (ብር)", 0)))
    member["የተከፈለ ወለድ (ብር)"] = safe_float(member.get("የተከፈለ ወለድ (ብር)", 0))
    member["የተከፈለ ዋና ብድር (ብር)"] = safe_float(member.get("የተከፈለ ዋና ብድር (ብር)", 0))
    member["የተበደረበት ቀን"] = str(member.get("የተበደረበት ቀን", "") or "")
    return member

# ============================================================
# INITIAL MEMBERS
# ============================================================

def create_initial_members():
    members = []
    df = pd.read_csv(StringIO(MEMBER_DATA.strip()), sep="\t", header=None, names=["የአባል ቁጥር", "ስም", "መስከረም", "ጥቅምት", "ኅዳር"])
    for _, row in df.iterrows():
        member = {
            "የአባል ቁጥር": int(row["የአባል ቁጥር"]),
            "ስም": str(row["ስም"]),
            "ብሔራዊ መታወቂያ": "",
            "ፎቶ": "",
            "መስከረም": safe_float(row["መስከረም"]),
            "ጥቅምት": safe_float(row["ጥቅምት"]),
            "ኅዳር": safe_float(row["ኅዳር"])
        }
        for month in MONTHS[3:]:
            member[month] = 0.0
        member["የመመዝገቢያ ክፍያ (ብር)"] = REGISTRATION_FEE
        member["የተበደረ ብር"] = 0.0
        member["10% የብድር ክፍያ (ብር)"] = 0.0
        member["በእጅ የተሰጠ 90% (ብር)"] = 0.0
        member["የብድር ጊዜ (ወር)"] = 0
        member["የብድር ወርሃዊ ክፍያ (ብር)"] = 0.0
        member["የቀረው ዋና ብድር (ብር)"] = 0.0
        member["የቀረው ዕዳ (ብር)"] = 0.0
        member["የተከፈለ ወለድ (ብር)"] = 0.0
        member["የተከፈለ ዋና ብድር (ብር)"] = 0.0
        member["የተበደረበት ቀን"] = ""
        members.append(normalize_member(member))
    return members

# ============================================================
# LOAN CALCULATION
# ============================================================

def calculate_monthly_payment(principal, months, rate=INTEREST_RATE):
    principal = safe_float(principal)
    if principal <= 0 or months <= 0:
        return 0.0
    if rate == 0:
        return principal / months
    payment = principal * rate * ((1 + rate) ** months) / (((1 + rate) ** months) - 1)
    return payment

def calculate_current_interest(member):
    remaining_principal = safe_float(member.get("የቀረው ዋና ብድር (ብር)", 0))
    return remaining_principal * INTEREST_RATE

# ============================================================
# LOAN PAYMENT
# ============================================================

def apply_loan_payment(member, payment_amount):
    payment_amount = safe_float(payment_amount)
    if payment_amount <= 0:
        return {"success": False, "message": "የክፍያ መጠን ከ0 በላይ መሆን አለበት።"}
    remaining_principal = safe_float(member.get("የቀረው ዋና ብድር (ብር)", 0))
    if remaining_principal <= 0:
        return {"success": False, "message": "ይህ አባል የሚከፈል የቀረ ብድር የለውም።"}

    interest_due = remaining_principal * INTEREST_RATE
    interest_paid = min(payment_amount, interest_due)
    remaining_payment = payment_amount - interest_paid
    principal_paid = min(remaining_payment, remaining_principal)
    actual_payment = interest_paid + principal_paid
    new_remaining_principal = max(0.0, remaining_principal - principal_paid)

    member["የቀረው ዋና ብድር (ብር)"] = new_remaining_principal
    member["የቀረው ዕዳ (ብር)"] = new_remaining_principal
    member["የተከፈለ ወለድ (ብር)"] = safe_float(member.get("የተከፈለ ወለድ (ብር)", 0)) + interest_paid
    member["የተከፈለ ዋና ብድር (ብር)"] = safe_float(member.get("የተከፈለ ዋና ብድር (ብር)", 0)) + principal_paid

    return {
        "success": True,
        "payment": actual_payment,
        "interest": interest_paid,
        "principal": principal_paid,
        "remaining": new_remaining_principal
    }

# ============================================================
# EXCEL SAVE & LOAD
# ============================================================

def save_data_to_excel(members, payment_history=None):
    if payment_history is None:
        payment_history = []
    member_df = pd.DataFrame(members)
    preferred_columns = ["የአባል ቁጥር", "ስም", "ብሔራዊ መታወቂያ", "ፎቶ", "የመመዝገቢያ ክፍያ (ብር)"] + MONTHS + [
        "የተበደረ ብር", "10% የብድር ክፍያ (ብር)", "በእጅ የተሰጠ 90% (ብር)", "የብድር ጊዜ (ወር)", 
