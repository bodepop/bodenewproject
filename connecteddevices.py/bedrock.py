import boto3
import streamlit as st
from langchain.chains import LLMChain
from langchain.chains import ConversationChain
from langchain_community.chat_models import BedrockChat
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

 

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

 

# Initialize AWS Bedrock client

def init_bedrock_client():

    try:

        bedrock_client = boto3.client(

            service_name='bedrock-runtime',

            region_name='us-east-1'

        )

        return bedrock_client

    except Exception as e:

        st.error(f"Error initializing Bedrock client: {str(e)}")

        return None

 

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'temperature' not in st.session_state:
    st.session_state.temperature = 1.0
if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = 1000
if 'top_k' not in st.session_state:
    st.session_state.top_k = 250
if 'top_p' not in st.session_state:
    st.session_state.top_p = 1.0

 

# Initialize Bedrock client
bedrock_client = init_bedrock_client()


# Create LLM function
def create_llm(model_id, temp, max_tok, topk, topp):
    try:
        llm = BedrockChat(
            model_id=model_id,
            client=bedrock_client,
            model_kwargs={

                "max_tokens": max_tok,
                "temperature": temp,
                "top_k": topk,
                "top_p": topp,

            }

        )

        return llm
    except Exception as e:
        st.error(f"Error creating LLM: {str(e)}")
        return None

 

# Chatbot function

def my_chatbot(llm, language, user_input):

    try:

        # Create conversation memory
        memory = ConversationBufferMemory() 

        # Create prompt template based on language
        if language == "spanish":
            prompt = PromptTemplate(
                input_variables=["input"],
                template="Por favor responde en español: {input}"

            )

        else:

            prompt = PromptTemplate(
                input_variables=["input"],
                template="Please respond to: {input}"

            )

       

        # Create conversation chain

        conversation = LLMChain(
            llm=llm,
            prompt=prompt,
            memory=memory,
            verbose=True

        )

       

        # Get response

        response = conversation.run(user_input)

        return {
            'text': response,
            'status': 'success'

        }

    except Exception as e:
        return {

            'text': f"Error: {str(e)}",
            'status': 'error'

        }

 

# Main app title
st.title("Bode's Interactive Bedrock Chatbot")


# Sidebar configuration
with st.sidebar:
    st.header("Model Settings")


    # Model selection
    selected_model_name = st.selectbox("Select Model", list(MODEL_OPTIONS.keys()))
    selected_model_id = MODEL_OPTIONS[selected_model_name]

   

    # Basic settings
    st.subheader("Basic Settings")
    temperature = st.slider(

        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Higher values make output more creative, lower values more focused"

    )


    # Advanced settings
    with st.expander("Advanced Settings"):
        max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=st.session_state.max_tokens,
            step=100,
            help="Maximum number of tokens in the response"

        )

       

        top_k = st.slider(

            "Top K",
            min_value=0,
            max_value=500,
            value=st.session_state.top_k,
            step=10,
            help="Number of tokens to consider for sampling"

        )

       

        top_p = st.slider(

            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.top_p,
            step=0.1,
            help="Cumulative probability threshold for sampling"

        )

   

    # Language selection
    language = st.selectbox("Language", ["english", "spanish"])


    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.experimental_rerun()

 

# Update session state
st.session_state.temperature = temperature
st.session_state.max_tokens = max_tokens
st.session_state.top_k = top_k
st.session_state.top_p = top_p

 

# Chat interface
chat_container = st.container()
with chat_container:

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

 

    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:

        # Show user message
        with st.chat_message("user"):
            st.write(user_input)

       

        # Create LLM and get response
        llm = create_llm(
            selected_model_id,
            st.session_state.temperature,
            st.session_state.max_tokens,
            st.session_state.top_k,
            st.session_state.top_p

        )

       

        if llm:
            try:
                response = my_chatbot(llm, language, user_input)

                if response['status'] == 'success':

                    # Show assistant response
                    with st.chat_message("assistant"):
                        st.write(response['text'])


                    # Add to chat history
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": response['text']})

                else:
                    st.error(response['text'])

                   

            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

 

# Chat statistics

with st.sidebar:
    st.markdown("---")
    st.subheader("Chat Statistics")
    col1, col2 = st.columns(2)
    with col1:

        st.metric("Total Messages", len(st.session_state.chat_history))

    with col2:
        st.metric("User Messages", len([m for m in st.session_state.chat_history if m["role"] == "user"]))