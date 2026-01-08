import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import base64
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from fpdf import FPDF
import plotly.graph_objects as go

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="EduQuest | Study Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS: MODERN UI, DARK MODE, CLEAN TABS ---
st.markdown("""
    <style>
    /* 1. HEADER STYLES */
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0px;
        font-family: 'Helvetica Neue', sans-serif;
        background: -webkit-linear-gradient(45deg, #3498db, #9b59b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .tagline {
        text-align: center;
        font-size: 1.3rem;
        color: #7F8C8D;
        font-style: italic;
        margin-bottom: 40px;
    }

    /* 2. CLEAN TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 40px;
        justify-content: center;
        border-bottom: 1px solid #ddd;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent !important;
        border: none !important;
        font-size: 18px;
        font-weight: 600;
        color: #555;
    }
    .stTabs [aria-selected="true"] {
        color: #2980B9 !important;
        border-bottom: 3px solid #2980B9 !important;
    }

    /* 3. FEATURE CARDS */
    .feature-card {
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        height: 320px;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature-card:hover { transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0,0,0,0.2); }

    /* LIGHT/DARK MODE HANDLERS */
    .feature-card { background-color: #FFFFFF; border: 1px solid #EAEDED; }
    .feature-title { font-size: 1.4rem; font-weight: 700; margin-bottom: 15px; color: #34495E; }
    .feature-desc { font-size: 1rem; color: #7F8C8D; line-height: 1.6; }
    .feature-icon { font-size: 3.5rem; margin-bottom: 15px; color: #2980B9; }

    @media (prefers-color-scheme: dark) {
        .feature-card { background-color: #262730; border: 1px solid #4F4F4F; }
        .feature-title { color: #FAFAFA !important; }
        .feature-desc { color: #E0E0E0 !important; }
        .feature-icon { color: #5DADE2 !important; }
        .tagline { color: #B0B0B0 !important; }
    }

    /* 4. METRIC BOXES */
    .metric-box {
        padding: 15px; border-radius: 5px; margin-bottom: 10px;
        background-color: #f0f2f6; border-left: 5px solid #2980b9; color: #31333F;
    }

    /* 5. KPI BOX (For Batch Stats) */
    .kpi-box {
        background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 12px; padding: 20px; text-align: center;
    }
    @media (prefers-color-scheme: dark) {
        .kpi-box { background: #1e1e1e; border: 1px solid #333; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE & DATABASE
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""
if 'email' not in st.session_state: st.session_state['email'] = ""
if 'auth_mode' not in st.session_state: st.session_state['auth_mode'] = 'login'

USER_DB_FILE = 'users.json'


# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def load_users():
    if not os.path.exists(USER_DB_FILE):
        return {"admin": {"password": "123", "email": "admin@eduquest.com"}}
    with open(USER_DB_FILE, 'r') as f:
        return json.load(f)


def save_new_user(username, email, password):
    users = load_users()
    users[username] = {"password": password, "email": email}
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f)


def check_login(login_input, password):
    users = load_users()
    if login_input in users:
        if users[login_input]['password'] == password:
            return True, login_input, users[login_input]['email']
    for u, data in users.items():
        if data.get('email') == login_input and data.get('password') == password:
            return True, u, data['email']
    return False, None, None


def toggle_auth_mode():
    st.session_state['auth_mode'] = 'register' if st.session_state['auth_mode'] == 'login' else 'login'


@st.cache_resource
def load_model():
    try:
        return joblib.load('study_habit_model.pkl')
    except:
        return None


def train_model(df):
    X = df[['Study_Hours', 'Sleep_Hours', 'Social_Media_Hours', 'Exercise_Hours', 'Attention_Level']]
    y = df['Marks']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)
    joblib.dump(model, 'study_habit_model.pkl')
    return model, r2, mae, X.columns, model.coef_


# --- PDF GENERATOR ---
def generate_pdf(student_name, prediction, input_data, advice):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_left_margin(10);
    pdf.set_right_margin(10)
    printable_width = 190

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(printable_width, 10, txt="EduQuest Student Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(printable_width, 10, txt=f"Student Name: {student_name}", ln=True)
    pdf.cell(printable_width, 10, txt=f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(printable_width, 10, txt=f"Predicted Score: {prediction:.2f} / 100", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.cell(printable_width, 10, txt="Input Habits:", ln=True)
    headers = ['Study Hours', 'Sleep Hours', 'Social Media', 'Exercise', 'Attention']
    values = input_data[0]
    for h, v in zip(headers, values):
        pdf.cell(printable_width, 8, txt=f"- {h}: {v}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(printable_width, 10, txt="AI Recommendations:", ln=True)
    pdf.set_font("Arial", size=12)

    for item in advice:
        clean_text = item.replace('**', '').encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(printable_width, 8, txt="- " + clean_text)

    return pdf.output(dest='S')


def get_recommendations(study, sleep, social, exercise, attention):
    recs = []
    if study < 4: recs.append("📚 **Increase Study Time:** Aim for 4-6 hours.")
    if study > 9: recs.append("⚠️ **Avoid Burnout:** Take breaks every 50 minutes.")
    if sleep < 6: recs.append("😴 **Sleep More:** < 6 hours hurts memory.")
    if social > 3: recs.append("📵 **Cut Social Media:** High usage (>3 hrs) kills focus.")
    if exercise < 1: recs.append("🏃 **Exercise:** Even 30 mins walking boosts brain power.")
    if attention < 6: recs.append("🧘 **Focus Training:** Try meditation or Pomodoro.")
    if not recs: recs.append("🌟 **Perfect Habits!** Keep it up!")
    return recs


def plot_radar_chart(input_values):
    categories = ['Study', 'Sleep', 'Social', 'Exercise', 'Attention']
    max_vals = [12, 10, 10, 2, 10]
    norm_vals = [v / m for v, m in zip(input_values, max_vals)]
    ideal_vals = [8 / 12, 8 / 10, 1 / 10, 1 / 2, 9 / 10]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=norm_vals, theta=categories, fill='toself', name='You', line_color='#3498db'))
    fig.add_trace(
        go.Scatterpolar(r=ideal_vals, theta=categories, fill='toself', name='Top Performer', line_color='#2ecc71',
                        opacity=0.4))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, height=300,
                      margin=dict(l=40, r=40, t=20, b=20))
    return fig


# --- HELPER FOR KPI DISPLAY ---
def kpi_metric(label, value):
    st.markdown(f"""
    <div class="kpi-box">
        <div style="font-size:0.9rem; color:#888;">{label}</div>
        <div style="font-size:1.8rem; font-weight:bold;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 4. MAIN APP LOGIC
# ==========================================

# --- PART A: AUTHENTICATION ---
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1>🎓 EduQuest</h1></div>",
                    unsafe_allow_html=True)
        container = st.container(border=True)

        if st.session_state['auth_mode'] == 'login':
            with container:
                st.subheader("Sign In")
                with st.form("login_form"):
                    login_input = st.text_input("Username or Email")
                    pw = st.text_input("Password", type="password")
                    if st.form_submit_button("Login", use_container_width=True):
                        is_valid, user, email = check_login(login_input, pw)
                        if is_valid:
                            st.session_state['username'] = user
                            st.session_state['email'] = email
                            st.session_state['logged_in'] = True
                            st.rerun()
                        else:
                            st.error("Invalid Credentials")
                st.markdown("---")
                if st.button("New User? Register Here", type="tertiary"): toggle_auth_mode(); st.rerun()
        else:
            with container:
                st.subheader("Create Account")
                with st.form("reg_form"):
                    new_user = st.text_input("Username")
                    new_email = st.text_input("Email")
                    new_pw = st.text_input("Password", type="password")
                    conf_pw = st.text_input("Confirm Password", type="password")
                    if st.form_submit_button("Register", use_container_width=True):
                        users = load_users()
                        if new_user in users:
                            st.error("Username taken.")
                        elif new_pw != conf_pw:
                            st.error("Passwords mismatch.")
                        elif len(new_pw) < 6:
                            st.error("Password too weak.")
                        else:
                            save_new_user(new_user, new_email, new_pw); st.success("Created! Login now.")
                st.markdown("---")
                if st.button("Back to Login", type="tertiary"): toggle_auth_mode(); st.rerun()

# --- PART B: DASHBOARD ---
else:
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        st.markdown(f"<h3 style='margin:0; padding:0; color:#2c3e50;'>{st.session_state['username']}</h3>",
                    unsafe_allow_html=True)
        st.caption(st.session_state['email'])
        st.markdown("---")
        if st.button("Logout", use_container_width=True): st.session_state['logged_in'] = False; st.rerun()

    st.markdown("<div class='main-title'>Student Study Habit Tracker</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='tagline'>Empowering students to optimize their habits and achieve academic excellence through AI</div>",
        unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Home", "Train Model", "Visualization", "Prediction"])

    # --- TAB 1: HOME ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        with c1: st.markdown(
            """<div class="feature-card"><div class="feature-icon">📊</div><div class="feature-title">Smart Analytics</div><div class="feature-desc">Visualize trends in sleep, study, and focus to understand performance.</div></div>""",
            unsafe_allow_html=True)
        with c2: st.markdown(
            """<div class="feature-card"><div class="feature-icon">🔮</div><div class="feature-title">AI Prediction</div><div class="feature-desc">Predict future grades with high accuracy based on daily habits.</div></div>""",
            unsafe_allow_html=True)
        with c3: st.markdown(
            """<div class="feature-card"><div class="feature-icon">🧩</div><div class="feature-title">Clustering</div><div class="feature-desc">Group students into distinct profiles like 'Top Performers' or 'At Risk'.</div></div>""",
            unsafe_allow_html=True)
        with c4: st.markdown(
            """<div class="feature-card"><div class="feature-icon">💡</div><div class="feature-title">Recommendations</div><div class="feature-desc">Get personalized, actionable advice to improve efficiency.</div></div>""",
            unsafe_allow_html=True)

    # --- TAB 2: TRAIN ---
    with tab2:
        st.header("⚙️ Train Your Model")
        train_file = st.file_uploader("Upload Dataset (CSV)", type=['csv'])
        if train_file:
            try:
                df_train = pd.read_csv(train_file)
                df_train.columns = df_train.columns.str.strip()
                required = ['Study_Hours', 'Sleep_Hours', 'Social_Media_Hours', 'Exercise_Hours', 'Attention_Level',
                            'Marks']
                if not all(col in df_train.columns for col in required):
                    st.error(f"CSV must contain columns: {required}")
                else:
                    if st.button("Start Training"):
                        with st.spinner("Training..."):
                            model, r2, mae, feats, coefs = train_model(df_train)
                            st.success("Training Complete!")
                            m1, m2 = st.columns(2)
                            m1.markdown(f"<div class='metric-box'><b>Accuracy (R2):</b> {r2:.2f}</div>",
                                        unsafe_allow_html=True)
                            m2.markdown(f"<div class='metric-box'><b>Avg Error:</b> +/- {mae:.2f} Marks</div>",
                                        unsafe_allow_html=True)
                            st.subheader("Feature Importance")
                            imp_df = pd.DataFrame({'Feature': feats, 'Impact': coefs}).sort_values('Impact',
                                                                                                   ascending=False)
                            st.bar_chart(imp_df.set_index('Feature'))
            except Exception as e:
                st.error(f"Error: {e}")

    # --- TAB 3: VISUALIZATION ---
    with tab3:
        st.header("📊 Data Insights")
        viz_file = st.file_uploader("Upload Data for Viz", type=['csv'], key="viz")
        if viz_file:
            df_viz = pd.read_csv(viz_file)
            st.subheader("Actual vs Predicted")
            model = load_model()
            if model:
                try:
                    df_viz.columns = df_viz.columns.str.strip()
                    X_v = df_viz[
                        ['Study_Hours', 'Sleep_Hours', 'Social_Media_Hours', 'Exercise_Hours', 'Attention_Level']]
                    df_viz['Predicted'] = model.predict(X_v)
                    st.line_chart(df_viz[['Marks', 'Predicted']].head(30))
                except:
                    st.warning("Columns mismatch for prediction.")
            c1, c2 = st.columns(2)
            with c1:
                st.scatter_chart(df_viz, x='Study_Hours', y='Marks')
            with c2:
                st.bar_chart(df_viz['Sleep_Hours'].value_counts())

    # --- TAB 4: PREDICTION (DUAL MODE WITH ROBUST BATCH LOGIC) ---
    with tab4:
        st.header("🎯 Smart Prediction")
        mode = st.radio("Select Mode:", ["👤 Individual Prediction", "👥 Batch Prediction (Group)"], horizontal=True)
        st.markdown("---")
        model = load_model()

        if mode == "👤 Individual Prediction":
            col_in, col_res = st.columns([1, 1], gap="large")
            with col_in:
                st.subheader("Student Details")
                p_name = st.text_input("Name")
                p_study = st.slider("📚 Study Hours", 0.0, 12.0, 4.0)
                p_sleep = st.slider("😴 Sleep Hours", 3.0, 10.0, 7.0)
                p_social = st.slider("📱 Social Media", 0.0, 10.0, 2.0)
                p_ex = st.slider("🏃 Exercise", 0.0, 2.0, 1.0)
                p_att = st.slider("🧘 Attention (1-10)", 1, 10, 6)
            with col_res:
                if st.button("🚀 Predict Result"):
                    if model:
                        vals = [p_study, p_sleep, p_social, p_ex, p_att]
                        score = model.predict([vals])[0]
                        score = max(0, min(100, score))
                        st.metric("Predicted Score", f"{score:.2f} / 100")
                        st.progress(int(score))
                        st.plotly_chart(plot_radar_chart(vals), use_container_width=True)
                        if score < 90: st.info(
                            f"💡 **Tip:** Increasing Study by 1 hr might boost score by approx {model.coef_[0]:.2f} points!")
                        advice = get_recommendations(*vals)
                        with st.expander("View Recommendations"):
                            for tip in advice: st.write(tip)
                        pdf_bytes = generate_pdf(p_name if p_name else "Student", score, [vals], advice)
                        b64 = base64.b64encode(pdf_bytes).decode()
                        st.markdown(
                            f'<a href="data:application/pdf;base64,{b64}" download="Report.pdf">📄 Download PDF Report</a>',
                            unsafe_allow_html=True)
                    else:
                        st.error("Please train model first.")
        else:
            # --- BATCH PROCESSING (WITH AUTO-ID & AT-RISK TABLES) ---
            st.subheader("Upload Class Data")
            f_batch = st.file_uploader("Upload CSV for Batch Prediction", type=['csv'])

            if f_batch and model:
                try:
                    df = pd.read_csv(f_batch)
                    df.columns = df.columns.str.strip()

                    # 1. AUTO-DETECT OR GENERATE NAME
                    name_col = None
                    possible_names = ['Name', 'Student', 'Student Name', 'Student_Name', 'ID', 'Roll No']
                    for col in df.columns:
                        if col in possible_names:
                            name_col = col
                            break
                    if not name_col:
                        df['Student_ID'] = [f"Student {i + 1}" for i in range(len(df))]
                        name_col = 'Student_ID'
                        st.info("ℹ️ Generated Student IDs for tracking.")

                    # 2. PREDICT
                    preds = model.predict(
                        df[['Study_Hours', 'Sleep_Hours', 'Social_Media_Hours', 'Exercise_Hours', 'Attention_Level']])
                    df['Predicted'] = [max(0, min(100, p)) for p in preds]


                    def get_status(s):
                        if s < 50:
                            return "🔴 At Risk"
                        elif s < 75:
                            return "🟡 Average"
                        else:
                            return "🟢 On Track"


                    df['Status'] = df['Predicted'].apply(get_status)

                    # 3. METRICS
                    st.markdown("<br>", unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        kpi_metric("Class Average", f"{df['Predicted'].mean():.1f}")
                    with m2:
                        kpi_metric("Highest Score", f"{df['Predicted'].max():.1f}")
                    with m3:
                        kpi_metric("Lowest Score", f"{df['Predicted'].min():.1f}")
                    st.markdown("<hr>", unsafe_allow_html=True)

                    # 4. TABLES: AT RISK vs TOP PERFORMERS
                    c_risk, c_top = st.columns(2, gap="large")
                    with c_risk:
                        st.markdown("### ⚠️ Intervention Needed")
                        st.markdown("<small>Students below 50%</small>", unsafe_allow_html=True)
                        risk_df = df[df['Predicted'] < 50].sort_values(by='Predicted')
                        if not risk_df.empty:
                            st.dataframe(risk_df[[name_col, 'Predicted', 'Status']], hide_index=True,
                                         use_container_width=True)
                        else:
                            st.success("✅ No students at risk.")

                    with c_top:
                        st.markdown("### 🏆 Top Performers")
                        st.markdown("<small>Top 5 Students</small>", unsafe_allow_html=True)
                        top_df = df.sort_values(by='Predicted', ascending=False).head(5)
                        st.dataframe(top_df[[name_col, 'Predicted', 'Status']], hide_index=True,
                                     use_container_width=True)

                    # 5. FULL DATA
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.markdown("### 📋 Full Class Data")
                    st.dataframe(df, use_container_width=True)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Results CSV", csv, "class_results.csv", "text/csv")

                except Exception as e:
                    st.error(f"Error processing batch: {e}")
                    st.info(
                        "Ensure CSV has columns: Study_Hours, Sleep_Hours, Social_Media_Hours, Exercise_Hours, Attention_Level")