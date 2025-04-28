from pathlib import Path
from typing import Optional, List, BinaryIO
import shutil
from src.app.configs.app_config import AppConfig
from src.app.configs.disk_config import DiskConfig

class AppDisk:
    """
    AppDisk
    """
    @classmethod
    def config (cls) -> DiskConfig:
        """
        Args:
            cls
        Returns:
            DiskConfig
        """
        return DiskConfig.config ()

    @classmethod
    def diskPath (cls) -> Path:
        """
        Args:
            cls
        Returns:
            Path
        """
        config = cls.config ()
        path = Path (config.disk_path)
        path.mkdir (parents=True, exist_ok=True)
        return path

    @classmethod
    def publicPath (cls) -> Path:
        """
        Args:
            cls
        Returns:
            Path
        """
        config = cls.config ()
        path = Path (config.disk_public_path)
        path.mkdir (parents=True, exist_ok=True)
        return path

    @classmethod
    def privatePath (cls) -> Path:
        """
        Args:
            cls
        Returns:
            Path
        """
        config = cls.config ()
        path = Path (config.disk_private_path)
        path.mkdir (parents=True, exist_ok=True)
        return path

    @classmethod
    def put (cls, path: str, content: bytes | BinaryIO, disk: str = "public") -> bool:
        """
        Args:
            path (str)
            content (bytes | BinaryIO)
            disk (str)
        Returns:
            bool
        """
        try:
            if disk == "public":
                basePath = cls.publicPath ()
            elif disk == "private":
                basePath = cls.privatePath ()
            else:
                basePath = cls.diskPath ()
            filePath = basePath / path
            filePath.parent.mkdir (parents=True, exist_ok=True)
            if isinstance (content, bytes):
                filePath.write_bytes (content)
            else:
                with open (filePath, "wb") as f:
                    shutil.copyfileobj (content, f)
            return True
        except Exception as e:
            print (f"[AppDisk.put] Error putting file: {e}")
            import traceback
            traceback.print_exc ()
            return False

    @classmethod
    def get (cls, path: str, disk: str = "public") -> Optional[bytes]:
        """
        Args:
            path (str)
            disk (str)
        Returns:
            Optional[bytes]
        """
        try:
            if disk == "public":
                basePath = cls.publicPath ()
            elif disk == "private":
                basePath = cls.privatePath ()
            else:
                basePath = cls.diskPath ()
            filePath = basePath / path
            if filePath.exists () and filePath.is_file ():
                return filePath.read_bytes ()
            return None
        except Exception as e:
            print (f"Error getting file: {e}")
            return None

    @classmethod
    def exists (cls, path: str, disk: str = "public") -> bool:
        """
        Args:
            path (str)
            disk (str)
        Returns:
            bool
        """
        try:
            if disk == "public":
                basePath = cls.publicPath ()
            elif disk == "private":
                basePath = cls.privatePath ()
            else:
                basePath = cls.diskPath ()
            filePath = basePath / path
            return filePath.exists () and filePath.is_file ()
        except Exception:
            return False

    @classmethod
    def delete (cls, path: str, disk: str = "public") -> bool:
        """
        Args:
            path (str)
            disk (str)
        Returns:
            bool
        """
        try:
            if disk == "public":
                basePath = cls.publicPath ()
            elif disk == "private":
                basePath = cls.privatePath ()
            else:
                basePath = cls.diskPath ()
            filePath = basePath / path
            if filePath.exists () and filePath.is_file ():
                filePath.unlink ()
                return True
            return False
        except Exception as e:
            print (f"Error deleting file: {e}")
            return False

    @classmethod
    def url (cls, path: str, disk: str = "public") -> Optional[str]:
        """
        Args:
            path (str)
            disk (str)
        Returns:
            Optional[str]
        """
        try:
            if disk == "public":
                basePath = cls.publicPath ()
            elif disk == "private":
                basePath = cls.privatePath ()
            else:
                return None

            filePath = basePath / path
            if filePath.exists () and filePath.is_file ():
                diskConfig = cls.config ()
                return f"{diskConfig.public_url ()}/{path}" if disk == "public" else None
            return None
        except Exception:
            return None

    @classmethod
    def path (cls, path: str, disk: str = "public") -> Optional[Path]:
        """
        Args:
            path (str)
            disk (str)
        Returns:
            Optional[Path]
        """
        try:
            if disk == "public":
                basePath = cls.publicPath ()
            elif disk == "private":
                basePath = cls.privatePath ()
            else:
                basePath = cls.diskPath ()
            filePath = basePath / path
            if filePath.exists ():
                return filePath
            return None
        except Exception:
            return None

    @classmethod
    def size (cls, path: str, disk: str = "public") -> Optional[int]:
        """
        Args:
            path (str)
            disk (str)
        Returns:
            Optional[int]
        """
        try:
            if disk == "public":
                basePath = cls.publicPath ()
            elif disk == "private":
                basePath = cls.privatePath ()
            else:
                basePath = cls.diskPath ()
            filePath = basePath / path
            if filePath.exists () and filePath.is_file ():
                return filePath.stat ().st_size
            return None
        except Exception:
            return None

    @classmethod
    def copy (cls, fromPath: str, toPath: str, fromDisk: str = "public", toDisk: str = "public") -> bool:
        """
        Args:
            fromPath (str)
            toPath (str)
            fromDisk (str)
            toDisk (str)
        Returns:
            bool
        """
        try:
            content = cls.get (fromPath, fromDisk)
            if content is None:
                return False
            return cls.put (toPath, content, toDisk)
        except Exception as e:
            print (f"Error copying file: {e}")
            return False

    @classmethod
    def move (cls, fromPath: str, toPath: str, fromDisk: str = "public", toDisk: str = "public") -> bool:
        """
        Args:
            fromPath (str)
            toPath (str)
            fromDisk (str)
            toDisk (str)
        Returns:
            bool
        """
        try:
            if fromDisk == toDisk:
                if fromDisk == "public":
                    basePath = cls.publicPath ()
                elif fromDisk == "private":
                    basePath = cls.privatePath ()
                else:
                    basePath = cls.diskPath ()
                fromFilePath = basePath / fromPath
                toFilePath = basePath / toPath
                if fromFilePath.exists () and fromFilePath.is_file ():
                    toFilePath.parent.mkdir (parents=True, exist_ok=True)
                    fromFilePath.rename (toFilePath)
                    return True
            else:
                if cls.copy (fromPath, toPath, fromDisk, toDisk):
                    return cls.delete (fromPath, fromDisk)
            return False
        except Exception as e:
            print (f"Error moving file: {e}")
            return False
