import streamlit as st
from db import user_coll
 
def register():
    new_u = st.text_input("Create Username")
    new_p = st.text_input("Create Password", type="password")
 
    if st.button("Register"):
        if user_coll.get(ids=[new_u])["ids"]:
            st.error("User exists!")
        else:
            user_coll.add(
                ids=[new_u],
                documents=["profile"],
                metadatas=[{"pw": new_p}]
            )
            st.success("Registered!")