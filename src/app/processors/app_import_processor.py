from pathlib import Path
from typing import Dict, List
import io
import pandas as pd
from src.app.bases.app_i18n import AppI18n

class AppImportProcessor:
    """
    AppImportProcessor
    """
    def __init__ (self) -> None:
        """
        Returns:
        """
        pass

    @staticmethod
    def import_file (file_content: bytes, filename: str) -> List[Dict[str, object]]:
        """
        Args:
            file_content (bytes)
            filename (str)
        Returns:
            List[Dict[str, object]]
        """
        i18n = AppI18n.i18n ()
        file_extension = Path (filename).suffix.lower ()

        if file_extension == ".csv":
            content = file_content.decode ("utf-8") if isinstance (file_content, bytes) else file_content
            df = pd.read_csv (io.StringIO (content))
        elif file_extension in [".xlsx", ".xls"]:
            content = io.BytesIO (file_content) if isinstance (file_content, bytes) else file_content
            df = pd.read_excel (content)
        else:
            raise ValueError (i18n.t ("_app.processor.import.unsupported_format", args={"format": file_extension}))

        if df.empty:
            raise ValueError (i18n.t ("_app.processor.import.empty_file"))

        return df.to_dict (orient="records")

    @staticmethod
    def validate_columns (data: List[Dict[str, object]], required_columns: List[str]) -> None:
        """
        Args:
            data (List[Dict[str, object]])
            required_columns (List[str])
        Returns:
            None
        """
        i18n = AppI18n.i18n ()
        if not data:
            raise ValueError (i18n.t ("_app.processor.import.no_data"))

        first_row = data[0]
        missing_columns = [col for col in required_columns if col not in first_row]

        if missing_columns:
            raise ValueError (i18n.t ("_app.processor.import.missing_columns", args={"columns": ', '.join (missing_columns)}))

    @staticmethod
    def filter_valid_rows (data: List[Dict[str, object]], required_fields: List[str]) -> List[Dict[str, object]]:
        """
        Args:
            data (List[Dict[str, object]])
            required_fields (List[str])
        Returns:
            List[Dict[str, object]]
        """
        valid_rows = []

        for row in data:
            is_valid = True
            for field in required_fields:
                value = row.get (field)
                if value is None or (isinstance (value, str) and not value.strip ()) or pd.isna (value):
                    is_valid = False
                    break

            if is_valid:
                cleaned_row = {}
                for key, value in row.items ():
                    if isinstance (value, str):
                        cleaned_row[key] = value.strip ()
                    else:
                        cleaned_row[key] = value
                valid_rows.append (cleaned_row)

        return valid_rows
