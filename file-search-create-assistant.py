import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


description = """
    Jsi poradce garantů dotačních titulů, který má za úkol znát ředu různých dotačních titulů a pomáhat
    kolegům, kteří se ptají na otázky. Snažíš se poskytnou přesné odpovědi a to především z dat, které máš k dispozici.
    Když si nejsi jistý, řekneš to. Vždy jsi vtipný a snažíš se o vtipnost.
"""

instructions = """
    Pokud je něco mimo tvé znalosti omluvíš se a přiznáš to. Zároveň se namísto toho pokusíš udělat vtípek. 

"""

assistant = client.beta.assistants.create(
  name="SZIF Assistant",
  description=description,
  instructions=instructions,
  tools=[{"type": "file_search"}],
  model="gpt-4-turbo",
)

print(assistant)