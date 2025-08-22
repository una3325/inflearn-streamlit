import streamlit as st
from llm import get_ai_response, LLMConfigError

st.set_page_config(page_title="소득세 챗봇", page_icon="🤖")
st.title("🤖 소득세 챗봇")
st.caption("소득세에 관련된 모든것을 답변해드립니다!")

# ---- 사이드바: 키 입력만 받기 (인덱스는 X) ----
st.sidebar.header("API 키 입력")
openai_input = st.sidebar.text_input(
    "OPENAI_API_KEY", type="password", value=st.session_state.get("OPENAI_API_KEY", "")
)
pinecone_input = st.sidebar.text_input(
    "PINECONE_API_KEY", type="password", value=st.session_state.get("PINECONE_API_KEY", "")
)

if openai_input.strip():
    st.session_state["OPENAI_API_KEY"] = openai_input.strip()
if pinecone_input.strip():
    st.session_state["PINECONE_API_KEY"] = pinecone_input.strip()

# ---- 채팅 기록 ----
if "message_list" not in st.session_state:
    st.session_state.message_list = []

for m in st.session_state.message_list:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# ---- 채팅 입력 처리 ----
if user_question := st.chat_input("소득세에 대해 물어보세요!"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    openai_api_key = st.session_state.get("OPENAI_API_KEY")
    pinecone_api_key = st.session_state.get("PINECONE_API_KEY")

    if not openai_api_key or not pinecone_api_key:
        with st.chat_message("ai"):
            st.write("👉 먼저 왼쪽 사이드바에서 OPENAI_API_KEY와 PINECONE_API_KEY를 입력해주세요.")
        st.stop()

    try:
        with st.spinner("답변을 생성하는 중입니다"):
            stream = get_ai_response(
                user_message=user_question,
                openai_api_key=openai_api_key,
                pinecone_api_key=pinecone_api_key,
            )
            with st.chat_message("ai"):
                ai_msg = st.write_stream(stream)
                st.session_state.message_list.append({"role": "ai", "content": ai_msg})
    except LLMConfigError as e:
        with st.chat_message("ai"):
            st.write(f"❌ 설정 오류: {e}")
    except Exception:
        with st.chat_message("ai"):
            st.write("🚨 예기치 못한 오류가 발생했습니다. 입력값을 확인하고 다시 시도해 주세요.")
