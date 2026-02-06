import streamlit as st
import pandas as pd
import datetime
import time
import requests
import io
import base64  # <--- Η απαραίτητη προσθήκη για το AutoPlay
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# --- 1. ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ & CONFIGURATION ---
st.set_page_config(
    page_title="Creta Gas AI Knowledge Hub", 
    page_icon="🔥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SECURITY & API HANDLING (GITHUB SAFE) ---
# Ο κώδικας ψάχνει τα κλειδιά στα "Secrets" του Cloud.
if "OPENAI_API_KEY" in st.secrets and "ELEVENLABS_API_KEY" in st.secrets:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    elevenlabs_api_key = st.secrets["ELEVENLABS_API_KEY"]
else:
    # Αν τρέχει και δεν βρίσκει κλειδιά
    st.error("⚠️ SYSTEM HALT: Missing API Keys in Streamlit Secrets.")
    st.info("Παρακαλώ πηγαίνετε: Settings -> Secrets και προσθέστε τα OPENAI_API_KEY & ELEVENLABS_API_KEY")
    st.stop()

# Σύνδεση με το "Μυαλό" (OpenAI)
try:
    client = OpenAI(api_key=openai_api_key)
except Exception as e:
    st.error(f"❌ Critical Connection Error: {e}")
    st.stop()

# --- 3. DATA LAYER (MOCK DATABASE) ---
def create_mock_database():
    # Προσομοίωση βάσης δεδομένων SoftOne (ERP)
    data_softone = {
        "id": [101, 102, 103, 104, 105],
        "name": ["Ταβέρνα 'Ο Νίκος'", "Blue Coast Hotel & Resort", "Πλαστικά Κρήτης ΑΒΕΕ", "Super Market ΑΦΟΙ", "Cafe Αμάν"],
        "balance": [450.50, 12500.00, 5000.00, 0.00, 120.00],
        "currency": ["EUR", "EUR", "EUR", "EUR", "EUR"],
        "status": ["Overdue", "Active", "Active", "Active", "Overdue"],
        "last_payment": ["2023-10-01", "2023-11-15", "2023-11-20", "2023-11-22", "2023-09-10"]
    }
    
    # Προσομοίωση CRM / Συμφωνιών
    data_agreements = {
        "customer_id": [101, 102, 103, 104, 105],
        "agreement_note": [
            "⚠️ ΠΡΟΣΟΧΗ: Μόνο μετρητοίς (Blacklist Candidate)", 
            "💎 VIP Συμφωνία: 5% Έκπτωση λόγω γνωριμίας CEO", 
            "🏭 Συμβόλαιο Βιομηχανικού - Τιμή Ζώνης Β", 
            "🆕 Νέος πελάτης - Υπό δοκιμή", 
            "📄 Παλιά συμφωνία - Χωρίς έκπτωση"
        ],
        "logistics_note": [
            "🚛 Είσοδος από πίσω πόρτα κουζίνας", 
            "⏰ Παράδοση 08:00-10:00 αυστηρά", 
            "🚜 Χρειάζεται κλαρκ - Προτεραιότητα 4ωρου", 
            "✅ Εύκολη πρόσβαση - Ράμπα", 
            "⚠️ Στενό δρομάκι - Μόνο μικρό φορτηγό (Van)"
        ],
        "contact_person": ["Κος Νίκος", "κα Μαρία (Λογιστήριο)", "Κος Γιώργος (Αποθήκη)", "Κος Γιάννης", "Κος Στράτος"]
    }

    df1 = pd.DataFrame(data_softone)
    df2 = pd.DataFrame(data_agreements)
    # Join tables (ERP + CRM)
    return pd.merge(df1, df2, left_on="id", right_on="customer_id", how="left")

full_data = create_mock_database()

# --- 4. EXTRAS: AUTOPLAY AUDIO FUNCTION (NEW FEATURE) ---
# Αυτή η συνάρτηση επιτρέπει στον ήχο να παίζει αυτόματα χωρίς κλικ
def autoplay_audio(audio_content):
    # Μετατροπή των bytes σε base64 string
    b64 = base64.b64encode(audio_content).decode()
    # Δημιουργία κρυφού HTML player που κάνει autoplay
    md = f"""
        <audio controls autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

# --- 5. UI SIDEBAR & SECURITY LAYER ---
st.title("🔥 Creta Gas: Enterprise AI Hub")
st.markdown("### *Unified Intelligence: ERP + CRM + ElevenLabs Voice*")
st.markdown("---")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.header("⚙️ Control Center")
    st.divider()
    
    # User Access Control
    st.subheader("👤 Identity Management")
    user_role = st.selectbox(
        "Επιλέξτε Ρόλο Χρήστη:", 
        ["CEO (God Mode)", "Sales Manager", "Driver (Field Ops)"]
    )
    
    # Visual Feedback για τον ρόλο
    if "CEO" in user_role:
        st.success("🟢 Full Access Granted")
    elif "Sales" in user_role:
        st.info("🔵 Sales Access Granted")
    else:
        st.error("🔴 Driver Access (Restricted)")

    st.divider()

    # --- ΡΥΘΜΙΣΕΙΣ ΦΩΝΗΣ (ELEVENLABS) ---
    st.subheader("🔊 Audio Configuration")
    
    # Λίστα με IDs της ElevenLabs
    voice_options = {
        "Rachel (Αμερικάνικη/Καθαρή)": "21m00Tcm4TlvDq8ikWAM",
        "Charlie (Αντρική/Ήρεμη)": "IKne3meq5aSn9XLyUdCD",
        "Nicole (Επαγγελματική)": "piTKgcLEGmPE4e6mEKli",
        "Mimi (Παιδική)": "zrHiDhphv9ZnVXBqCLjf"
    }
    
    selected_voice_name = st.selectbox("Επιλογή Φωνής AI:", list(voice_options.keys()))
    selected_voice_id = voice_options[selected_voice_name]
    
    st.caption(f"Voice Engine: ElevenLabs Multilingual v2\nID: {selected_voice_id}")


# --- 6. CORE AI ENGINE ---

# (Α) Whisper (Speech to Text)
def transcribe_audio_whisper(audio_bytes):
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "voice_input.wav" 
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            language="el"
        )
        return transcript.text
    except Exception as e:
        return f"Audio Error: {e}"

# (Β) ElevenLabs (Text to Speech)
def generate_elevenlabs_audio(text, api_key, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", 
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            # Επιστροφή λάθους για Debugging
            st.error(f"ElevenLabs Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# (Γ) GPT-4o Logic (The Brain)
def get_smart_response(user_query, context_data, role):
    # Dynamic Security Protocol
    if "Driver" in role:
        security_protocol = "SECURITY: Do NOT reveal money/balances. Focus on Logistics/Location only."
    elif "Sales" in role:
        security_protocol = "SECURITY: Reveal balances. Focus on Sales/Negotiation."
    else:
        security_protocol = "SECURITY: Full Access. No restrictions."

    system_message = f"""
    ROLE: You are the advanced AI Assistant of Creta Gas.
    CONTEXT DATA: {context_data.to_string()}
    SECURITY: {security_protocol}
    INSTRUCTIONS:
    1. Language: Greek (Ελληνικά).
    2. Tone: Professional but natural.
    3. Length: Short and concise (Max 2 sentences).
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: {str(e)}"

# --- 7. INTERFACE & INTERACTION ---

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT SECTION ---
st.markdown("### 🎙️ Voice Command Center")

col_mic, col_text = st.columns([1, 4])
prompt = None

with col_mic:
    # Καταγραφή ήχου
    audio_data = mic_recorder(
        start_prompt="🎤 PUSH TO TALK",
        stop_prompt="⏹️ RELEASE", 
        key='recorder',
        just_once=True,
        use_container_width=True
    )

with col_text:
    text_input = st.chat_input("Type your query or use voice above...")

if audio_data:
    with st.spinner("🎧 Processing Audio Stream..."):
        prompt = transcribe_audio_whisper(audio_data['bytes'])
elif text_input:
    prompt = text_input

# --- EXECUTION LOOP ---
if prompt:
    # 1. Εμφάνιση ερώτησης χρήστη
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Σκέψη AI & Latency Check
    start_time = time.time()
    with st.spinner('🧠 Analyzing Data & Security Protocols...'):
        response_text = get_smart_response(prompt, full_data, user_role)
    end_time = time.time()
    latency = round(end_time - start_time, 2)

    # 3. Εμφάνιση απάντησης & Ήχος
    with st.chat_message("assistant"):
        st.markdown(response_text)
        
        # --- ElevenLabs Generation DISABLED (COMMENTED OUT) ---
        # with st.spinner(f"🔊 Synthesizing Voice ({selected_voice_name})..."):
        #     audio_bytes = generate_elevenlabs_audio(response_text, elevenlabs_api_key, selected_voice_id)
        #     
        #     if audio_bytes:
        #         # ΧΡΗΣΗ ΤΗΣ ΝΕΑΣ ΛΕΙΤΟΥΡΓΙΑΣ AUTOPLAY
        #         autoplay_audio(audio_bytes)
        #     else:
        #         st.warning("⚠️ Voice Generation Failed (Check Logs).")
        
        # --- LOGS & DEBUGGING (COMPLETE ENTERPRISE VIEW) ---
        with st.expander("🛠️ System Logs (Debug Info)"):
            st.code(f"""
            [INFO] Timestamp: {datetime.datetime.now()}
            [INFO] User Role: {user_role}
            [INFO] Latency: {latency}s
            [VOICE] Provider: ElevenLabs (DISABLED)
            [VOICE] Model: eleven_multilingual_v2
            [VOICE] ID: {selected_voice_id}
            """, language="yaml")

    st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- ΤΟ DATA LAKE ---
st.markdown("---")
with st.expander("📂 View Raw Data Lake (Database Inspection)"):
    st.dataframe(full_data)