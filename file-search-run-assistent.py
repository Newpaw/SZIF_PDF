import os
from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
from typing_extensions import override

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
assistent_id = os.getenv("ASSISTANT_ID")
vectore_storage_id = os.getenv("VS_STORAGE")

client = OpenAI(api_key=openai_api_key)

if not vectore_storage_id:
    vector_store = client.beta.vector_stores.create(name="SZIF_test_docs", expires_after=3600)
    print(f"Vector Store ID - {vector_store.id}")

    file_paths = [f"docs/{file}" for file in os.listdir("docs") if file.endswith(".pdf")]
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
    )
    vectore_storage_id = vector_store.id
    print(f"File ctatus {file_batch.status}")
    print(f"File counts {file_batch.file_counts}")


assistant = client.beta.assistants.update(
  assistant_id=assistent_id,
  tool_resources={"file_search": {"vector_store_ids" : [vectore_storage_id]}})

print(f"Assistant ({assistant.id}) updated with vecto restore {vectore_storage_id}.")

print(f"Assistand_id {assistent_id} or assistand.id {assistant.id}")
thread = client.beta.threads.create()

print(f"Thread ID - {thread.id} \n\n")



#class EventHandler(AssistantEventHandler):
#    @override
#    def on_text_created(self, text) -> None:
#        print(f"\nassistant > ", end="", flush=True)
#
#    @override
#    def on_tool_call_created(self, tool_call):
#        print(f"\nassistant > {tool_call.type}\n", flush=True)
#
#    @override
#    def on_message_done(self, message) -> None:
#        # print a citation to the file searched
#        message_content = message.content[0].text
#        annotations = message_content.annotations
#        citations = []
#        for index, annotation in enumerate(annotations):
#            message_content.value = message_content.value.replace(
#                annotation.text, f"[{index}]"
#            )
#            if file_citation := getattr(annotation, "file_citation", None):
#                cited_file = client.files.retrieve(file_citation.file_id)
#                citations.append(f"[{index}] {cited_file.filename}")
#
#        print(message_content.value)
#        print("\n".join(citations))
#
#
#with client.beta.threads.runs.stream(
#    thread_id=thread.id,
#    assistant_id=assistant.id,
#    instructions="Jsi poradce garantů dotačních titulů, který má za úkol znát ředu různých dotačních titulů a pomáhat kolegům, kteří se ptají na otázky. Snažíš se poskytnou přesné odpovědi a to především z dat, které máš k dispozici. Když si nejsi jistý, řekneš to. Vždy jsi vtipný a snažíš se o vtipnost. Pokud je něco mimo tvé znalosti omluvíš se a přiznáš to. Zároveň se namísto toho pokusíš udělat vtípek.",
#    event_handler=EventHandler(),
#) as stream:
#    stream.until_done()
#



while True:
    text = input("\nO jaké dotace máš zájem a jakou máš na mě otázku?\n\n")
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
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    print(message_content.value)
    print("\n".join(citations))