# FileUtils TODO List

notes:
   - check input and output handling (processed, raw, etc.)


1. Add type hinting
   - Implement throughout the code for improved readability and maintainability
   - Example: def load_single_file(self, file_path: Union[str, Path]) -> pd.DataFrame:

2. Enhance error handling
   - Create custom exceptions for specific error cases
   - Implement try-except blocks in all methods
   - Example: class FileUtilsError(Exception): pass

3. Support additional file formats
   - Add methods for JSON, Parquet, and HDF5 files
   - Example: def load_json(self, file_path: Path) -> Dict:

4. Implement dependency checking
   - Create a method to check for required libraries
   - Run at initialization
   - Example: def check_dependencies(self) -> None:

5. Flexible directory structure management
   - Allow custom directory structures in config file
   - Update ensure_directories method to use custom structure
   - Example: directory_structure: {data: [raw, processed], models: []}

6. Add data validation and schema checking
   - Implement optional validation when loading data
   - Example: def validate_dataframe(self, df: pd.DataFrame, schema: Dict) -> bool:

7. Create data preprocessing methods
   - Add methods for common preprocessing tasks
   - Example: def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:

8. Implement data versioning support
   - Integrate with DVC or create a simple versioning system
   - Example: def save_data_version(self, data: pd.DataFrame, version: str) -> None:

9. Enhance configuration system
   - Add validation for required config fields
   - Provide clear error messages for invalid configs
   - Example: def validate_config(self, config: Dict) -> None:

10. Develop comprehensive test suite
    - Write unit tests for all public methods
    - Create integration tests for common scenarios
    - Example: def test_load_single_file(self):

11. Improve docstrings
    - Add comprehensive docstrings to all methods
    - Include parameter descriptions and return types
    - Example:
      ```python
      def load_single_file(self, file_path: Union[str, Path]) -> pd.DataFrame:
          """
          Load a single file based on its extension.

          Args:
              file_path (Union[str, Path]): Path to the file to be loaded.

          Returns:
              pd.DataFrame: Loaded data as a pandas DataFrame.

          Raises:
              FileUtilsError: If the file format is unsupported or the file cannot be loaded.
          """
      ```

12. Refactor save_data_to_disk method
    - Split into smaller, format-specific methods
    - Example: def save_csv(self, df: pd.DataFrame, file_path: Path) -> None:

13. Enhance load_data_from_metadata method
    - Add option to load specific datasets from metadata
    - Example: def load_data_from_metadata(self, metadata_file: Path, datasets: List[str] = None) -> Dict[str, pd.DataFrame]:

14. Implement chunked reading/writing
    - Add options for handling large datasets
    - Example: def load_csv_chunked(self, file_path: Path, chunksize: int = 10000) -> Iterator[pd.DataFrame]:

15. Create method for file format detection
    - Implement a method to automatically detect file format
    - Example: def detect_file_format(self, file_path: Path) -> str:

Remember to update the README.md file after implementing these changes to reflect the new features and improvements in the FileUtils class.
