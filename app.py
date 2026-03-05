import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# --- 설정 (개인용 @gmail.com 계정에서 만든 키를 넣으세요) ---
GEMINI_API_KEY = "여기에_새로_발급받은_키를_넣으세요"
PDF_FILE_NAME = "school_rules.pdf" 

# 페이지 설정
st.set_page_config(page_title="학교 행정 AI 도우미", layout="centered")
st.title("🏫 학교생활 무엇이든 물어보세요!")

# 1. API 키 인증 및 모델 준비
genai.configure(api_key="AIzaSyDWKKpQRBzaj9Dz43OPV-83lQRZQr2ro10")
model = genai.GenerativeModel('gemini-pro')

# 2. PDF 데이터 로드 함수 (오류 파악용 코드 추가)
@st.cache_resource
def load_school_data(file_path):
    if not os.path.exists(file_path):
        return f"오류: '{file_path}' 파일이 서버에 없습니다. 파일명을 확인하세요."
    try:
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            content = page.extract_text()
            if content: text += content
        
        if not text.strip():
            return "오류: PDF에서 텍스트를 추출할 수 없습니다. 스캔 이미지가 아닌지 확인하세요."
        return text
    except Exception as e:
        return f"PDF 읽기 중 기술적 오류 발생: {e}"

context_data = load_school_data(PDF_FILE_NAME)

# 3. 채팅 UI 구성
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 학교 규정이나 일정에 대해 물어봐 주세요."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # PDF 데이터에 오류 문구가 있는지 확인
        if isinstance(context_data, str) and context_data.startswith("오류"):
            st.error(context_data)
        else:
            try:
                # AI에게 구체적인 답변 지침 하달
                response = model.generate_content(
                    f"너는 학교 도우미야. 아래 내용을 참고해서 친절히 답해줘.\n\n[내용]\n{context_data}\n\n질문: {prompt}"
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"AI 응답 실패: {e}")
                st.info("개인 @gmail.com 계정으로 생성한 API 키가 맞는지 다시 확인해 주세요.")
