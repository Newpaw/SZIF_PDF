import os
file_paths = [f"docs/{file}" for file in os.listdir("docs") if file.endswith(".pdf")]
print(file_paths)