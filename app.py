import streamlit as st
import asyncio
import os
from autogen_backend import run_litrev, EXPORT_DIR 

st.set_page_config(page_title="AI-Powered Literature Review", layout="wide")
st.title("📚Literature Review Assistant")

with st.sidebar:
    st.header("🔧 Configuration")
    topic = st.text_input("Enter topic", value="Enter your required query.....")
    num_papers = st.slider("Number of Papers", 1, 10, value=4)
    model = st.selectbox("LLM Model", ["gemini-2.5-flash"])
    run_button = st.button("🔍 Generate Literature Review")

output_area = st.empty()

if run_button:
    output_area.markdown("⏳ Generating literature review... Please wait.")

    async def stream_and_display():
        markdown_lines = ""
        async for chunk in run_litrev(topic, num_papers=num_papers, model=model):
            markdown_lines = chunk
            output_area.markdown(markdown_lines)

        # Find latest export file
        files = sorted(os.listdir(EXPORT_DIR), reverse=True)
        latest_base = os.path.splitext(files[0])[0].replace(".md", "")
        md_path = os.path.join(EXPORT_DIR, f"{latest_base}.md")

        st.success("✅ Review completed!")
        with st.expander("📄 Download Files"):
            st.download_button("⬇️ Download Markdown", open(md_path, "rb"), file_name=os.path.basename(md_path))

    asyncio.run(stream_and_display())
