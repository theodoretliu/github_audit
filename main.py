import os
from typing import Union

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import pathspec
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.add_middleware(GZipMiddleware, minimum_size=1000)

spec = None


def f():
    allowed_filenames = [
        x.decode("utf-8")
        for x in subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd="../code",
        ).splitlines()
    ]

    return set(allowed_filenames)


allow_set = f()

def is_ignored(path):
    rel_path = os.path.relpath(path, "../code")

    return rel_path not in allow_set


def all_files_in_directory(directory):
    directories = []
    files = []
    for entry in os.scandir(directory):
        if entry.is_dir():
            directories.append(entry.path)
        elif entry.is_file():
            files.append(entry.path)

    directories = sorted(directories)

    for d in directories:
        yield from all_files_in_directory(d)

    for f in files:
        yield f


def all_non_ignored_paths_in_directory(directory):
    for path in all_files_in_directory(directory):
        if not is_ignored(path):
            yield path


@app.get("/")
@app.get("/{subdirectory:path}", response_class=HTMLResponse)
def audit(request: Request, subdirectory: str = ""):
    # exec git ls-files in a shell and get the response
    filenames = list(all_non_ignored_paths_in_directory(os.path.join("../code", subdirectory)))

    files = []

    for filename in filenames:
        with open(filename, "r") as f:
            try:
                contents = f.readlines()
            except UnicodeDecodeError:
                contents = ['Binary content']

        trimmed_contents = [x.rstrip() for x in contents]

        final_contents = [x if len(x) > 0 else " " for x in trimmed_contents]

        files.append({"name": filename[8:], "contents": '\n'.join(final_contents)})

    return templates.TemplateResponse(
        request=request, name="audit.html", context={"files": files}
    )
