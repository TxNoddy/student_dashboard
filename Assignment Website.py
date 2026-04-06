import streamlit as st
import os
import glob
import base64

# Set global configuration for the entire web app
st.set_page_config(
    page_title="REM Assignments Hub",
    page_icon="🌍",
    layout="wide"
)

# Helper function to display PDFs natively inline via iframe
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf" style="border: 1px solid #ccc; border-radius: 8px;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("📚 Course Hub")
st.sidebar.markdown("Navigate through the assignments below. Any viewer can see your live apps, documents, and images!")
st.sidebar.divider()

# Provide exactly 10 slots
assignment_list = [f"Assignment {i}" for i in range(1, 11)]
selected_assignment = st.sidebar.selectbox("Go to...", assignment_list)

st.sidebar.divider()
st.sidebar.caption("Hosted with Streamlit")

# -----------------------------
# MAIN VIEW AREA
# -----------------------------
st.title(f"🎓 REM Portfolio: {selected_assignment}")

# 1. FIND EXISTING FILES
# Discover any files mapping to this specific assignment slot
matching_files = []

# Special case for existing Enterprise Assignment 3
if selected_assignment == "Assignment 3" and os.path.exists("REM Assignment no 3.py"):
    matching_files.append("REM Assignment no 3.py")

# Grab all other matched extensions (e.g., Assignment 1.pdf, Assignment 1.png, etc.)
for file in glob.glob(f"{selected_assignment}.*"):
    if file not in matching_files:
        matching_files.append(file)

# 2. RENDER EXISTING FILES DYNAMICALLY
if len(matching_files) > 0:
    for file_path in matching_files:
        ext = file_path.split('.')[-1].lower()
        
        st.markdown(f"### 📄 Attached File: `{file_path}`")
        
        # Universally provide a download button for any uploaded file format
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"📥 Download {file_path}",
                data=f,
                file_name=file_path,
                mime="application/octet-stream"
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
            
        # Specific Rendering Logic Based on File Type
        if ext == 'py':
            with st.expander("🛠️ View Source Code", expanded=False):
                with open(file_path, "r", encoding="utf-8") as f:
                    st.code(f.read(), language="python")

            st.markdown("---")
            st.markdown("#### 🖥️ Live Python App Output")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                
                # Strip st.set_page_config since the global hub already sets it
                safe_code_lines = [line for line in code.split('\\n') if 'st.set_page_config' not in line]
                safe_code = '\\n'.join(safe_code_lines)
                
                # Execute the app inside the view
                exec(safe_code, globals())
            except Exception as e:
                st.error(f"❌ Error encountered running the Python script: {e}")
                
        elif ext == 'pdf':
            # Renders PDF directly in browser
            show_pdf(file_path)
            
        elif ext in ['png', 'jpg', 'jpeg']:
            # Render images
            st.image(file_path, use_column_width=True)
            
        elif ext in ['doc', 'docx']:
            # For Word Files, we just prompt them to download
            st.info("📝 Word documents cannot be natively drawn inside web browsers securely. Please click the Download button above to view it in Microsoft Word.")
            
        st.markdown("---")

else:
    st.info(f"The `{selected_assignment}` slot is currently empty.")

# 3. FILE UPLOADER (ADD FROM FILE)
st.markdown("#### ➕ Add File to This Assignment")
st.markdown("Upload Python scripts, PDFs, Word documents, or Images. (You can securely upload multiple file types to the same assignment!)")

uploaded_files = st.file_uploader(
    "Drop your files securely here:", 
    type=['py', 'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        original_ext = uploaded_file.name.split('.')[-1].lower()
        
        # Format the saved file natively into the backend so it maps automatically to the dropdown
        if selected_assignment == "Assignment 3" and original_ext == "py":
            save_name = "REM Assignment no 3.py"
        else:
            save_name = f"{selected_assignment}.{original_ext}"
            
        with open(save_name, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
    st.success(f"✅ Successfully uploaded to **{selected_assignment}**!")
    st.info("Refreshing website...")
    st.rerun()
