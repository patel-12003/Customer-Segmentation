"""
Demo script for IconManager usage.

Shows various use cases for the professional icon system.
Run with: streamlit run examples/icon_manager_demo.py
"""

import streamlit as st
from src.ui.icon_manager import IconManager

# Initialize Material Icons font
IconManager.inject_material_icons_font()

st.title("IconManager Demo")
st.markdown("---")

# Section 1: Basic Icons
st.header("Basic Icon Usage")
st.markdown("### Different Sizes")
cols = st.columns(4)
for idx, size in enumerate(["sm", "md", "lg", "xl"]):
    with cols[idx]:
        st.markdown(f"**{size.upper()}**")
        icon_html = IconManager.get_icon("home", size=size)
        st.markdown(icon_html, unsafe_allow_html=True)

st.markdown("### Different Colors")
cols = st.columns(5)
colors = ["cyan", "purple", "green", "orange", "pink"]
for idx, color in enumerate(colors):
    with cols[idx]:
        st.markdown(f"**{color}**")
        icon_html = IconManager.get_icon("star", size="lg", color=color)
        st.markdown(icon_html, unsafe_allow_html=True)

st.markdown("---")

# Section 2: Emoji Mapping
st.header("Emoji to Icon Mapping")
st.markdown("Automatically converts emojis to professional icons:")
cols = st.columns(5)
emojis = ["🏠", "📊", "🔍", "🤖", "💡"]
for idx, emoji in enumerate(emojis):
    with cols[idx]:
        st.markdown(f"**{emoji}**")
        icon_html = IconManager.get_icon(emoji, size="lg")
        st.markdown(icon_html, unsafe_allow_html=True)
        st.caption(f"→ {IconManager.ICON_MAPPINGS[emoji]}")

st.markdown("---")

# Section 3: Navigation Icons
st.header("Navigation Icons")
st.markdown("Icons with active/inactive states:")
pages = [
    "🏠 Home",
    "📊 Dataset Overview",
    "🔍 EDA Dashboard",
    "🎯 Cluster Visualization",
    "🤖 Customer Prediction",
    "💡 Business Insights"
]

selected_page = st.radio("Select a page:", pages, label_visibility="collapsed")

for page in pages:
    is_active = (page == selected_page)
    icon_name = IconManager.get_icon_for_page(page)
    icon_html = IconManager.render_nav_icon(icon_name, size="md", active=is_active)
    
    status = "**Active**" if is_active else "Inactive"
    st.markdown(f"{icon_html} {page} — {status}", unsafe_allow_html=True)

st.markdown("---")

# Section 4: Status Icons
st.header("Status Icons")
st.markdown("Icons for different status states:")
cols = st.columns(4)
statuses = ["success", "warning", "error", "info"]
for idx, status in enumerate(statuses):
    with cols[idx]:
        icon_html = IconManager.render_status_icon(status, size="lg")
        st.markdown(icon_html, unsafe_allow_html=True)
        st.caption(status.capitalize())

st.markdown("---")

# Section 5: Icon Button (Note: This is a workaround since Streamlit doesn't support HTML in buttons)
st.header("Icon Buttons")
st.markdown("Buttons with icon prefixes:")

col1, col2, col3 = st.columns(3)
with col1:
    if IconManager.render_icon_button("upload", "Upload File", "upload_demo"):
        st.success("Upload clicked!")

with col2:
    if IconManager.render_icon_button("download", "Download Report", "download_demo"):
        st.success("Download clicked!")

with col3:
    if IconManager.render_icon_button("refresh", "Refresh Data", "refresh_demo"):
        st.success("Refresh clicked!")

st.markdown("---")

# Section 6: Custom Styling
st.header("Custom Styling Examples")
st.markdown("### Icon with Custom Hex Color")
icon_html = IconManager.get_icon("palette", size="xl", color="#FF6B6B")
st.markdown(icon_html, unsafe_allow_html=True)

st.markdown("### Different Icon Styles")
cols = st.columns(4)
styles = ["material-icons", "material-icons-outlined", "material-icons-round", "material-icons-sharp"]
for idx, style in enumerate(styles):
    with cols[idx]:
        icon_html = IconManager.get_icon("star", size="lg", style=style)
        st.markdown(icon_html, unsafe_allow_html=True)
        st.caption(style.split("-")[-1].capitalize())

st.markdown("---")

# Section 7: All Available Emoji Mappings
st.header("All Available Emoji Mappings")
st.markdown("Complete list of emoji-to-icon mappings:")

# Display in a table
mapping_data = []
for emoji, icon_name in IconManager.ICON_MAPPINGS.items():
    mapping_data.append({
        "Emoji": emoji,
        "Icon Name": icon_name,
        "Preview": IconManager.get_icon(emoji, size="md")
    })

# Split into columns for better display
col1, col2 = st.columns(2)
half = len(mapping_data) // 2

with col1:
    for item in mapping_data[:half]:
        st.markdown(f"{item['Preview']} **{item['Emoji']}** → `{item['Icon Name']}`", unsafe_allow_html=True)

with col2:
    for item in mapping_data[half:]:
        st.markdown(f"{item['Preview']} **{item['Emoji']}** → `{item['Icon Name']}`", unsafe_allow_html=True)
