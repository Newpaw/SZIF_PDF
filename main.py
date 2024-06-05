import os
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from openai import OpenAI
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")
vector_storage_id = os.getenv("VS_STORAGE")

client = OpenAI(api_key=openai_api_key)

if not vector_storage_id:
    vector_store = client.beta.vector_stores.create(
        name="SZIF_test_docs", expires_after=3600)
    print(f"Vector Store ID - {vector_store.id}")

    file_paths = [
        f"docs/{file}" for file in os.listdir("docs") if file.endswith(".pdf")]
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )
    vector_storage_id = vector_store.id
    print(f"File status {file_batch.status}")
    print(f"File counts {file_batch.file_counts}")

assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    tool_resources={"file_search": {"vector_store_ids": [vector_storage_id]}}
)

print(
    f"Assistant ({assistant.id}) updated with vector store {vector_storage_id}.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return """
    <html>
        <head>
            <title>SZIF - DEMOPAGE</title>
            <script src="https://unpkg.com/htmx.org@1.6.1"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                form { margin-bottom: 20px; }
                input[type="text"] { width: 80%; padding: 10px; margin-right: 10px; }
                button { padding: 10px 20px; }
                #response { margin-top: 20px; }
                .loader { border: 4px solid #f3f3f3; border-radius: 50%; border-top: 4px solid #3498db; width: 20px; height: 20px; animation: spin 2s linear infinite; display: none; }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                .response-content { background: #f9f9f9; padding: 20px; border-radius: 5px; }
                .citations { margin-top: 10px; font-size: 0.9em; color: #555; }
            </style>
        </head>
        <body>
            <h1>SZIF -  DEMO</h1>
            <form hx-post="/chat" hx-trigger="submit" hx-target="#response" hx-include="[name=query]">
                <input type="text" name="query" placeholder="Zadejte svůj dotaz" required>
                <button type="submit">Odeslat</button>
                <div class="loader"></div>
            </form>
            <form hx-post="/new_thread" hx-trigger="submit" hx-target="#response" style="margin-top: 20px;">
                <button type="submit">Začít novou konverzaci</button>
            </form>
            <div id="response"></div>
            <script>
                document.addEventListener('htmx:configRequest', function(evt) {
                    document.querySelector('.loader').style.display = 'inline-block';
                });
                document.addEventListener('htmx:afterRequest', function(evt) {
                    document.querySelector('.loader').style.display = 'none';
                });
            </script>
        </body>
    </html>
    """

@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, query: str = Form(...)):
    session = request.session
    current_thread_id = session.get("thread_id")

    if not current_thread_id:
        current_thread_id = client.beta.threads.create().id
        session["thread_id"] = current_thread_id

    print(current_thread_id)
    print(f"Dotaz uživatel byl {query}")
    message = client.beta.threads.messages.create(
        thread_id=current_thread_id,
        role="user",
        content=query
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=current_thread_id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(
        thread_id=current_thread_id, run_id=run.id))
    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(
            annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    response_text = f"{message_content.value}"
    formatted_response = f"<div class='response-content'><p>{response_text}</p></div>"
    if citations:
        formatted_citations = f"<div class='citations'><p>{' '.join(citations)}</p></div>"
    else:
        formatted_citations = ""

    return f"{formatted_response}{formatted_citations}"

@app.post("/new_thread", response_class=HTMLResponse)
async def new_thread(request: Request):
    current_thread_id = client.beta.threads.create().id
    request.session["thread_id"] = current_thread_id
    return "<p>Nová konverzace byla zahájena.</p>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
