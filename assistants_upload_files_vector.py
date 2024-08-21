import os
import time
import glob
from openai import OpenAI
from datetime_utils import *
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-3.5-turbo-1106"
TODAY = date.today()
START_OF_WEEK, END_OF_WEEK = get_school_week_bounds(date.today())

key = os.environ.get("OPENAI_API_KEY")
assistant_id = os.environ.get("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=key)
print(f"VARIABLES LOADED: \n assistant_id: {assistant_id}\nkey: {key}")

try:
    assistant = client.beta.assistants.retrieve(assistant_id)
    print("Assistant Found:")
    print(assistant)
except Exception as e:
    print(e)
    # create the assistant if not exists
    assistant = client.beta.assistants.create(
        name = "KinderLogger",
        instructions=f"""
        You are an intelligent assistant equipped with a wealth of information contained in various internal files. When addressing user questions, it's essential to rely on this information to formulate your responses. However, it's crucial to present these answers as though they are derived from your own knowledge base, without referencing or hinting at the existence of these files. The user should perceive the assistance you provide as coming directly from your own expertise, without any visible reliance on external sources or annotations. Your role is to seamlessly offer informed responses, creating an impression of innate understanding and proficiency.

        ***IMPORTANT***

        Please review the contents of the uploaded file(s) before answering.
        
        If you don't know an answer, you must respond 'I don't know.'. No other responses will be accepted.
        """,
        # tools=[{"type":"retrieval"},{"type":"code_interpreter"}],
        tools=[{"type":"file_search"},{"type":"code_interpreter"}],
        model=MODEL
    )
    print("New Assistant Created")
    print(assistant)


'''
FOUND RESPONSE:
Assistant(id='asst_rBsu7u3vfM5q4CAyCr2eWEde', created_at=1724180957, description=None, instructions='You are an intelligent assistant.', metadata={}, model='gpt-3.5-turbo-1106', name='KinderLogger', object='assistant', tools=[CodeInterpreterTool(type='code_interpreter'), FileSearchTool(type='file_search', file_search=None)], response_format='auto', temperature=1.0, tool_resources=ToolResources(code_interpreter=ToolResourcesCodeInterpreter(file_ids=[]), file_search=ToolResourcesFileSearch(vector_store_ids=['vs_IXvB0zlvy4ou4f29UZTJ09Q8'])), top_p=1.0)

NOT FOUND RESPONSE
Error code: 404 - {'error': {'message': "No assistant found with id 'abcd'.", 'type': 'invalid_request_error', 'param': None, 'code': None}}

CREATED RESPONSE
ssistant(id='asst_ULDjcK2ZAd7XzzdiwC1qtvz1', created_at=1724252499, description=None, instructions="\n        You are an intelligent assistant equipped with a wealth of information contained in various internal files. When addressing user questions, it's essential to rely on this information to formulate your responses. However, it's crucial to present these answers as though they are derived from your own knowledge base, without referencing or hinting at the existence of these files. The user should perceive the assistance you provide as coming directly from your own expertise, without any visible reliance on external sources or annotations. Your role is to seamlessly offer informed responses, creating an impression of innate understanding and proficiency.\n\n        ***IMPORTANT***\n\n        Please review the contents of the uploaded file(s) before answering.\n        \n        If you don't know an answer, you must respond 'I don't know.'. No other responses will be accepted.\n        ", metadata={}, model='gpt-3.5-turbo-1106', name='KinderLogger', object='assistant', tools=[FileSearchTool(type='file_search', file_search=None), CodeInterpreterTool(type='code_interpreter')], response_format='auto', temperature=1.0, tool_resources=ToolResources(code_interpreter=ToolResourcesCodeInterpreter(file_ids=[]), file_search=ToolResourcesFileSearch(vector_store_ids=[])), top_p=1.0)
'''

print("assistant.id: ")
print(assistant.id)

# UPLOAD FILES


pattern = "*.json"
json_files = glob.glob(pattern)
uploaded_files = []
print(" # json_files: ")
print(json_files)

###############################################
# upload files and add them to a Vector Store #
###############################################
# Create a named vector store
vector_store = client.beta.vector_stores.create(name="Kinder Assistant 1")
print(" # vector_store: ")
print(vector_store)

# Ready the files for upload to OpenAI
# file_paths = ["edgar/goog-10k.pdf", "edgar/brka-10k.txt"]
file_streams = [open(file_path, "rb") for file_path in json_files]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

print(file_batch.status)
print(file_batch.file_counts)

# Update the assistant to use the new Vector Store
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

print(assistant)

# Original code

'''

for file_path in json_files:
    print(f'Processing file: {file_path}')

    transcript_file = client.files.create(
        file=open(file_path, "rb"),
        purpose="assistants"
    )


    print("Uploaded_file:")
    print(transcript_file.id)
    uploaded_files.append(transcript_file.id)

print(uploaded_files)

# Step 8. Modify the Assistant
assistant_update = client.beta.assistants.update(
    assistant_id=assistant.id,
    tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
    # file_ids=uploaded_files
)

print("assistant_update")
print(assistant_update)

#     client.beta.assistants.files.create(
#         assistant_id=assistant.id,
#         file_id=transcript_file.id
#     )

# thread = client.beta.threads.create()

# def display_main_menu():
#     print("\n[KinderLogger Assistant]")
#     prompt=input("\nEnter your prompt: ")
#     handle_main_menu_option(prompt)

# def handle_main_menu_option(prompt):
#     client.beta.threads.messages.create(
#         thread.id,
#         role="user",
#         content=prompt
#     )
#     client.beta.threads.messages.create(
#         thread.id,
#         role="user",
#         content=f"""
#         -----------------
#         Today is {TODAY}.
#         -----------------
#         The current school week goes from {START_OF_WEEK} and {END_OF_WEEK}.
#         -----------------
#         SEARCH IN ALL THE DOCUMENTS.
#         """
#     )
#     run = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant.id
#     )
#     still_running = True
#     while still_running:
#         latest_run = client.beta.threads.runs.retrieve(
#             thread_id=thread.id, run_id=run.id)
#         still_running = latest_run.status != "completed"
#         if (still_running):
#             time.sleep(2)

#     messages = client.beta.threads.messages.list(thread_id=thread.id)
#     print(messages.data[0].content)

# while True:
#     display_main_menu()

########################
# const response = await fetch(`https://api.openai.com/v1/assistants/${assistant_id}`,
# {
#     method: 'POST',
#     headers: {
#         'Content-Type':  'application/json',
#         'OpenAI-Beta':   'assistants=v1',
#         'Authorization': `Bearer ${apiKey}`
#         },
#     body: JSON.stringify({
#         instructions: instructions , 
#         name: assistant_name , 
#         model: "gpt-4-turbo-preview", 
#         tools: [{ "type": "retrieval" }] , 			 
#         file_ids: [file_id] 
#     })

########################

'''