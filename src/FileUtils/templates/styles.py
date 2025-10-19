"""Style mapping utilities for DOCX templates."""

from typing import Dict, Any, Optional


class StyleMapper:
    """Maps style types to actual DOCX style names."""
    
    def __init__(self, style_mappings: Optional[Dict[str, str]] = None):
        """Initialize style mapper.
        
        Args:
            style_mappings: Custom style mappings
        """
        self.style_mappings = style_mappings or self._get_default_mappings()
    
    def _get_default_mappings(self) -> Dict[str, str]:
        """Get default style mappings."""
        return {
            "table": "IP-table_light",
            "table_fallback": "IP-table", 
            "table_default": "Table Grid",
            "heading_1": "Heading 1",
            "heading_2": "Heading 2",
            "heading_3": "Heading 3", 
            "heading_4": "Heading 4",
            "heading_5": "Heading 5",
            "heading_6": "Heading 6",
            "list_bullet": "List Bullet",
            "list_number": "List Number", 
            "list_paragraph": "List Paragraph",
            "normal": "Normal",
            "title": "Title",
            "subtitle": "Subtitle"
        }
    
    def get_style(self, style_type: str, fallback: Optional[str] = None) -> str:
        """Get style name for a style type.
        
        Args:
            style_type: Type of style to get
            fallback: Fallback style if not found
            
        Returns:
            Style name to use
        """
        return self.style_mappings.get(style_type, fallback or style_type)
    
    def get_table_style_chain(self) -> list[str]:
        """Get chain of table styles to try in order."""
        return [
            self.style_mappings.get("table"),
            self.style_mappings.get("table_fallback"),
            self.style_mappings.get("table_default"),
            "Table Grid"
        ]
    
    def apply_style_safely(self, element, style_name: str) -> bool:
        """Apply style to element safely with fallback.
        
        Args:
            element: DOCX element to style
            style_name: Style name to apply
            
        Returns:
            True if style was applied successfully
        """
        try:
            element.style = style_name
            return True
        except Exception:
            # Try fallback styles
            for fallback_style in self.get_table_style_chain():
                if fallback_style and fallback_style != style_name:
                    try:
                        element.style = fallback_style
                        return True
                    except Exception:
                        continue
            return False
