import os
import time
import glob
from openai import OpenAI
from datetime_utils import *
# from dotenv import load_dotenv

# load_dotenv()

MODEL = "gpt-3.5-turbo-1106"
TODAY = date.today()
START_OF_WEEK, END_OF_WEEK = get_school_week_bounds(date.today())

key = os.environ.get("OPENAI_API_KEY")
assistant_id = os.environ.get("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=key)

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
print(" #### Creating Threads ####")

thread = client.beta.threads.create()

def display_main_menu():
    print("\n[KinderLogger Assistant]")
    prompt=input("\nEnter your prompt: ")
    handle_main_menu_option(prompt)

def handle_main_menu_option(prompt):
    client.beta.threads.messages.create(
        thread.id,
        role="user",
        content=prompt
    )
    client.beta.threads.messages.create(
        thread.id,
        role="user",
        content=f"""
        -----------------
        Today is {TODAY}.
        -----------------
        The current school week goes from {START_OF_WEEK} and {END_OF_WEEK}.
        -----------------
        SEARCH IN ALL THE DOCUMENTS.
        """
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    still_running = True
    while still_running:
        latest_run = client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id)
        still_running = latest_run.status != "completed"
        if (still_running):
            time.sleep(2)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print(messages.data[0].content)

while True:
    display_main_menu()