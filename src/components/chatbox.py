import streamlit as st
import time

from src. services.llms_chat import get_response
from src.components.stats.stats import show_stats

thread = []  

def message(content, is_user=False, key=None):
    if is_user:
        st.write(
            f'<div style="text-align:right; padding: 5px 10px;">😎 <b>You</b>: {content}</div>',
            unsafe_allow_html=True
        )
    else:
        st.write(
            '<div style="text-align:left; padding: 5px 10px;">🧉 <b>ChatMate</b>:</div>',
            unsafe_allow_html=True
        )
        st.markdown(            content        )
 
def render_message(msg_list):
    if len(msg_list) == 0:
        return
    
    msg = msg_list[0]
    message(msg["content"].replace('$', '&#36;'), is_user=msg["role"] == "user", key=str(time.time()))

# Render chat box
def chatbox(modelfamily, model, instructions, temperature, use_cache, similarity_threshold):
    # If new user message submitted, send it to the assistant
    if query := st.chat_input() or st.session_state["saved_query"]:
        prompt_msg = {"role": "user", "content": query}
        render_message([prompt_msg])
        thread.append(prompt_msg)
        
        with st.spinner("Thinking..."):
            start_time = time.time()
            response = get_response(query, modelfamily, model, instructions, temperature, use_cache, similarity_threshold)
            elapsed_time = time.time() - start_time
            
        if "error" in response:
            st.error(response["error"])
            return
        else:           
            thread.append({"role": "assistant", "content": response["content"], "elapsed_time": elapsed_time})
            
            response_msg = {"role": "assistant", "content": response["content"]}
            render_message([response_msg])

            show_stats(response, elapsed_time, model, query)
        