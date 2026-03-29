import os
import json
import boto3
import streamlit as st
from langchain.chains import LLMChain
from langchain.chains import ConversationChain
from langchain_community.chat_models import BedrockChat
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# AWS setup and credential check (unchanged)

# ...

# Initialize Bedrock client
try:

    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"

    )

    st.success("Bedrock client initialized successfully")

except Exception as e:

    st.error(f"Error initializing Bedrock client: {str(e)}")

# Define model options

MODEL_OPTIONS = {

    "Claude 3 Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "Claude 2": "anthropic.claude-v2:1",
    "Claude 1": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "Claude 3 Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
    "Claude 3.5 Sonnet v2": "manthropic.claude-3-5-sonnet-20241022-v2:0",
    "Claude 3 Opus": "anthropic.claude-3-opus-20240229-v1:0",
    "Claude Instant":"anthropic.claude-instant-v1"

}

def create_llm(model_id):

    try:

        llm = BedrockChat(

            model_id=model_id,
            client=bedrock_client,
            model_kwargs={

                "max_tokens": 1000,
                "temperature": 1,
                "top_k": 250,
                "top_p": 1,

            }

        )

        st.success(f"LLM created successfully with model: {model_id}")

        return llm
    except Exception as e:
        st.error(f"Error creating LLM with model {model_id}: {str(e)}")

        return None

# Initialize conversation memory
memory = ConversationBufferMemory()

# Create the conversation chain
def create_conversation_chain(llm):

    if llm:

        conversation = ConversationChain(
            llm=llm,
            memory=memory,
            verbose=True

        )

        st.success("Conversation chain created successfully")

        return conversation

    else:

        st.error("Failed to create conversation chain due to LLM initialization error")

        return None

def my_chatbot(model, language, freeform_text):

    st.write(f"Debug - Model: {model}, Language: {language}, Input: {freeform_text}")

    prompt = PromptTemplate(
        input_variables=["language", "freeform_text"],
        template="You are a chatbot. You are in {language}.\n\n{freeform_text}"

    )

    bedrock_chain = LLMChain(llm=model, prompt=prompt)


    try:
        response = bedrock_chain({'language': language, 'freeform_text': freeform_text})
        st.success("Chatbot response generated successfully")
        return response

    except Exception as e:

        st.error(f"Error in chatbot response generation: {str(e)}")

        return None

st.title("Bode's Bedrock Chatbot App")

# Model selection
selected_model_name = st.sidebar.selectbox("Select Model", list(MODEL_OPTIONS.keys()))
selected_model_id = MODEL_OPTIONS[selected_model_name]

# Create LLM and conversation chain

llm = create_llm(selected_model_id)
conversation = create_conversation_chain(llm)
language = st.sidebar.selectbox("Language", ["english", "spanish"])

st.write(f"Selected model: {selected_model_name}")
st.write(f"Selected language: {language}")

if language:

    freeform_text = st.sidebar.text_area(label="What is your question?", max_chars=1000)
    st.write(f"User input: {freeform_text}")

if freeform_text and conversation:

    response = my_chatbot(llm, language, freeform_text)
    if response:

        st.write("Chatbot response:")
        st.write(response['text'])

    else:

        st.error("Failed to get a response from the chatbot")