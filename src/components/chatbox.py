import streamlit as st
import time

from st_chat_message import message

from src. services.llms_chat import get_response
from src.components.stats import show_stats

# Hack to right-align user messages

thread = [{"role": "assistant", "content": "How can I help you?"}]  
 
def render_message(msg):
    message(msg["content"], is_user=msg["role"] == "user", key=str(time.time()))

# Render chat box
def chatbox(modelfamily, model, instructions, scoped_answer, use_markdown, temperature):
    render_message(thread[0])
    # If new user message submitted, send it to the assistant
    if prompt := st.chat_input() or st.session_state["saved_query"]:
        prompt_msg = {"role": "user", "content": prompt}
        render_message(prompt_msg)
        thread.append(prompt_msg)
        
        with st.spinner("Thinking..."):
            start_time = time.time()
            response = get_response(prompt, modelfamily, model, instructions, scoped_answer, use_markdown, temperature)
            elapsed_time = time.time() - start_time
            
        thread.append({"role": "assistant", "content": response["content"], "elapsed_time": elapsed_time})
        
        response_msg = {"role": "assistant", "content": response["content"]}
        render_message(response_msg)

        show_stats(response, elapsed_time, model)
        