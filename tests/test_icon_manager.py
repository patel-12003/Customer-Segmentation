"""
Tests for IconManager class.

Validates icon generation, mappings, and HTML output.
"""

import pytest
from src.ui.icon_manager import IconManager


class TestIconManager:
    """Test suite for IconManager functionality."""
    
    def test_get_icon_basic(self):
        """Test basic icon generation."""
        icon_html = IconManager.get_icon("home")
        
        assert "home" in icon_html
        assert "material-icons" in icon_html
        assert "#00d2ff" in icon_html  # Default cyan color
    
    def test_get_icon_with_size(self):
        """Test icon generation with different sizes."""
        sizes = ["sm", "md", "lg", "xl"]
        expected_px = [16, 20, 28, 36]
        
        for size, px in zip(sizes, expected_px):
            icon_html = IconManager.get_icon("home", size=size)
            assert f"{px}px" in icon_html
    
    def test_get_icon_with_color_name(self):
        """Test icon generation with named color."""
        icon_html = IconManager.get_icon("home", color="green")
        assert "#00e676" in icon_html
    
    def test_get_icon_with_hex_color(self):
        """Test icon generation with hex color code."""
        icon_html = IconManager.get_icon("home", color="#FF0000")
        assert "#FF0000" in icon_html
    
    def test_emoji_mapping(self):
        """Test emoji to icon name mapping."""
        icon_html = IconManager.get_icon("🏠")
        assert "home" in icon_html
        
        icon_html2 = IconManager.get_icon("📊")
        assert "bar_chart" in icon_html2
    
    def test_icon_mapping_coverage(self):
        """Test that all mapped emojis produce valid icons."""
        for emoji, expected_name in IconManager.ICON_MAPPINGS.items():
            icon_html = IconManager.get_icon(emoji)
            assert expected_name in icon_html
            assert "material-icons" in icon_html
    
    def test_get_icon_for_page(self):
        """Test page name to icon mapping."""
        assert IconManager.get_icon_for_page("🏠 Home") == "home"
        assert IconManager.get_icon_for_page("📊 Dashboard") == "bar_chart"  # Emoji takes precedence
        assert IconManager.get_icon_for_page("Dashboard") == "home"  # Without emoji, infers from name
        assert IconManager.get_icon_for_page("ℹ️ About Project") == "info"
        assert IconManager.get_icon_for_page("Dataset Overview") == "table_chart"
        assert IconManager.get_icon_for_page("EDA Dashboard") == "search"
        assert IconManager.get_icon_for_page("Cluster Visualization") == "adjust"
        assert IconManager.get_icon_for_page("Customer Prediction") == "smart_toy"
        assert IconManager.get_icon_for_page("Business Insights") == "lightbulb"
    
    def test_render_nav_icon(self):
        """Test navigation icon rendering with active state."""
        # Inactive icon should use gray
        inactive = IconManager.render_nav_icon("home", active=False)
        assert "#9aa6b2" in inactive
        
        # Active icon should use cyan
        active = IconManager.render_nav_icon("home", active=True)
        assert "#00d2ff" in active
    
    def test_render_status_icon(self):
        """Test status icon rendering."""
        success = IconManager.render_status_icon("success")
        assert "check_circle" in success
        assert "#00e676" in success  # Green
        
        warning = IconManager.render_status_icon("warning")
        assert "warning" in warning
        assert "#ffab40" in warning  # Orange
        
        error = IconManager.render_status_icon("error")
        assert "cancel" in error
        assert "#ff5252" in error  # Red
        
        info = IconManager.render_status_icon("info")
        assert "info" in info
        assert "#00d2ff" in info  # Cyan
    
    def test_default_size(self):
        """Test that default size is 'md' (20px)."""
        icon_html = IconManager.get_icon("home")
        assert "20px" in icon_html
    
    def test_default_color(self):
        """Test that default color is cyan."""
        icon_html = IconManager.get_icon("home")
        assert "#00d2ff" in icon_html
    
    def test_icon_style_variants(self):
        """Test different Material Icons style variants."""
        styles = [
            "material-icons",
            "material-icons-outlined",
            "material-icons-round",
            "material-icons-sharp",
        ]
        
        for style in styles:
            icon_html = IconManager.get_icon("home", style=style)
            assert style in icon_html
    
    def test_size_map_completeness(self):
        """Test that all size options are defined."""
        assert "sm" in IconManager.SIZE_MAP
        assert "md" in IconManager.SIZE_MAP
        assert "lg" in IconManager.SIZE_MAP
        assert "xl" in IconManager.SIZE_MAP
    
    def test_default_colors_completeness(self):
        """Test that all theme colors are defined."""
        expected_colors = ["cyan", "purple", "green", "orange", "pink", "red", "white", "gray"]
        for color in expected_colors:
            assert color in IconManager.DEFAULT_COLORS
    
    def test_invalid_size_fallback(self):
        """Test that invalid size falls back to 'md'."""
        icon_html = IconManager.get_icon("home", size="invalid")
        assert "20px" in icon_html  # md default
    
    def test_html_safety(self):
        """Test that generated HTML is safe and properly formatted."""
        icon_html = IconManager.get_icon("home")
        
        # Should contain span tag
        assert "<span" in icon_html
        assert "</span>" in icon_html
        
        # Should contain style attribute
        assert "style=" in icon_html
        
        # Should not contain script tags
        assert "<script" not in icon_html.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
