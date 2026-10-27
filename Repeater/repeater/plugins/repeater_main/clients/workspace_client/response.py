from pydantic import BaseModel

class FileInfo(BaseModel):
    size: int
    st_mtime: float
    st_mtime_ns: int
    st_atime: float
    st_atime_ns: int
    st_mode: str

class DeleteResult(BaseModel):
    deleted_files: int
    deleted_dirs: int

class MoveResult(BaseModel):
    source: str
    destination: str

class CopyResult(MoveResult):
    copied_files: int
    copied_dirs: int
