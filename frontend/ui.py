import streamlit as st
import requests

# ---------------- CONFIG ---------------- #
API_BASE_URL = "https://churn-prediction-q232.onrender.com"

st.set_page_config(
    page_title="Customer Churn Predictor",
    page_icon="📊",
    layout="centered"
)

# ---------------- SESSION STATE ---------------- #
if "token" not in st.session_state:
    st.session_state.token = None

# ---------------- HELPERS ---------------- #
def api_post(endpoint, payload, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.post(f"{API_BASE_URL}{endpoint}", json=payload, headers=headers)

# ---------------- UI ---------------- #
st.title("📊 Customer Churn Prediction")
st.caption("FastAPI + JWT + ML Model + Streamlit")

tabs = st.tabs(["🔐 Login", "📝 Register", "📈 Predict Churn"])

# ---------------- LOGIN ---------------- #
with tabs[0]:
    st.subheader("Login")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        response = api_post("/login", {
            "username": username,
            "password": password
        })

        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.success("Login successful ✅")
        else:
            st.error(response.json()["detail"])

# ---------------- REGISTER ---------------- #
with tabs[1]:
    st.subheader("Register")

    r_user = st.text_input("New Username")
    r_pass = st.text_input("New Password", type="password")

    if st.button("Register"):
        response = api_post("/register", {
            "username": r_user,
            "password": r_pass
        })

        if response.status_code == 200:
            st.success("Registered successfully 🎉")
        else:
            st.error(response.json()["detail"])

# ---------------- PREDICTION ---------------- #
with tabs[2]:
    st.subheader("Predict Customer Churn")

    if not st.session_state.token:
        st.warning("⚠️ Please login first")
    else:
        with st.form("prediction_form"):
            Gender = st.selectbox("Gender", ["Male", "Female"])
            Age = st.slider("Age", 18, 100, 30)
            Tenure = st.slider("Tenure (Months)", 0, 100, 12)
            Services_Subscribed = st.slider("Services Subscribed", 0, 10, 3)
            Contract_Type = st.selectbox("Contract Type", ["Month-to-Month", "One year", "Two year"])
            MonthlyCharges = st.number_input("Monthly Charges", min_value=1.0, value=70.0)
            TotalCharges = st.number_input("Total Charges", min_value=0.0, value=1000.0)
            TechSupport = st.selectbox("Tech Support", ["Yes", "No"])
            OnlineSecurity = st.selectbox("Online Security", ["Yes", "No"])
            InternetService = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])

            submitted = st.form_submit_button("Predict")

        if submitted:
            payload = {
                "customer": {
                    "Gender": Gender,
                    "Age": Age,
                    "Tenure": Tenure,
                    "Services_Subscribed": Services_Subscribed,
                    "Contract_Type": Contract_Type,
                    "MonthlyCharges": MonthlyCharges,
                    "TotalCharges": TotalCharges,
                    "TechSupport": TechSupport,
                    "OnlineSecurity": OnlineSecurity,
                    "InternetService": InternetService
                }
            }

            response = api_post(
                "/predict/auth",
                payload,
                st.session_state.token
            )

            if response.status_code == 200:
                result = response.json()

                st.success(f"Prediction: **{result['churn_label']}**")
                st.metric("Churn Probability", round(result["churn_probablity"], 2))
            else:
                st.error(response.json()["detail"])
