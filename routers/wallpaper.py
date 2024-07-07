from fastapi import APIRouter
import os
import random
import mimetypes
from starlette.responses import StreamingResponse

router = APIRouter()

wallPaperDir = "wallpaper"


@router.get("/wallpaper", tags=["wallpaper"])
async def get_wallpaper():
    files = os.listdir(wallPaperDir)
    selected_file = random.choice(files)
    file_path = os.path.join(wallPaperDir, selected_file)
    contentType, _ = mimetypes.guess_type(file_path)
    if contentType is None:
        contentType = "application/octet-stream"

    disposition = "inline"

    headers = {
        "Content-Disposition": f"{disposition}; filename=\"{selected_file}\"",
        "Content-Type": contentType
    }

    def iterfile():
        with open(file_path, mode="rb") as file:
            yield from file

    return StreamingResponse(iterfile(), headers=headers)
