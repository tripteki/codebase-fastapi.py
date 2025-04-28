from pathlib import Path
from typing import Dict, List, Literal, Optional
import io
import pandas as pd
from src.app.bases.app_i18n import AppI18n
from src.app.configs.disk_config import DiskConfig

class AppExportProcessor:
    """
    AppExportProcessor
    """
    def __init__ (self) -> None:
        """
        Returns:
        """
        pass

    @staticmethod
    def export_file (
        data: List[Dict[str, object]],
        filename: str,
        file_type: Literal["csv", "xlsx", "xls"] = "csv",
        subfolder: str = "export",
        sheet_name: str = "Sheet1"
    ) -> Dict[str, str]:
        """
        Args:
            data (List[Dict[str, object]])
            filename (str)
            file_type (Literal["csv", "xlsx", "xls"])
            subfolder (str)
            sheet_name (str)
        Returns:
            Dict[str, str]
        """
        i18n = AppI18n.i18n ()

        if not data:
            raise ValueError (i18n.t ("_app.processor.export.no_data"))

        disk_config = DiskConfig.config ()
        public_storage_path = Path (disk_config.disk_public_path)
        export_path = public_storage_path / subfolder

        export_path.mkdir (parents=True, exist_ok=True)

        file_path = export_path / filename

        df = pd.DataFrame (data)

        if file_type == "csv":
            df.to_csv (file_path, index=False, encoding="utf-8")
        elif file_type in ["xlsx", "xls"]:
            with pd.ExcelWriter (file_path, engine="openpyxl" if file_type == "xlsx" else "xlwt") as writer:
                df.to_excel (writer, sheet_name=sheet_name, index=False)
        else:
            raise ValueError (i18n.t ("_app.processor.export.unsupported_type", args={"type": file_type}))

        file_url = f"storage/{subfolder}/{filename}"

        return {
            "filePath": str (file_path),
            "fileUrl": file_url
        }

    @staticmethod
    def prepare_data (data: List[Dict[str, object]], columns: Optional[List[str]] = None) -> List[Dict[str, object]]:
        """
        Args:
            data (List[Dict[str, object]])
            columns (Optional[List[str]])
        Returns:
            List[Dict[str, object]]
        """
        if not data:
            return []

        if columns:
            return [
                {col: row.get (col) for col in columns}
                for row in data
            ]

        return data

    @staticmethod
    def sanitize_data (data: List[Dict[str, object]]) -> List[Dict[str, object]]:
        """
        Args:
            data (List[Dict[str, object]])
        Returns:
            List[Dict[str, object]]
        """
        sanitized = []

        for row in data:
            sanitized_row = {}
            for key, value in row.items ():
                if value is None:
                    sanitized_row[key] = ""
                elif isinstance (value, (list, dict)):
                    sanitized_row[key] = str (value)
                else:
                    sanitized_row[key] = value
            sanitized.append (sanitized_row)

        return sanitized
