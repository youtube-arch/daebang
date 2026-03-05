import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# --- 설정 (이 부분을 수정하세요) ---
GEMINI_API_KEY = "AIzaSyDWKKpQRBzaj9Dz43OPV-83lQRZQr2ro10"
PDF_FILE_NAME = "school_rules.pdf"  # 학교 규정집/학사일정 파일명
# ------------------------------

# API 키 인증
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="학교 행정 AI 도우미", layout="centered")
st.title("🏫 학교생활 무엇이든 물어보세요!")

# PDF 파일에서 텍스트 추출 (캐싱 처리)
@st.cache_resource
def load_school_data(file_path):
    if not os.path.exists(file_path):
        return None
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text()
    return text

context_text = load_school_data(PDF_FILE_NAME)

if context_text:
    # 채팅 기록 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 학교 규정 및 학사일정에 대해 안내해 드리는 AI입니다. 무엇이 궁금하신가요?"}
        ]

    # 채팅 메시지 출력
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("예: 체험학습 신청은 며칠 전까지 해야 하나요?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI에게 지시 (RAG)
        system_instruction = f"""
        너는 학교 규정 안내 전문가야. 아래 제공된 학교 데이터를 바탕으로만 답변해줘.
        데이터에 없는 내용은 지어내지 말고 "해당 내용은 규정집에 명시되어 있지 않으니 행정실로 문의해주세요"라고 답해줘.
        
        [학교 데이터]
        {context_text}
        """
        
        with st.chat_message("assistant"):
            try:
                response = model.generate_content([system_instruction, prompt])
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("답변 생성 중 오류가 발생했습니다. API 키를 확인해주세요.")
else:
    st.error(f"서버에 '{PDF_FILE_NAME}' 파일이 없습니다. 파일을 업로드해주세요.")
