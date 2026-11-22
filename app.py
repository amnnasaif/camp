import calendar
import hmac
import json
import os
from datetime import date

import streamlit as st

st.set_page_config(page_title="حجوزات المخيم", page_icon="⛺", layout="centered")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "bookings.json")
MONTHS = [(2026, 11), (2026, 12), (2027, 1), (2027, 2), (2027, 3)]
MONTH_NAMES = {1: "يناير", 2: "فبراير", 3: "مارس", 11: "نوفمبر", 12: "ديسمبر"}
DAY_NAMES = ["أحد", "اثنين", "ثلاثاء", "أربعاء", "خميس", "جمعة", "سبت"]

st.markdown(
    """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"]{background:#FCF3E2 !important;}
.block-container{max-width:520px;padding-top:1.5rem;direction:rtl;}
#MainMenu, footer{visibility:hidden;}
.legend{display:flex;gap:18px;justify-content:center;margin:6px 0 18px;font-size:14px;color:#1a1512}
.legend i{display:inline-block;width:14px;height:14px;border-radius:4px;border:1.5px solid #1a1512;vertical-align:middle;margin-left:6px}
.legend i.b{background:#b8362b;border-color:#b8362b}
.month{background:#fff9ee;border:1px solid #e6d8bd;border-radius:16px;padding:14px 12px 16px;margin-bottom:16px}
.month h3{margin:2px 0 12px;font-size:19px;text-align:center;color:#1a1512}
.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;direction:rtl}
.dn{font-size:11px;color:#8a7d6b;text-align:center}
.d{aspect-ratio:1;display:flex;align-items:center;justify-content:center;border-radius:10px;border:1.5px solid #1a1512;font-size:15px;color:#1a1512}
.d.booked{background:#b8362b;border-color:#b8362b;color:#fff;font-weight:600}
.d.empty{border:none}
</style>
""",
    unsafe_allow_html=True,
)


def load():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save(booked):
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(sorted(booked), f)
    os.replace(tmp, DATA_FILE)


def month_html(y, m, booked):
    cal = calendar.Calendar(firstweekday=6)  # الأسبوع يبدأ الأحد
    cells = "".join(f'<div class="dn">{n}</div>' for n in DAY_NAMES)
    for d in cal.itermonthdates(y, m):
        if d.month != m:
            cells += '<div class="d empty"></div>'
        else:
            cls = "d booked" if d.isoformat() in booked else "d"
            cells += f'<div class="{cls}">{d.day}</div>'
    return f'<div class="month"><h3>{MONTH_NAMES[m]} {y}</h3><div class="grid">{cells}</div></div>'


def is_admin():
    return st.session_state.get("admin", False)


booked = load()

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.image(os.path.join(BASE, "logo.png"), use_container_width=True)

st.markdown(
    '<div class="legend"><span><i></i>متوفر</span><span><i class="b"></i>محجوز</span></div>',
    unsafe_allow_html=True,
)

for y, m in MONTHS:
    st.markdown(month_html(y, m, booked), unsafe_allow_html=True)

# ---------------- الأدمن ----------------
st.divider()
with st.expander("دخول الأدمن"):
    if not is_admin():
        pw = st.text_input("كلمة السر", type="password")
        if st.button("دخول"):
            real = st.secrets.get("ADMIN_PASSWORD", "")
            if real and hmac.compare_digest(pw.encode(), str(real).encode()):
                st.session_state["admin"] = True
                st.rerun()
            else:
                st.error("كلمة السر غلط")
    else:
        st.success("وضع الأدمن")
        new_booked = set()
        for y, m in MONTHS:
            days = calendar.monthrange(y, m)[1]
            options = list(range(1, days + 1))
            current = [d for d in options if date(y, m, d).isoformat() in booked]
            chosen = st.multiselect(
                f"الأيام المحجوزة - {MONTH_NAMES[m]} {y}",
                options,
                default=current,
                key=f"ms-{y}-{m}",
            )
            new_booked |= {date(y, m, d).isoformat() for d in chosen}
        a, b = st.columns(2)
        if a.button("حفظ", type="primary"):
            save(new_booked)
            st.rerun()
        if b.button("خروج"):
            st.session_state["admin"] = False
            st.rerun()
