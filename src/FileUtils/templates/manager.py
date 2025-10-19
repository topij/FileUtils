"""DOCX Template Manager for FileUtils.

Manages DOCX templates, style mappings, and template configuration.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
import yaml

from ..utils.common import get_logger


class DocxTemplateManager:
    """Manages DOCX templates and their configurations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize template manager.
        
        Args:
            config: Configuration dictionary containing template settings
        """
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        self.template_config = self._load_template_config()
        self.style_mappings = self._load_style_mappings()
    
    def _load_template_config(self) -> Dict[str, Any]:
        """Load template configuration from config or defaults."""
        template_config = self.config.get("docx_templates", {})
        
        # Default template configuration
        default_config = {
            "template_dir": "templates",
            "default_template": "IP-template-doc.docx",
            "templates": {
                "default": "IP-template-doc.docx",
                "review": "IP-template-doc.docx",  # Can be different
                "report": "IP-template-doc.docx"   # Can be different
            },
            "fallback_template": None  # Use python-docx default
        }
        
        # Merge with provided config
        for key, value in template_config.items():
            if key in default_config:
                if isinstance(default_config[key], dict) and isinstance(value, dict):
                    default_config[key].update(value)
                else:
                    default_config[key] = value
            else:
                default_config[key] = value
        
        return default_config
    
    def _load_style_mappings(self) -> Dict[str, str]:
        """Load style mappings from config or defaults."""
        style_config = self.config.get("style_mapping", {})
        
        # Default style mappings
        default_mappings = {
            "table": "IP-table_light",
            "table_fallback": "IP-table",
            "table_default": "Table Grid",
            "heading_1": "Heading 1",
            "heading_2": "Heading 2", 
            "heading_3": "Heading 3",
            "list_bullet": "List Bullet",
            "list_number": "List Number",
            "list_paragraph": "List Paragraph",
            "normal": "Normal"
        }
        
        # Merge with provided mappings
        default_mappings.update(style_config)
        return default_mappings
    
    def get_template_path(self, template_name: Optional[str] = None) -> Optional[Path]:
        """Get the path to a specific template.
        
        Args:
            template_name: Name of the template to use
            
        Returns:
            Path to template file or None if not found
        """
        if not template_name:
            template_name = self.template_config.get("default_template")
        
        # Get template filename
        template_filename = self.template_config.get("templates", {}).get(template_name)
        if not template_filename:
            self.logger.warning(f"Template '{template_name}' not found in configuration")
            return None
        
        # Look for template in multiple locations
        template_dir = self.template_config.get("template_dir", "templates")
        search_paths = [
            Path(template_dir) / template_filename,
            Path("templates") / template_filename,
            Path("data/templates") / template_filename,
            Path(template_filename),  # Current directory
            Path("src/conversion/templates") / template_filename,  # Your old location
        ]
        
        for template_path in search_paths:
            if template_path.exists():
                self.logger.debug(f"Found template: {template_path}")
                return template_path
        
        self.logger.warning(f"Template file '{template_filename}' not found in any location")
        return None
    
    def get_style_name(self, style_type: str) -> str:
        """Get the style name for a specific style type.
        
        Args:
            style_type: Type of style (e.g., 'table', 'heading_1')
            
        Returns:
            Style name to use in DOCX
        """
        return self.style_mappings.get(style_type, style_type)
    
    def get_table_style_with_fallback(self) -> str:
        """Get table style with fallback chain.
        
        Returns:
            First available table style
        """
        fallback_chain = [
            self.style_mappings.get("table"),
            self.style_mappings.get("table_fallback"), 
            self.style_mappings.get("table_default"),
            "Table Grid"  # Final fallback
        ]
        
        for style in fallback_chain:
            if style:
                return style
        
        return "Table Grid"  # Ultimate fallback
    
    def validate_template(self, template_path: Path) -> bool:
        """Validate that a template file exists and is readable.
        
        Args:
            template_path: Path to template file
            
        Returns:
            True if template is valid, False otherwise
        """
        try:
            if not template_path.exists():
                return False
            
            # Try to open with python-docx to validate
            from docx import Document
            doc = Document(template_path)
            return True
        except Exception as e:
            self.logger.error(f"Template validation failed for {template_path}: {e}")
            return False
    
    def list_available_templates(self) -> Dict[str, Path]:
        """List all available templates.
        
        Returns:
            Dictionary mapping template names to their paths
        """
        available = {}
        template_dir = self.template_config.get("template_dir", "templates")
        
        # Check configured templates
        for name, filename in self.template_config.get("templates", {}).items():
            template_path = self.get_template_path(name)
            if template_path:
                available[name] = template_path
        
        # Also scan template directory for additional templates
        template_dir_path = Path(template_dir)
        if template_dir_path.exists():
            for template_file in template_dir_path.glob("*.docx"):
                if template_file not in available.values():
                    name = template_file.stem
                    available[name] = template_file
        
        return available
    
    def get_template_info(self, template_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a template.
        
        Args:
            template_name: Name of template to get info for
            
        Returns:
            Dictionary with template information
        """
        template_path = self.get_template_path(template_name)
        if not template_path:
            return {"error": f"Template '{template_name}' not found"}
        
        try:
            from docx import Document
            doc = Document(template_path)
            
            # Get available styles
            available_styles = [style.name for style in doc.styles]
            
            return {
                "name": template_name or "default",
                "path": str(template_path),
                "exists": True,
                "available_styles": available_styles,
                "style_count": len(available_styles),
                "paragraph_count": len(doc.paragraphs),
                "table_count": len(doc.tables)
            }
        except Exception as e:
            return {
                "name": template_name or "default", 
                "path": str(template_path),
                "exists": True,
                "error": str(e)
            }
