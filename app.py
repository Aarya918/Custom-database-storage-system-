
import streamlit as st
from lsm_store import LSMStore

# Page configuration
st.set_page_config(
    page_title="Custom Database Storage System",
    page_icon="🗄️",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
h1 {
    color: #243b63;
}
.stButton button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# Initialize your existing database engine
@st.cache_resource
def get_database():
    return LSMStore()

try:
    db = get_database()
except Exception as e:
    st.error(f"Database initialization failed: {e}")
    st.stop()

# Header
st.title("🗄️ Custom Database Storage System")
st.subheader("LSM-Tree Based Key-Value Database")
st.caption("Powered by Python | MemTable | SSTables | Write-Ahead Log")

st.divider()

# Dashboard
st.header("Database Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Storage Engine", "LSM-Tree")

with col2:
    st.metric("Database Status", "Connected")

with col3:
    st.metric("Operations", "PUT / GET / DELETE")

st.divider()

# Database operations
st.header("Database Operations")

tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Insert Data",
    "🔍 Search Data",
    "🗑️ Delete Data",
    "⚙️ Maintenance"
])

with tab1:
    st.subheader("Insert a Key-Value Pair")

    key = st.text_input("Enter Key", key="put_key")
    value = st.text_area("Enter Value", key="put_value")

    if st.button("PUT - Save Data", type="primary"):
        if key.strip():
            try:
                db.put(key, value)
                st.success(f"Successfully stored key: {key}")
            except Exception as e:
                st.error(f"Insert failed: {e}")
        else:
            st.warning("Please enter a key.")

with tab2:
    st.subheader("Retrieve Stored Data")

    search_key = st.text_input("Enter Key to Search", key="get_key")

    if st.button("GET - Search Data", type="primary"):
        if search_key.strip():
            try:
                result = db.get(search_key)

                if isinstance(result, bytes):
                    result = result.decode("utf-8", errors="replace")

                if result is None:
                    st.warning("Key not found.")
                else:
                    st.success("Key found!")
                    st.code(str(result))
            except Exception as e:
                st.error(f"Search failed: {e}")
        else:
            st.warning("Please enter a key.")

with tab3:
    st.subheader("Delete Stored Data")

    delete_key = st.text_input("Enter Key to Delete", key="delete_key")

    if st.button("DELETE - Remove Data", type="primary"):
        if delete_key.strip():
            try:
                db.delete(delete_key)
                st.success(f"Delete operation completed for: {delete_key}")
            except Exception as e:
                st.error(f"Delete failed: {e}")
        else:
            st.warning("Please enter a key.")

with tab4:
    st.subheader("Database Maintenance")

    st.write("Flush the MemTable or compact SSTables.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Flush MemTable"):
            try:
                if hasattr(db, "flush"):
                    db.flush()
                    st.success("Flush completed.")
                else:
                    st.warning("Your database does not expose a flush() method.")
            except Exception as e:
                st.error(f"Flush failed: {e}")

    with col2:
        if st.button("Compact SSTables"):
            try:
                if hasattr(db, "compact"):
                    db.compact()
                    st.success("Compaction completed.")
                elif hasattr(db, "compaction"):
                    db.compaction()
                    st.success("Compaction completed.")
                else:
                    st.warning("Your database does not expose a compaction method.")
            except Exception as e:
                st.error(f"Compaction failed: {e}")

st.divider()

st.markdown("""
### About This Project

This project implements a custom database storage engine
using Log-Structured Merge Trees (LSM-Trees).

**Core Concepts**
- Write-Ahead Logging (WAL)
- MemTable
- Sorted String Tables (SSTables)
- Flush operations
- Compaction

**Developed using Python and Streamlit.**
""")
