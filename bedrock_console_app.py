import boto3
import json

def call_bedrock(prompt, model_id="anthropic.claude-3-sonnet-20240229-v1:0"):
    """Call Bedrock AI model with user prompt"""
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
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
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    print("Bedrock AI Console Chat")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if user_input:
            print("AI: ", end="")
            response = call_bedrock(user_input)
            print(response)
            print()

if __name__ == "__main__":
    main()