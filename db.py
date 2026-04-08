import chromadb
from config import CHROMA_PATH

client = chromadb.PersistentClient(path=CHROMA_PATH)

user_coll = client.get_or_create_collection("users")
session_coll = client.get_or_create_collection("chat_sessions")
message_coll = client.get_or_create_collection("chat_messages")