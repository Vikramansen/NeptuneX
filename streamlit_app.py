import streamlit as st
import pandas as pd
import os
import hashlib
import csv
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import subprocess
import tempfile
import openai

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Predefined advertisement categories
ad_categories = [
    "Technology & Electronics", "Health & Wellness", "Finance & Insurance",
    "Automotive & Transport", "Education & Learning", "Entertainment & Media",
    "Food & Beverages", "Travel & Tourism", "Retail & Consumer Goods",
    "Beauty & Personal Care", "Home & Garden", "Sports & Fitness",
    "Real Estate & Housing", "Professional Services", "Energy & Environment",
    "Uncategorized"
]

# User credentials and data files directory
credentials_path = 'user_credentials.csv'
if not os.path.exists(credentials_path):
    with open(credentials_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Username', 'PasswordHash'])

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_credentials():
    creds = {}
    with open(credentials_path, mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            creds[row['Username']] = row['PasswordHash']
    return creds
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hash_password("adminpassword")  # Use the hash_password function to hash the admin password

def admin_login():
    st.sidebar.title("Admin Login")
    username = st.sidebar.text_input("Admin Username", key="admin_username")
    password = st.sidebar.text_input("Admin Password", type="password", key="admin_password")
    if st.sidebar.button("Login as Admin"):
        if username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD_HASH:
            st.session_state["admin_logged_in"] = True
            st.success("Logged in as Admin")
        else:
            st.error("Incorrect Admin credentials")

def admin_page():
    st.title("Admin Dashboard")
    
    # Display all users
    creds = load_user_credentials()
    st.subheader("All Users")
    all_users = list(creds.keys())
    st.write(all_users)
    
    # Allow admin to download user data
    user_selection = st.selectbox("Select a user to download their data:", [""] + all_users)
    if user_selection:
        user_prefs_file, user_count_file = f'{user_selection}_preferences.csv', f'{user_selection}_category_count.csv'
        if st.button(f"Download {user_selection}'s Preferences"):
            with open(user_prefs_file) as f:
                st.download_button(label="Download Preferences", data=f.read(), file_name=f"{user_selection}_preferences.csv", mime='text/csv')
        if st.button(f"Download {user_selection}'s Category Count"):
            with open(user_count_file) as f:
                st.download_button(label="Download Category Count", data=f.read(), file_name=f"{user_selection}_category_count.csv", mime='text/csv')

    # Allow admin to view users interested in a specific category
    st.subheader("Filter Users by Category Interest")
    category = st.selectbox("Select a category:", [""] + ad_categories)
    if category:
        interested_users = []
        for user in all_users:
            user_count_file = f'{user}_category_count.csv'
            df = pd.read_csv(user_count_file)
            if not df[df['Category'] == category]['Count'].sum() == 0:
                interested_users.append(user)
        st.write(f"Users interested in {category}:", interested_users)

def sign_up():
    st.title("Sign Up")
    new_username = st.text_input("Choose a username", key="new_username_signup")
    new_password = st.text_input("Choose a password", type="password", key="new_password_signup")
    confirm_password = st.text_input("Confirm password", type="password", key="confirm_password_signup")

    if st.button("Sign Up"):
        if new_password == confirm_password:
            creds = load_user_credentials()
            if new_username in creds:
                st.error("Username already exists.")
            else:
                with open(credentials_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([new_username, hash_password(new_password)])
                st.success("User created successfully. You can now log in.")
        else:
            st.error("Passwords do not match.")

def login():
    username = st.sidebar.text_input("Username", key="username_login")
    password = st.sidebar.text_input("Password", type="password", key="password_login")
    if st.sidebar.button("Login"):
        user_credentials = load_user_credentials()
        if username in user_credentials and user_credentials[username] == hash_password(password):
            st.session_state["username"] = username
            initialize_user_files(username)
            # Directly go to the Voice Assistant page after login
            st.session_state["navigation"] = "Voice Assistant"
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")

def initialize_user_files(username):
    user_prefs_file = f'{username}_preferences.csv'
    user_count_file = f'{username}_category_count.csv'
    if not os.path.exists(user_prefs_file):
        pd.DataFrame({'Category': ad_categories[:-1], 'Preference': [False] * (len(ad_categories) - 1)}).to_csv(user_prefs_file, index=False)
    if not os.path.exists(user_count_file):
        pd.DataFrame({'Category': ad_categories, 'Count': [0] * len(ad_categories)}).to_csv(user_count_file, index=False)

def get_user_files():
    username = st.session_state.get("username", "default")
    return f'{username}_preferences.csv', f'{username}_category_count.csv'

def voice_assistant_page():
    st.title("Voice Assistant")
    audio_data = audio_recorder()
    if audio_data is not None:
        st.audio(audio_data, format='audio/webm')
        if st.button('Transcribe and Classify'):
            with st.spinner('Processing...'):
                text, error = process_audio(audio_data)
                if text:
                    st.success(f"Recognized Text: {text}")
                    category = classify_query(text)
                    st.markdown(f"**Category:** {category}")
                else:
                    st.error(error)

def ad_preferences_page():
    user_prefs_file, _ = get_user_files()
    st.title("Ad Preferences")
    user_prefs = pd.read_csv(user_prefs_file).set_index('Category')['Preference'].to_dict()
    new_prefs = {category: st.checkbox(category, value=user_prefs.get(category, False)) for category in ad_categories[:-1]}  # Exclude "Uncategorized"
    if st.button('Save Preferences'):
        pd.DataFrame.from_dict(new_prefs, orient='index', columns=['Preference']).reset_index().rename(columns={'index': 'Category'}).to_csv(user_prefs_file, index=False)
        st.success("Your preferences have been saved.")
def category_count_page():
    _, user_count_file = get_user_files()
    st.title("Category Count")
    df = pd.read_csv(user_count_file)
    st.dataframe(df)
    st.download_button(label="Download Category Count", data=df.to_csv(index=False), file_name="category_count.csv", mime='text/csv')

def process_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name
    wav_path = convert_webm_to_wav(temp_audio_path)
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text, None
        except sr.UnknownValueError:
            return None, "Google Speech Recognition could not understand audio."
        except sr.RequestError as e:
            return None, f"Could not request results from Google Speech Recognition service; {e}"

def convert_webm_to_wav(webm_path):
    temp_wav = tempfile.NamedTemporaryFile(delete=True, suffix='.wav').name
    command = ['ffmpeg', '-y', '-i', webm_path, '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '1', temp_wav]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return temp_wav
    else:
        print(f"ffmpeg error: {result.stderr}")
        return None

def classify_query(query):
    openai.api_key = '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'  # Replace with your actual OpenAI API key
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=f"Classify the following user query into categories: {', '.join(ad_categories)}. Query: '{query}'",
        max_tokens=60,
        temperature=0.7
    )
    category_response = response.choices[0].text.strip()
    matched_category = "Uncategorized"
    for category in ad_categories:
        if category_response.lower() in category.lower():
            matched_category = category
            break
    update_category_count(matched_category)
    return matched_category

def update_category_count(category):
    _, user_count_file = get_user_files()
    df = pd.read_csv(user_count_file)
    if category in df['Category'].values:
        df.loc[df['Category'] == category, 'Count'] += 1
    else:
        df = df.append({'Category': category, 'Count': 1}, ignore_index=True)
    df.to_csv(user_count_file, index=False)

# Main application flow
# Assuming all previously defined functions and initializations are in place

# Main application flow
if "admin_logged_in" in st.session_state:
    # Display the admin dashboard if an admin is logged in
    admin_page()
elif "username" in st.session_state:
    # Display user-specific pages if a regular user is logged in
    pages = {
        "Voice Assistant": voice_assistant_page,
        "Ad Preferences": ad_preferences_page,
        "Category Count": category_count_page,
    }
    # Default to Voice Assistant page if no specific page is selected yet
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'Voice Assistant'
    
    page = st.sidebar.selectbox("Navigate", list(pages.keys()), index=list(pages.keys()).index(st.session_state['current_page']))
    st.session_state['current_page'] = page
    pages[page]()

    if st.sidebar.button("Logout"):
        # Clear the session state to log out the user
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
else:
    # If no user is logged in, display the login, sign-up, and admin login options
    auth_action = st.sidebar.selectbox("Action", ["Login", "Sign Up", "Admin Login"])
    if auth_action == "Sign Up":
        sign_up()
    elif auth_action == "Login":
        login()
    elif auth_action == "Admin Login":
        admin_login()

    # Provide the ability to switch between login and sign-up without having to refresh or reset the app state
    if auth_action in ["Login", "Sign Up"]:
        if st.sidebar.button("Switch to Sign Up" if auth_action == "Login" else "Switch to Login"):
            st.session_state['auth_status'] = "Sign Up" if auth_action == "Login" else "Login"
            st.experimental_rerun()
