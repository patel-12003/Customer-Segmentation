"""
IconManager — Professional icon system replacement for emojis.

Provides a centralized interface for rendering professional icons from
streamlit-icons or Material Icons library throughout the application.
Replaces emoji-based icons with professional alternatives that maintain
the dark theme aesthetic.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st


class IconManager:
    """
    Manages professional icon display across the UI.
    
    Provides methods to render individual icons and icon buttons with
    consistent sizing, coloring, and styling that matches the dark theme.
    """
    
    # Icon size mappings (in pixels)
    SIZE_MAP = {
        "sm": 16,
        "md": 20,
        "lg": 28,
        "xl": 36,
    }
    
    # Default dark theme colors
    DEFAULT_COLORS = {
        "cyan": "#00d2ff",
        "purple": "#7c4dff",
        "green": "#00e676",
        "orange": "#ffab40",
        "pink": "#ff4081",
        "red": "#ff5252",
        "white": "#e8eef5",
        "gray": "#9aa6b2",
    }
    
    # Emoji to professional icon mappings
    # Maps common emojis to Material Icons names
    ICON_MAPPINGS = {
        "🏠": "home",
        "📊": "bar_chart",
        "🔍": "search",
        "🎯": "adjust",
        "🤖": "smart_toy",
        "💡": "lightbulb",
        "⬆️": "upload",
        "⬇️": "download",
        "🔧": "settings",
        "ℹ️": "info",
        "📈": "trending_up",
        "📉": "trending_down",
        "✅": "check_circle",
        "❌": "cancel",
        "⚠️": "warning",
        "🔄": "refresh",
        "📁": "folder",
        "📝": "edit",
        "👤": "person",
        "👥": "group",
        "📅": "calendar_today",
        "🕒": "access_time",
        "🌐": "language",
        "🔗": "link",
        "📧": "email",
        "💾": "save",
        "🖨️": "print",
        "🎨": "palette",
        "🔒": "lock",
        "🔓": "lock_open",
        "🚀": "rocket_launch",
        "⭐": "star",
        "🎉": "celebration",
        "🛍️": "shopping_cart",
    }
    
    @staticmethod
    def get_icon(
        name: str,
        size: str = "md",
        color: Optional[str] = None,
        style: str = "material-icons",
    ) -> str:
        """
        Returns HTML/markdown for a professional icon.
        
        Args:
            name: Icon identifier (e.g., "home", "upload", "bar_chart")
                  Can be an emoji (will be mapped to professional icon)
                  or a Material Icons name.
            size: Icon size ("sm", "md", "lg", "xl"). Defaults to "md".
            color: Color name from theme palette or hex color code.
                   If None, uses default cyan (#00d2ff).
            style: Icon library style. Defaults to "material-icons".
                   Options: "material-icons", "material-icons-outlined",
                   "material-icons-round", "material-icons-sharp"
        
        Returns:
            HTML string for rendering the icon.
        
        Example:
            >>> IconManager.get_icon("home", size="lg", color="cyan")
            '<span class="material-icons" ...>home</span>'
        """
        # Map emoji to icon name if provided
        if name in IconManager.ICON_MAPPINGS:
            name = IconManager.ICON_MAPPINGS[name]
        
        # Get size in pixels
        size_px = IconManager.SIZE_MAP.get(size, IconManager.SIZE_MAP["md"])
        
        # Resolve color
        if color is None:
            color_hex = IconManager.DEFAULT_COLORS["cyan"]
        elif color in IconManager.DEFAULT_COLORS:
            color_hex = IconManager.DEFAULT_COLORS[color]
        else:
            color_hex = color  # Assume it's a hex code
        
        # Generate HTML for Material Icons
        html = f"""
        <span class="{style}" style="
            font-size: {size_px}px;
            color: {color_hex};
            vertical-align: middle;
            line-height: 1;
            user-select: none;
        ">{name}</span>
        """
        
        return html
    
    @staticmethod
    def render_icon(
        name: str,
        size: str = "md",
        color: Optional[str] = None,
        style: str = "material-icons",
    ) -> None:
        """
        Renders an icon directly to Streamlit.
        
        Args:
            name: Icon identifier or emoji.
            size: Icon size ("sm", "md", "lg", "xl").
            color: Color name or hex code.
            style: Material Icons style variant.
        """
        icon_html = IconManager.get_icon(name, size, color, style)
        st.markdown(icon_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_icon_button(
        icon: str,
        label: str,
        key: str,
        size: str = "md",
        color: Optional[str] = None,
        disabled: bool = False,
    ) -> bool:
        """
        Renders a button with an icon prefix.
        
        Args:
            icon: Icon name or emoji.
            label: Button label text.
            key: Unique Streamlit key for the button.
            size: Icon size ("sm", "md", "lg", "xl").
            color: Icon color name or hex code.
            disabled: Whether the button is disabled.
        
        Returns:
            True if button is clicked, False otherwise.
        
        Example:
            >>> if IconManager.render_icon_button("upload", "Upload Data", "upload_btn"):
            ...     st.write("Button clicked!")
        """
        # Get icon HTML
        icon_html = IconManager.get_icon(icon, size=size, color=color)
        
        # Create button with icon and label
        # Use columns to align icon and text within button
        button_html = f"""
        <style>
        .icon-button {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        </style>
        <div class="icon-button">
            {icon_html}
            <span>{label}</span>
        </div>
        """
        
        # Render button using Streamlit
        # Note: We need to use st.button with custom HTML label
        # But Streamlit doesn't support HTML in button text directly
        # So we'll display the icon separately and use standard button
        
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            st.markdown(icon_html, unsafe_allow_html=True)
        with col2:
            clicked = st.button(label, key=key, disabled=disabled, use_container_width=True)
        
        return clicked
    
    @staticmethod
    def get_icon_for_page(page_name: str) -> str:
        """
        Returns the appropriate icon name for a navigation page.
        
        Args:
            page_name: Page title (e.g., "🏠 Home", "Dashboard").
        
        Returns:
            Icon name suitable for the page.
        
        Example:
            >>> IconManager.get_icon_for_page("🏠 Home")
            'home'
            >>> IconManager.get_icon_for_page("Dashboard")
            'dashboard'
        """
        # Extract emoji if present and map it
        for emoji, icon_name in IconManager.ICON_MAPPINGS.items():
            if emoji in page_name:
                return icon_name
        
        # Otherwise, infer from page name (check specific terms first)
        page_lower = page_name.lower()
        
        # Check specific terms before general ones
        if "eda" in page_lower or "explore" in page_lower or "analysis" in page_lower:
            return "search"
        elif "cluster" in page_lower or "segment" in page_lower:
            return "adjust"
        elif "predict" in page_lower or "classification" in page_lower:
            return "smart_toy"
        elif "insight" in page_lower or "business" in page_lower:
            return "lightbulb"
        elif "upload" in page_lower:
            return "upload"
        elif "report" in page_lower or "download" in page_lower:
            return "download"
        elif "dataset" in page_lower or "data" in page_lower:
            return "table_chart"
        elif "about" in page_lower or "info" in page_lower:
            return "info"
        elif "home" in page_lower or "dashboard" in page_lower:
            return "home"
        else:
            return "circle"  # Default fallback
    
    @staticmethod
    def render_nav_icon(icon_name: str, size: str = "md", active: bool = False) -> str:
        """
        Returns HTML for a navigation icon with optional active state.
        
        Args:
            icon_name: Icon name or emoji.
            size: Icon size.
            active: Whether this is the active/selected navigation item.
        
        Returns:
            HTML string for the navigation icon.
        """
        color = "cyan" if active else "gray"
        return IconManager.get_icon(icon_name, size=size, color=color)
    
    @staticmethod
    def render_status_icon(status: str, size: str = "sm") -> str:
        """
        Returns HTML for a status indicator icon.
        
        Args:
            status: Status type ("success", "warning", "error", "info").
            size: Icon size.
        
        Returns:
            HTML string for the status icon.
        """
        icon_map = {
            "success": ("check_circle", "green"),
            "warning": ("warning", "orange"),
            "error": ("cancel", "red"),
            "info": ("info", "cyan"),
        }
        
        icon_name, color = icon_map.get(status, ("info", "cyan"))
        return IconManager.get_icon(icon_name, size=size, color=color)
    
    @staticmethod
    def inject_material_icons_font() -> None:
        """
        Injects the Material Icons font stylesheet into the Streamlit app.
        
        This should be called once at app startup to ensure icons render properly.
        """
        st.markdown(
            """
            <link href="https://fonts.googleapis.com/css2?family=Material+Icons" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css2?family=Material+Icons+Outlined" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css2?family=Material+Icons+Round" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css2?family=Material+Icons+Sharp" rel="stylesheet">
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Convenience functions for common icon operations
# ---------------------------------------------------------------------------

def icon(name: str, size: str = "md", color: Optional[str] = None) -> str:
    """Shorthand for IconManager.get_icon()."""
    return IconManager.get_icon(name, size, color)


def render_icon(name: str, size: str = "md", color: Optional[str] = None) -> None:
    """Shorthand for IconManager.render_icon()."""
    IconManager.render_icon(name, size, color)


def icon_button(icon_name: str, label: str, key: str, **kwargs) -> bool:
    """Shorthand for IconManager.render_icon_button()."""
    return IconManager.render_icon_button(icon_name, label, key, **kwargs)
