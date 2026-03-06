import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# --- 설정 (개인 @gmail.com 계정의 키를 넣어주세요) ---
GEMINI_API_KEY = "AIzaSyDWKKpQRBzaj9Dz43OPV-83lQRZQr2ro10"
PDF_FILE_NAME = "school_rules.pdf" 

st.set_page_config(page_title="학교 행정 AI 도우미", layout="centered")
st.title("🏫 학교생활 무엇이든 물어보세요!")

# 1. API 설정 및 가용 모델 자동 탐색
genai.configure(api_key=GEMINI_API_KEY)

@st.cache_resource
def find_working_model():
    try:
        # 내 계정에서 사용 가능한 모델 목록 확인
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 1.5-flash가 있으면 최우선, 없으면 첫 번째 모델 선택
        for target in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if target in models:
                return target
        return models[0] if models else "models/gemini-pro"
    except Exception as e:
        return "models/gemini-pro"

target_model_name = find_working_model()

# 2. PDF 로드 및 텍스트 추출
@st.cache_resource
def load_pdf_text(file_path):
    if not os.path.exists(file_path):
        return None
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            content = page.extract_text()
            if content: text += content
        return text if text.strip() else None
    except:
        return None

context_text = load_pdf_text(PDF_FILE_NAME)

# 3. 채팅 인터페이스
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 학교 규정에 대해 궁금한 점을 말씀해 주세요."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not context_text:
            st.error("PDF 파일(school_rules.pdf)을 찾을 수 없거나 내용이 비어있습니다.")
        else:
            try:
                # 자동 선택된 모델로 답변 생성
                model = genai.GenerativeModel(target_model_name)
                response = model.generate_content(
                    f"너는 학교 행정 전문가야. 아래 정보를 바탕으로만 답변해줘.\n\n[정보]\n{context_text}\n\n질문: {prompt}"
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"AI 응답 실패 (사용 모델: {target_model_name}): {e}")
