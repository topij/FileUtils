"""Local filesystem storage implementation."""

import csv
from pathlib import Path
import yaml
import json
import tempfile
from typing import Dict, Optional, Union, Any

import pandas as pd

from ..core.base import BaseStorage, StorageOperationError
from ..utils.common import ensure_path


class LocalStorage(BaseStorage):
    """Local filesystem storage implementation."""

    def save_dataframe(
        self, df: pd.DataFrame, file_path: Union[str, Path], **kwargs
    ) -> str:
        """Save DataFrame to local filesystem.
        
        Args:
            df: DataFrame to save
            file_path: Path to save to
            **kwargs: Additional arguments for saving:
                - sheet_name: Sheet name for Excel files
                - orient: Orientation for JSON files ("records", "index", etc.)
                - yaml_options: Dict of options for yaml.safe_dump
                - compression: Compression options for parquet files
            
        Returns:
            String path where the file was saved
        """
        try:
            path = ensure_path(file_path)
            suffix = path.suffix.lower()

            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            if suffix == ".csv":
                df.to_csv(
                    path,
                    index=False,
                    encoding=self.config["encoding"],
                    sep=self.config["csv_delimiter"],
                )
            elif suffix == ".parquet":
                compression = kwargs.get("compression", "snappy")
                df.to_parquet(path, index=False, compression=compression)
            elif suffix in (".xlsx", ".xls"):
                sheet_name = kwargs.get("sheet_name", "Sheet1")
                with pd.ExcelWriter(path, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            elif suffix == ".json":
                orient = kwargs.get("orient", "records")
                df.to_json(path, orient=orient, indent=2)
            elif suffix == ".yaml" or suffix == ".yml":
                yaml_options = kwargs.get("yaml_options", {})
                default_flow_style = yaml_options.pop("default_flow_style", False)
                sort_keys = yaml_options.pop("sort_keys", False)
                
                # Convert DataFrame to dict based on orient
                orient = kwargs.get("orient", "records")
                if orient == "records":
                    data = df.to_dict(orient="records")
                elif orient == "index":
                    data = df.to_dict(orient="index")
                else:
                    raise ValueError(f"Unsupported YAML orientation: {orient}")
                
                with open(path, "w", encoding=self.config["encoding"]) as f:
                    yaml.safe_dump(
                        data,
                        f,
                        default_flow_style=default_flow_style,
                        sort_keys=sort_keys,
                        encoding=self.config["encoding"],
                        **yaml_options
                    )
            else:
                raise ValueError(f"Unsupported file format: {suffix}")

            return str(path)
        except yaml.YAMLError as e:
            raise StorageOperationError(f"Failed to save YAML file - YAML error: {e}") from e
        except Exception as e:
            raise StorageOperationError(f"Failed to save DataFrame: {e}") from e

    def load_dataframe(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load DataFrame from local filesystem."""
        try:
            path = ensure_path(file_path)
            suffix = path.suffix.lower()

            if suffix == ".csv":
                return self._load_csv_with_inference(path)
            elif suffix == ".parquet":
                return pd.read_parquet(path)
            elif suffix in (".xlsx", ".xls"):
                return pd.read_excel(path, engine="openpyxl")
            elif suffix == ".json":
                return self._load_json_as_dataframe(path)
            elif suffix == ".yaml":
                return self._load_yaml_as_dataframe(path)
            else:
                raise ValueError(f"Unsupported file format: {suffix}")

        except Exception as e:
            raise StorageOperationError(f"Failed to load DataFrame: {e}") from e

    def _load_csv_with_inference(self, path: Path) -> pd.DataFrame:
        """Load CSV with delimiter inference."""
        with open(path, "r", encoding=self.config["encoding"]) as f:
            content = f.read(1024)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(content)
                return pd.read_csv(
                    f,
                    dialect=dialect,
                    encoding=self.config["encoding"],
                    quoting=self.config["quoting"],
                )
            except:
                f.seek(0)
                return pd.read_csv(
                    f,
                    sep=self.config["csv_delimiter"],
                    encoding=self.config["encoding"],
                    quoting=self.config["quoting"],
                )

    def _load_json_as_dataframe(self, path: Path) -> pd.DataFrame:
        """Load JSON file as DataFrame.
        
        Supports both list of records and dictionary formats.
        """
        try:
            with open(path, "r", encoding=self.config["encoding"]) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    raise StorageOperationError(f"Invalid JSON format: {e}")

                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    return df.reindex(sorted(df.columns), axis=1)
                elif isinstance(data, dict):
                    df = pd.DataFrame.from_dict(data, orient="index")
                    return df.reindex(sorted(df.columns), axis=1)
                else:
                    raise ValueError("JSON must contain list of records or dictionary")
        except Exception as e:
            if isinstance(e, StorageOperationError):
                raise
            raise StorageOperationError(f"Failed to load JSON file: {e}") from e

    def _load_yaml_as_dataframe(self, path: Path) -> pd.DataFrame:
        """Load YAML file as DataFrame.
        
        Supports both list of records and dictionary formats.
        Handles YAML-specific errors separately for better error messages.
        """
        try:
            with open(path, "r", encoding=self.config["encoding"]) as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    raise StorageOperationError(f"Invalid YAML format: {e}")

                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    return df.reindex(sorted(df.columns), axis=1)
                elif isinstance(data, dict):
                    df = pd.DataFrame.from_dict(data, orient="index")
                    return df.reindex(sorted(df.columns), axis=1)
                else:
                    raise ValueError("YAML must contain list of records or dictionary")
        except Exception as e:
            if isinstance(e, StorageOperationError):
                raise
            raise StorageOperationError(f"Failed to load YAML file: {e}") from e

    def exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()

    def delete(self, file_path: Union[str, Path]) -> bool:
        """Delete file from local filesystem."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            raise StorageOperationError(
                f"Failed to delete file from local filesystem: {e}"
            ) from e

    def load_yaml(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Load YAML file from local filesystem."""
        try:
            path = Path(file_path)
            
            # If the exact file doesn't exist, try to find a file with timestamp
            if not path.exists():
                # Look for files matching the pattern (with timestamp)
                pattern = f"{path.stem}_*{path.suffix}"
                matching_files = list(path.parent.glob(pattern))
                
                if matching_files:
                    # Use the most recent file (by modification time)
                    path = max(matching_files, key=lambda f: f.stat().st_mtime)
                else:
                    # If no timestamped file found, raise the original error
                    raise FileNotFoundError(f"File not found: {path}")

            if path.suffix.lower() not in (".yaml", ".yml"):
                raise ValueError("File must have .yaml or .yml extension")

            with open(path, "r", encoding=self.config["encoding"]) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise StorageOperationError(f"Failed to load YAML file: {e}") from e

    def load_json(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Load JSON file from local filesystem."""
        try:
            path = Path(file_path)
            
            # If the exact file doesn't exist, try to find a file with timestamp
            if not path.exists():
                # Look for files matching the pattern (with timestamp)
                pattern = f"{path.stem}_*{path.suffix}"
                matching_files = list(path.parent.glob(pattern))
                
                if matching_files:
                    # Use the most recent file (by modification time)
                    path = max(matching_files, key=lambda f: f.stat().st_mtime)
                else:
                    # If no timestamped file found, raise the original error
                    raise FileNotFoundError(f"File not found: {path}")

            if path.suffix.lower() != ".json":
                raise ValueError("File must have .json extension")

            with open(path, "r", encoding=self.config["encoding"]) as f:
                return json.load(f, **kwargs)
        except Exception as e:
            raise StorageOperationError(f"Failed to load JSON file: {e}") from e

    def save_dataframes(
        self, data: Dict[str, pd.DataFrame], file_path: Union[str, Path], file_format: str, **kwargs
    ) -> Dict[str, str]:
        """Save multiple DataFrames to local filesystem.
        
        Args:
            data: Dictionary of DataFrames to save
            file_path: Path to save to
            file_format: File format to save as
            **kwargs: Additional arguments for saving (e.g., engine for Excel)
            
        Returns:
            Dictionary mapping sheet names to saved file paths. For Excel files,
            all sheets will map to the same file path.
        """
        try:
            path = ensure_path(file_path)

            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            if file_format.lower() in ("xlsx", "xls"):
                # Save all DataFrames to a single Excel file
                with pd.ExcelWriter(path, engine=kwargs.get("engine", "openpyxl")) as writer:
                    for sheet_name, df in data.items():
                        # Handle MultiIndex columns by flattening them
                        if isinstance(df.columns, pd.MultiIndex):
                            df_to_save = df.copy()
                            df_to_save.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df_to_save.columns]
                        else:
                            df_to_save = df
                        
                        # Use index=True for MultiIndex columns, otherwise use index=False
                        include_index = isinstance(df.columns, pd.MultiIndex) or isinstance(df.index, pd.MultiIndex)
                        df_to_save.to_excel(writer, sheet_name=sheet_name, index=include_index)
                # For Excel files, return mapping of sheet names to file path
                return {sheet_name: str(path) for sheet_name in data.keys()}
            else:
                # Save each DataFrame to a separate file
                saved_files = {}
                for sheet_name, df in data.items():
                    # Create unique file name for each sheet
                    sheet_path = path.parent / f"{path.stem}_{sheet_name}.{file_format}"
                    saved_path = self.save_dataframe(df, sheet_path, **kwargs)
                    saved_files[sheet_name] = saved_path
                return saved_files

        except Exception as e:
            raise StorageOperationError(f"Failed to save DataFrames: {e}") from e

    def save_document(
        self, content: Union[str, Dict[str, Any]], file_path: Union[str, Path], file_type: str, **kwargs
    ) -> str:
        """Save document content to local filesystem.
        
        Args:
            content: Document content (string or dict)
            file_path: Path to save to
            file_type: Type of document (docx, md, pdf)
            **kwargs: Additional arguments for saving
            
        Returns:
            String path where the file was saved
        """
        try:
            path = ensure_path(file_path)
            suffix = path.suffix.lower()

            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            if suffix == ".docx":
                return self._save_docx(content, path, **kwargs)
            elif suffix == ".md":
                return self._save_markdown(content, path, **kwargs)
            elif suffix == ".pdf":
                return self._save_pdf(content, path, **kwargs)
            elif suffix == ".json":
                return self._save_json(content, path, **kwargs)
            elif suffix in (".yaml", ".yml"):
                return self._save_yaml(content, path, **kwargs)
            else:
                raise ValueError(f"Unsupported document format: {suffix}")

        except Exception as e:
            raise StorageOperationError(f"Failed to save document: {e}") from e

    def load_document(self, file_path: Union[str, Path], **kwargs) -> Union[str, Dict[str, Any]]:
        """Load document content from local filesystem.
        
        Args:
            file_path: Path to file
            **kwargs: Additional arguments for loading
            
        Returns:
            Document content (string or dict depending on file type)
        """
        try:
            path = ensure_path(file_path)
            suffix = path.suffix.lower()

            if suffix == ".docx":
                return self._load_docx(path, **kwargs)
            elif suffix == ".md":
                return self._load_markdown(path, **kwargs)
            elif suffix == ".pdf":
                return self._load_pdf(path, **kwargs)
            elif suffix == ".json":
                return self._load_json(path, **kwargs)
            elif suffix in (".yaml", ".yml"):
                return self._load_yaml(path, **kwargs)
            else:
                raise ValueError(f"Unsupported document format: {suffix}")

        except Exception as e:
            raise StorageOperationError(f"Failed to load document: {e}") from e

    def _save_docx(self, content: Union[str, Dict[str, Any]], path: Path, **kwargs) -> str:
        """Save content to DOCX format using python-docx with template support."""
        try:
            from docx import Document
            from docx.shared import Inches
        except ImportError:
            raise StorageOperationError(
                "python-docx not installed. Install with: pip install 'FileUtils[documents]'"
            )

        # Check if this is markdown content that should be converted
        if isinstance(content, str) and self._is_markdown_content(content):
            return self._save_markdown_as_docx(content, path, **kwargs)
        
        # Check if template is specified, otherwise use default template
        template_name = kwargs.get("template")
        if template_name is None:
            # Use default template if no template specified
            try:
                from ..templates import DocxTemplateManager
                template_manager = DocxTemplateManager(self.config)
                default_template = template_manager.template_config.get("default_template")
                if default_template:
                    template_name = "default"  # Use the default template name
            except ImportError:
                pass  # Fall back to no template if template system not available
        
        if template_name:
            return self._save_with_template(content, path, template_name, **kwargs)
        
        # Fallback: Default DOCX creation without template
        doc = Document()
        
        if isinstance(content, str):
            # Simple text content
            doc.add_paragraph(content)
        elif isinstance(content, dict):
            # Structured content
            if "title" in content:
                doc.add_heading(content["title"], 0)
            
            if "sections" in content:
                for section in content["sections"]:
                    if "heading" in section:
                        doc.add_heading(section["heading"], level=section.get("level", 1))
                    if "text" in section:
                        doc.add_paragraph(section["text"])
                    if "table" in section and isinstance(section["table"], list):
                        # Add table
                        table = doc.add_table(rows=len(section["table"]), cols=len(section["table"][0]))
                        for i, row in enumerate(section["table"]):
                            for j, cell in enumerate(row):
                                table.cell(i, j).text = str(cell)
        else:
            # Fallback: convert to string
            doc.add_paragraph(str(content))

        doc.save(path)
        return str(path)
    
    def _is_markdown_content(self, content: str) -> bool:
        """Check if content looks like markdown."""
        # Simple heuristics to detect markdown
        markdown_indicators = [
            content.startswith('#'),
            '##' in content,
            '###' in content,
            '- ' in content,
            '* ' in content,
            '|' in content and '|' in content.split('\n')[0] if '\n' in content else False,
            '**' in content,
            '`' in content
        ]
        return any(markdown_indicators)
    
    def _save_markdown_as_docx(self, markdown_content: str, path: Path, **kwargs) -> str:
        """Save markdown content as DOCX using template system."""
        try:
            from ..templates import DocxTemplateManager, MarkdownToDocxConverter, StyleMapper
            
            # Initialize template system
            template_manager = DocxTemplateManager(self.config)
            style_mapper = StyleMapper()
            converter = MarkdownToDocxConverter(template_manager, style_mapper)
            
            # Get conversion options
            template_name = kwargs.get("template")
            add_provenance = kwargs.get("add_provenance", True)
            add_reviewer_instructions = kwargs.get("add_reviewer_instructions", False)
            source_file = kwargs.get("source_file")
            
            # Convert markdown to DOCX
            doc = converter.convert_markdown_to_docx(
                markdown_content=markdown_content,
                template_name=template_name,
                add_provenance=add_provenance,
                add_reviewer_instructions=add_reviewer_instructions,
                source_file=source_file
            )
            
            # Save document
            doc.save(path)
            return str(path)
            
        except ImportError as e:
            # Fallback to simple conversion if template system not available
            self.logger.warning(f"Template system not available, using simple conversion: {e}")
            doc = Document()
            doc.add_paragraph(markdown_content)
            doc.save(path)
            return str(path)
        except Exception as e:
            raise StorageOperationError(f"Failed to convert markdown to DOCX: {e}") from e
    
    def _save_with_template(self, content: Union[str, Dict[str, Any]], path: Path, template_name: str, **kwargs) -> str:
        """Save content using a specific template."""
        try:
            from docx import Document
            from ..templates import DocxTemplateManager
            
            template_manager = DocxTemplateManager(self.config)
            template_path = template_manager.get_template_path(template_name)
            
            if template_path and template_path.exists():
                # Load template
                doc = Document(template_path)
                
                # Clear template content
                self._clear_template_content(doc)
                
                # Add content
                if isinstance(content, str):
                    doc.add_paragraph(content)
                elif isinstance(content, dict):
                    if "title" in content:
                        doc.add_heading(content["title"], 0)
                    if "sections" in content:
                        for section in content["sections"]:
                            if "heading" in section:
                                doc.add_heading(section["heading"], level=section.get("level", 1))
                            if "text" in section:
                                doc.add_paragraph(section["text"])
                            if "table" in section and isinstance(section["table"], list):
                                table = doc.add_table(rows=len(section["table"]), cols=len(section["table"][0]))
                                for i, row in enumerate(section["table"]):
                                    for j, cell in enumerate(row):
                                        table.cell(i, j).text = str(cell)
                
                doc.save(path)
                return str(path)
            else:
                # Fallback to default if template not found
                self.logger.warning(f"Template '{template_name}' not found, using default")
                return self._save_docx(content, path, **{k: v for k, v in kwargs.items() if k != 'template'})
                
        except Exception as e:
            raise StorageOperationError(f"Failed to save with template '{template_name}': {e}") from e
    
    def _clear_template_content(self, doc):
        """Clear template content while preserving styles, headers, and footers."""
        # Remove all paragraphs from main document body only
        while len(doc.paragraphs) > 0:
            p = doc.paragraphs[0]._element
            p.getparent().remove(p)
        
        # Remove all tables from main document body only
        while len(doc.tables) > 0:
            t = doc.tables[0]._element
            t.getparent().remove(t)
        
        # Clear document body while preserving headers/footers
        try:
            body = doc._body
            for element in list(body):
                if element.tag.endswith('p') or element.tag.endswith('tbl'):
                    body.remove(element)
        except Exception:
            pass
        
        # Note: Headers and footers are preserved automatically by python-docx
        # They are stored separately from the main document body

    def _load_docx(self, path: Path, **kwargs) -> str:
        """Load DOCX file and extract text content."""
        try:
            from docx import Document
        except ImportError:
            raise StorageOperationError(
                "python-docx not installed. Install with: pip install 'FileUtils[documents]'"
            )

        doc = Document(path)
        text_content = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)
        
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text_content.append(" | ".join(row_text))
        
        return "\n".join(text_content)

    def _save_markdown(self, content: Union[str, Dict[str, Any]], path: Path, **kwargs) -> str:
        """Save content to Markdown format."""
        if isinstance(content, str):
            markdown_content = content
        elif isinstance(content, dict):
            # Handle structured content with YAML frontmatter
            frontmatter = content.get("frontmatter", {})
            body = content.get("body", "")
            
            if frontmatter:
                import yaml
                frontmatter_yaml = yaml.safe_dump(frontmatter, default_flow_style=False)
                markdown_content = f"---\n{frontmatter_yaml}---\n\n{body}"
            else:
                markdown_content = body
        else:
            markdown_content = str(content)

        with open(path, "w", encoding=self.config["encoding"]) as f:
            f.write(markdown_content)
        
        return str(path)

    def _load_markdown(self, path: Path, **kwargs) -> Union[str, Dict[str, Any]]:
        """Load Markdown file with optional YAML frontmatter."""
        with open(path, "r", encoding=self.config["encoding"]) as f:
            content = f.read()
        
        # Check for YAML frontmatter
        if content.startswith("---\n"):
            try:
                import yaml
                parts = content.split("---\n", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    return {
                        "frontmatter": frontmatter or {},
                        "body": body
                    }
            except Exception:
                # If frontmatter parsing fails, return as plain text
                pass
        
        return content

    def _save_pdf(self, content: Union[str, Dict[str, Any]], path: Path, **kwargs) -> str:
        """Save content to PDF format using PyMuPDF."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise StorageOperationError(
                "PyMuPDF not installed. Install with: pip install 'FileUtils[documents]'"
            )

        doc = fitz.open()  # Create new PDF
        page = doc.new_page()
        
        if isinstance(content, str):
            # Simple text content
            page.insert_text((50, 50), content, fontsize=12)
        elif isinstance(content, dict):
            # Structured content
            y_position = 50
            if "title" in content:
                page.insert_text((50, y_position), content["title"], fontsize=16)
                y_position += 30
            
            if "sections" in content:
                for section in content["sections"]:
                    if "heading" in section:
                        page.insert_text((50, y_position), section["heading"], fontsize=14)
                        y_position += 25
                    if "text" in section:
                        page.insert_text((50, y_position), section["text"], fontsize=12)
                        y_position += 20
        else:
            # Fallback: convert to string
            page.insert_text((50, 50), str(content), fontsize=12)

        doc.save(path)
        doc.close()
        return str(path)

    def _load_pdf(self, path: Path, **kwargs) -> str:
        """Load PDF file and extract text content."""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise StorageOperationError(
                "PyMuPDF not installed. Install with: pip install 'FileUtils[documents]'"
            )

        doc = fitz.open(path)
        text_content = []
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_content.append(text)
        
        doc.close()
        return "\n\n".join(text_content)

    def _load_json(self, path: Path, **kwargs) -> Dict[str, Any]:
        """Load JSON file."""
        try:
            import json
            
            with open(path, "r", encoding=self.config["encoding"]) as f:
                return json.load(f, **kwargs)
        except Exception as e:
            raise StorageOperationError(f"Failed to load JSON file: {e}") from e

    def _load_yaml(self, path: Path, **kwargs) -> Dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml
            
            with open(path, "r", encoding=self.config["encoding"]) as f:
                return yaml.safe_load(f, **kwargs)
        except Exception as e:
            raise StorageOperationError(f"Failed to load YAML file: {e}") from e

    def _save_json(self, content: Union[str, Dict[str, Any]], path: Path, **kwargs) -> str:
        """Save content as JSON file."""
        try:
            import json
            
            # Custom JSON encoder to handle pandas types
            class PandasJSONEncoder(json.JSONEncoder):
                def default(self, obj):
                    if hasattr(obj, 'isoformat'):  # datetime, Timestamp
                        return obj.isoformat()
                    elif hasattr(obj, 'tolist'):  # numpy arrays (check this first)
                        return obj.tolist()
                    elif hasattr(obj, 'item'):  # numpy scalar types
                        return obj.item()
                    return super().default(obj)
            
            with open(path, "w", encoding=self.config["encoding"]) as f:
                json.dump(content, f, indent=kwargs.get("indent", 2), cls=PandasJSONEncoder, **kwargs)
            return str(path)
        except Exception as e:
            raise StorageOperationError(f"Failed to save JSON file: {e}") from e

    def _save_yaml(self, content: Union[str, Dict[str, Any]], path: Path, **kwargs) -> str:
        """Save content as YAML file."""
        try:
            import yaml
            
            with open(path, "w", encoding=self.config["encoding"]) as f:
                yaml.dump(content, f, default_flow_style=False, **kwargs)
            return str(path)
        except Exception as e:
            raise StorageOperationError(f"Failed to save YAML file: {e}") from e
