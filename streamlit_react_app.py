# Import the necessary libraries
import streamlit as st  # For creating the web app interface
import base64

# --- Fungsi untuk mengonversi file biner (gambar) ke string Base64 ---
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- Konfigurasi Gambar Lokal ---
# Ganti dengan nama file PNG Anda: RoboPit.jpg
local_image_path = "RoboPit01.jpg"

# --- CSS Kustom untuk Latar Belakang Halaman dan Sidebar ---
try:
    bin_str = get_base64_of_bin_file(local_image_path)
    # Gunakan data:image/png;base64, diikuti dengan string Base64
    image_url_for_css = f"data:image/png;base64,{bin_str}"

    page_bg_image_and_sidebar_css = f"""
    <style>
    /* Gaya untuk latar belakang halaman utama (body) */
    body {{
        background-image: url("{image_url_for_css}");
     /*   background-size: cover;  Menutupi seluruh area tanpa terulang */
        background-repeat: no-repeat; /* Tidak mengulang gambar */
        background-attachment: fixed; /* Gambar tetap saat scroll */
        background-position: center; /* Posisikan gambar di tengah */
    }}

    /* Gaya untuk kontainer utama aplikasi Streamlit (agar konten mudah dibaca) */
    .stApp {{
        background-color: rgba(255, 255, 255, 0); /* Latar belakang semi-transparan putih */
        border-radius: 100px;
        padding: 10px;
    }}  

    /* Gaya untuk sidebar */
    .stSidebar > div:first-child {{
        background-color: rgba(240, 242, 246, 0.7); /* Warna abu-abu terang semi-transparan */
    }}
    </style>
    """
    # Suntikkan CSS kustom ke aplikasi Streamlit
    st.markdown(page_bg_image_and_sidebar_css, unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"Error: File gambar '{local_image_path}' tidak ditemukan.")
    st.info("Memuat dengan latar belakang standar.")
    # Opsional: Atur latar belakang default jika gambar tidak ditemukan
    # st.markdown("""<style>body { background-color: #f0f2f6; }</style>""", unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"Error: File gambar '{local_image_path}' tidak ditemukan.")
    st.info("Menggunakan latar belakang standar karena gambar tidak ditemukan.")
    # Jika gambar tidak ditemukan, Anda bisa menyuntikkan CSS default atau tidak melakukan apa-apa
    # Contoh:
    # st.markdown("""<style>body { background-color: #f0f2f6; }</style>""", unsafe_allow_html=True)

from langchain_google_genai import ChatGoogleGenerativeAI  # For interacting with Google Gemini via LangChain
from langgraph.prebuilt import create_react_agent  # For creating a ReAct agent
from langchain_core.messages import HumanMessage, AIMessage  # For message formatting

# --- 1. Page Configuration and Title ---

# Set the title and a caption for the web page
st.title("Teman Ngobrol 🗿")
st.caption("Obrolan sederhana dan bersahabat menggunakan LangGraph dengan model Google Gemini")

# --- 2. Sidebar for Settings ---

# Create a sidebar section for app settings using 'with st.sidebar:'
hide_sidebar = True # Set True untuk menyembunyikan, False untuk menampilkan
with st.sidebar:
    # Add a subheader to organize the settings
    st.subheader("Selamat datang!")
    st.caption("Saat santai dan minum kopi di senja hari adalah saat yang tepat mengobrol dengan sahabat AI Anda")
    
    # Create a text input field for the Google AI API Key.
    # 'type="password"' hides the key as the user types it.
    # google_api_key = st.text_input("Google AI API Key", type="password")
    google_api_key = "AIzaSyDczMQaJFM-mILbtzmkNM1ZVJH1_uLWJXk"
    
    # Create a button to reset the conversation.
    # 'help' provides a tooltip that appears when hovering over the button.
    # reset_button = st.button("Reset Conversation", help="Clear all messages and start fresh")

# --- 3. API Key and Agent Initialization ---

# Check if the user has provided an API key.
# If not, display an informational message and stop the app from running further.
# if not google_api_key:
#    st.info("Please add your Google AI API key in the sidebar to start chatting.", icon="🗝️")
#    st.stop()

# This block of code handles the creation of the LangGraph agent.
# It's designed to be efficient: it only creates a new agent if one doesn't exist
# or if the user has changed the API key in the sidebar.

# We use `st.session_state` which is Streamlit's way of "remembering" variables
# between user interactions (like sending a message or clicking a button).
if ("agent" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
    try:
        # Initialize the LLM with the API key
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.7
        )
        
        # Create a simple ReAct agent with the LLM
        st.session_state.agent = create_react_agent(
            model=llm,
            tools=[],  # No tools for this simple example
            prompt="You are a helpful, friendly assistant. Respond concisely and clearly."
        )
        
        # Store the new key in session state to compare against later.
        st.session_state._last_key = google_api_key
        # Since the key changed, we must clear the old message history.
        st.session_state.pop("messages", None)
    except Exception as e:
        # If the key is invalid, show an error and stop.
        st.error(f"Invalid API Key or configuration error: {e}")
        st.stop()

# --- 4. Chat History Management ---

# Initialize the message history (as a list) if it doesn't exist.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Handle the reset button click.
# if reset_button:
    # If the reset button is clicked, clear the agent and message history from memory.
#    st.session_state.pop("agent", None)
#    st.session_state.pop("messages", None)
    # st.rerun() tells Streamlit to refresh the page from the top.
#    st.rerun()

# --- 5. Display Past Messages ---

# Loop through every message currently stored in the session state.
for msg in st.session_state.messages:
    # For each message, create a chat message bubble with the appropriate role ("user" or "assistant").
    with st.chat_message(msg["role"]):
        # Display the content of the message using Markdown for nice formatting.
        st.markdown(msg["content"])

# --- 6. Handle User Input and Agent Communication ---

# Create a chat input box at the bottom of the page.
# The user's typed message will be stored in the 'prompt' variable.
prompt = st.chat_input("Buka Obrolan...")

# Check if the user has entered a message.
if prompt:
    # 1. Add the user's message to our message history list.
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 2. Display the user's message on the screen immediately for a responsive feel.
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Get the assistant's response.
    # Use a 'try...except' block to gracefully handle potential errors (e.g., network issues, API errors).
    try:
        # Convert the message history to the format expected by the agent
        messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Send the user's prompt to the agent
        response = st.session_state.agent.invoke({"messages": messages})
        
        # Extract the answer from the response
        if "messages" in response and len(response["messages"]) > 0:
            answer = response["messages"][-1].content
        else:
            answer = "Lagi Ngantuk."

    except Exception as e:
        # If any error occurs, create an error message to display to the user.
        answer = f"An error occurred: {e}"

    # 4. Display the assistant's response.
    with st.chat_message("assistant"):
        st.markdown(answer)
    # 5. Add the assistant's response to the message history list.
    st.session_state.messages.append({"role": "assistant", "content": answer})
