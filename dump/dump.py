from typing import Union

import logging
import math
from pathlib import Path

import dropbox


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_dropbox(auth_token: str) -> dropbox.Dropbox:
    return dropbox.Dropbox(auth_token)


CHUNK_SIZE = 149 * 1024 * 1024  # really 150, but lowball it a little


def upload_file(dbx: dropbox.Dropbox, path: Union[str, bytes]):
    path = Path(path)

    if path.stat().st_size < CHUNK_SIZE:
        _upload_small_file(dbx, path)
    else:
        _upload_large_file(dbx, path)


def _upload_small_file(dbx: dropbox.Dropbox, path: Path):
    dbx.files_upload(f=path.read_bytes(), path=_upload_path(path))
    logger.debug(f"Uploaded {path}")


def _upload_large_file(dbx: dropbox.Dropbox, path: Path):
    file_size = path.stat().st_size
    num_chunks = math.ceil(file_size / CHUNK_SIZE)
    curr_chunk = 0
    with path.open(mode="rb") as f:
        upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
        curr_chunk += 1
        logger.debug(f"Uploaded chunk {curr_chunk}/{num_chunks} of {path}")
        cursor = dropbox.files.UploadSessionCursor(
            session_id=upload_session_start_result.session_id, offset=f.tell()
        )
        commit = dropbox.files.CommitInfo(path=_upload_path(path))

        while f.tell() < file_size:
            if (file_size - f.tell()) <= CHUNK_SIZE:
                dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
            else:
                dbx.files_upload_session_append_v2(f.read(CHUNK_SIZE), cursor)
                cursor.offset = f.tell()
            curr_chunk += 1
            logger.debug(f"Uploaded chunk {curr_chunk}/{num_chunks} of {path}")


def _upload_path(path: Path) -> str:
    return fr"/{path.name}"
