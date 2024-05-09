import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
assistent_id = os.getenv("ASSISTANT_ID")

client = OpenAI(api_key=openai_api_key)

vector_store = client.beta.vector_stores.create(name="SZIF_test_docs")
print(f"Vector Store ID - {vector_store.id}")

#file_paths = [f"docs/{file}" for file in os.listdir("docs") if file.endswith(".pdf")]
#file_streams = [open(path, "rb") for path in file_paths]
#
#file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#  vector_store_id=vector_store.id, files=file_streams
#)
#
#print(f"File Status {file_batch.status}")


assistant = client.beta.assistants.update(
  assistant_id=assistent_id,
  tool_resources={"file_search": {"vector_store_ids" : [vector_store.id]}})

print(f"Assistant ({assistent_id}) Updated with vecto restore")

thread = client.beta.threads.create()

print(f"Thread ID - {thread.id} \n\n")

while True:
    text = input("O jaké dotace máš zýjem a jakou máš na mě otázku?\n\n")
    if text == "exit":
        break

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
    message_content = messages[0].content[0].text
    print("Response:\n")

    print(f"{message_content.value}\n")