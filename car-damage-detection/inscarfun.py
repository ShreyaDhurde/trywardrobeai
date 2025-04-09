'''make a python code which can validate where the given images while be accepted for you a
 expert in insuarance company to approve the accident insuarance claim 
'''

def ask_anyting(query):
   model = ChatOpenAI(temperature=0.7)
    # Construct the prompt
    prompt = (
    f'''
   
    You are an insurance advisor with expertise in life and car insurance. Provide accurate, helpful information on policies, coverage, claims, and benefits.
    {query}
    '''
)
 
   
    # Create a message with the prompt
    message = HumanMessage(content=prompt)
   
    # Invoke the model with the message
    try:
        response = model([message])
        return response.content
    except Exception as e:
        return f"Error generating response: {e}"