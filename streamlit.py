import os

import google.generativeai as genai
import pandas as pd

import streamlit as st

# Set up Google AI API key
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Set up the generative model
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
# safety_settings = [
#     {
#         "category": "HARM_CATEGORY_HARASSMENT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#     },
#     {
#         "category": "HARM_CATEGORY_HATE_SPEECH",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#     },
#     {
#         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#     },
#     {
#         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#     },
# ]
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    # model_name="gemini-1.5-pro",
    safety_settings=safety_settings,
    generation_config=generation_config,
    #     system_instruction="""I can answer your questions about anything, drawing only on the information provided to me. I will never access the internet for answers.
    # After answering your questions, I will display contact information so customers can reach you. Please provide the following details:
    # สอบถามรายละเอียดเพิ่มเติมได้ที่ :
    # Facebook: SCGHomeOfficial > https://www.facebook.com/SCGHomeOfficial
    # Line: @scghome > https://line.me/R/ti/p/@scghome
    # """,
    system_instruction="""คุณสามารถตอบคำถามได้ทุกเรื่อง และคุณจะอ้างอิงคำตอบจากเอกสารที่มีในระบบ 
    หากมีคำถามที่เข้ามาหาคำตอบไม่ได้ แต่มีบริการอื่นที่ใกล้เคียง คุณสามารถแนะนำและเอามาเป็นคำตอบได้
    คุณจะไม่เอาคำตอบจากภายนอกหรืออินเทอร์เน็ตมาตอบเด็ดขาด
    และในกรณีที่แสดงผลเกี่ยวกับการติดต่อ SCG คุณจะแสดงผลออกมาในรูปแบบดังต่อไปนี้
    สอบถามรายละเอียดเพิ่มเติมได้ที่ :
    Facebook: SCGHomeOfficial > https://www.facebook.com/SCGHomeOfficial
    Line: @scghome > https://line.me/R/ti/p/@scghome
    แต่ถ้าเป็นคำถามที่เกี่ยวข้อกับ จระเข้ คุณจะแสดงผลออกมาในรูปแบบดังต่อไปนี้
    สอบถามรายละเอียดเพิ่มเติมได้ที่ :
    Facebook: จระเข้ – JORAKAY > https://www.facebook.com/JorakayPage
    Line: @scghome > https://lin.ee/WdPMtDe
    """,
)


# Function to clear chat history
def clear_history():
    st.session_state["messages"] = [
        {"role": "model", "content": "หนูเป็น Chatbot ตอบคำถามได้ทุกเรื่อง"}
    ]
    st.experimental_rerun()  # Rerun the script to refresh the page


# Sidebar with Clear History button
with st.sidebar:
    if st.button("Clear History"):
        clear_history()

st.title("💬 Chatbot for SCG Home")

# Initialize messages if not present in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "model",
            "content": "หนูเป็น Chatbot ของ SCG Home ตอบคำถามได้ทุกเรื่องเกี่ยวกับความรู้ที่มีค่ะ",
        }
    ]

# Path to the Excel file
file_path = "data/context_scg_home.xlsx"

# Read the Excel file
try:
    df = pd.read_excel(file_path)
    file_content = df.to_string(index=False)
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

# Display chat messages
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Input for new chat messages
if prompt := st.chat_input():
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    def generate_response():
        # Convert messages to the required format
        history = [
            {"role": msg["role"], "parts": [{"text": msg["content"]}]}
            for msg in st.session_state["messages"]
        ]

        # Add the file content to the history
        history.insert(1, {"role": "user", "parts": [{"text": file_content}]})

        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(prompt)
        st.session_state["messages"].append({"role": "model", "content": response.text})
        st.chat_message("model").write(response.text)

    generate_response()
