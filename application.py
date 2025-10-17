import streamlit as st
from characters import system_role, instruction
from chatbot import Chatbot
from common import model
from function_calling import FunctionCalling, tools
from pathlib import Path


ASSETS = Path(__file__).parent / "assets"
BANNER = str(ASSETS / "banner2.png")
AVATAR = str(ASSETS / "persona.png")

# 기본 페이지 설정
st.set_page_config(
    page_title="Chatbot_project",
    layout="centered",
)
st.image(BANNER, use_container_width=True)   # 배너설정
st.title("나만의 경제 전문가 고비와 대화하기")

# 세션 초기화 (대화 기록, 챗봇, 함수 호출기)
if "history" not in st.session_state:
    st.session_state.history = [] #여기에 모든 대화 기록 저장해서 출력
if "chatbot" not in st.session_state: #챗봇 인스턴스 생성
    st.session_state.chatbot = Chatbot(
        model=model.basic,
        system_role=system_role,
        instruction=instruction,
        user="사용자",
        assistant="고비"
    )
if "fcaller" not in st.session_state: #함수 호출기 인스턴스 생성
    st.session_state.fcaller = FunctionCalling(model=model.basic)

# 이전 대화 출력
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
user_text = st.chat_input("고비에게 질문해보세요!")

if user_text:   #사용자 입력 들어오면 프로그램 동작 시작
    # 1. 사용자 메시지 history에 저장하고 그대로 출력
    st.session_state.history.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)


    #2. 챗봇 불러와서 답변 생성
    chatbot = st.session_state.chatbot
    fcaller = st.session_state.fcaller
    chatbot.add_user_message(user_text)

    try:
        # 함수 호출 분석 시도
        prev_resp, _ = fcaller.analyze(user_text, tools)

        # GPT가 실제로 함수를 요청했는지 확인
        has_tool_call = any(
            hasattr(item, "type") and item.type == "function_call"
            for item in prev_resp.output
        )

        if has_tool_call:
            # 함수 실행 및 결과 전달
            final_resp = fcaller.run(
                previous_response=prev_resp,
                context=chatbot.context
            )
            answer = getattr(final_resp, "output_text", "[응답 없음]")
        else:
            # 도구 호출이 없으면 일반 대화로
            response = chatbot.send_request()
            chatbot.add_response(response)
            chatbot.clean_context()
            answer = chatbot.get_last_response()

    except Exception as e:
        response = chatbot.send_request()
        chatbot.add_response(response)
        chatbot.clean_context()
        answer = chatbot.get_last_response() + f"\n(참고: {e})"

    # 결과 출력
    st.session_state.history.append({"role": "developer", "content": answer})
    with st.chat_message("assistant", avatar=AVATAR):
        st.markdown(answer)



