# 🎓 EduQuest | StudyTrack Dashboard

**Current Version:** Milestone 4  
**License:** MIT License

## 📖 Project Overview
**StudyTrack** is an AI-powered academic analytics dashboard designed to help students and teachers optimize study habits. By analyzing daily activities—such as study hours, sleep patterns, social media usage, and exercise—the system uses Machine Learning (Linear Regression) to predict potential academic scores and generates personalized, actionable recommendations.

## 🚀 Milestone 4 Updates
This release focuses on **Security** and **User Interface Experience**:
- **🔐 Secure Authentication:** Implemented a full Login and Registration system using Session State and JSON-based user management.
- **🎨 Modern UI Overhaul:** Integrated a custom "Dark Mode" aesthetic with CSS injection for a professional, dashboard-style look.
- **📄 Licensing:** Added MIT License for open-source distribution.

## ✨ Key Features
1.  **Smart Predictions:** Predicts student marks (0-100%) based on input habits.
2.  **Interactive Visualization:** Radar charts and trend analysis using Plotly.
3.  **Batch Processing:** Allows teachers to upload a CSV of an entire class to identify "At Risk" vs. "Top Performing" students instantly.
4.  **PDF Reports:** Generates downloadable PDF reports with AI-driven advice.
5.  **System Workflow:** Visual representation of the Data -> Preprocessing -> ML pipeline.

## 🛠️ Tech Stack
-   **Frontend:** Streamlit, Custom HTML/CSS
-   **Backend:** Python
-   **Machine Learning:** Scikit-Learn (Linear Regression)
-   **Data Manipulation:** Pandas, NumPy
-   **Visualization:** Plotly Graph Objects

## 📂 Project Structure
```text
EduQuest_Milestone4/
├── app.py                  # Main application source code
├── study_habit_model.pkl   # Pre-trained Machine Learning model
├── users.json              # Database for user credentials
├── requirements.txt        # List of Python dependencies
├── LICENSE                 # MIT License file
└── README.md               # Project documentation

```

## ⚙️ How to Run Locally

1. **Install Dependencies:**
Open your terminal/command prompt in the project folder and run:
```bash
pip install -r requirements.txt

```
2. **Run the Application:**
Execute the following command:
```bash
streamlit run app.py

```
3. **Access the Dashboard:**
The app will open in your browser at `http://localhost:8501`.

## 👤 Default Login Credentials

To test the admin features immediately:

* **Email:** `admin@eduquest.com`
* **Password:** `123`
*(Note: You can also register a new user via the "Sign Up" button)*

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.
