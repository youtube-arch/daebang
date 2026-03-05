import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# --- 설정 (반드시 개인 @gmail.com 계정의 키를 넣으세요) ---
GEMINI_API_KEY = "AIzaSyDWKKpQRBzaj9Dz43OPV-83lQRZQr2ro10"
PDF_FILE_NAME = "school_rules.pdf" 

st.set_page_config(page_title="학교 행정 AI 도우미", layout="centered")
st.title("🏫 학교생활 무엇이든 물어보세요!")

# API 설정
genai.configure(api_key=GEMINI_API_KEY)

# 사용 가능한 모델 자동 찾기 함수
@st.cache_resource
def get_best_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # 1.5-flash가 있으면 우선 선택, 없으면 첫 번째 가능 모델 선택
                if 'gemini-1.5-flash' in m.name:
                    return m.name
        return 'models/gemini-pro' # 기본값
    except Exception:
        return 'models/gemini-pro'

target_model = get_best_model()

# PDF 로드 함수
@st.cache_resource
def load_pdf_data(file_path):
    if not os.path.exists(file_path):
        return None
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text()
        return text if text.strip() else None
    except:
        return None

context_text = load_pdf_data(PDF_FILE_NAME)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 학교 규정 및 일정에 대해 답변해 드립니다."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not context_text:
            st.error("PDF 파일을 읽을 수 없습니다. 파일명과 내용을 확인해주세요.")
        else:
            try:
                # 선택된 모델로 답변 생성
                model = genai.GenerativeModel(target_model)
                response = model.generate_content(
                    f"당신은 학교 도우미입니다. 아래 정보를 바탕으로 답변하세요.\n\n[정보]\n{context_text}\n\n질문: {prompt}"
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"AI 응답 실패 (모델: {target_model}): {e}")
