import boto3
import json
import streamlit as st

# Initialize Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def call_bedrock(prompt, model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0"):


    """Call Bedrock AI model with user prompt"""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    })
    
    response = bedrock.invoke_model(
        body=body,
        modelId=model_id,
        contentType="application/json"
    )
    
    result = json.loads(response['body'].read())
    return result['content'][0]['text']

# Streamlit UI
st.title("🤖 Bode Bedrock AI Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            response = call_bedrock(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error: {str(e)}")