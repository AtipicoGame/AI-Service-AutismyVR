import streamlit as st
from ui.chat_session_manager import ChatSessionManager

# Streamlit UI entrypoint
st.title("AutismyVR Chat")
st.write("Hello 👋")

# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input and process response
if user_prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Initialize the chat session manager
    chat_manager = ChatSessionManager()

    # Display assistant's response in chat message container
    with st.chat_message("assistant"):
        response_stream = st.empty()  # Placeholder for streamed content
        full_response = ""

        try:
            # Process and stream response in chunks
            for chunk in chat_manager.response_generator(user_prompt):
                full_response += chunk
                response_stream.markdown(full_response)  # Update the placeholder with streamed content

            # Add assistant's full response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            # Display the error message
            error_message = f"Probably OLLAMA service not running. The error exception message: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            st.error(error_message)

else:
    if len(st.session_state.messages) > 0:
        st.session_state.messages.append({"role": "assistant", "content": st.write('Enter a valid prompt!')})
