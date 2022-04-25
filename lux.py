import os, sys, subprocess

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.templating import Jinja2Templates
from starlette.background import BackgroundTask

import uvicorn
from collections import ChainMap

templates = Jinja2Templates(directory="")

app_defaults = {
    "SERVER_HOST": "0.0.0.0",
    "SERVER_PORT": 8080,
}


async def dl_queue_list(request):
    return templates.TemplateResponse("index.html", {"request": request})


async def q_put(request):
    form = await request.form()
    url = form.get("url").strip()
    options = {"format": form.get("format")}

    if not url:
        return JSONResponse(
            {"success": False, "error": "/q called without a 'url' in form data"}
        )

    task = BackgroundTask(download, url)

    print("Added url " + url + " to the download queue")
    return JSONResponse(
        {"success": True, "url": url, "options": options}, background=task
    )


async def update_route(scope, receive, send):
    task = BackgroundTask(update)

    return JSONResponse({"output": "Initiated package update"}, background=task)


def update():
    try:
        output = subprocess.check_output(
            ["go", "install", "github.com/iawia002/lux@latest"]
        )

        print(output.decode("ascii"))
    except subprocess.CalledProcessError as e:
        print(e.output)


def download(url):
    os.system('lux -o /downloads ' + url)


routes = [
    Route("/lux", endpoint=dl_queue_list),
    Route("/lux/q", endpoint=q_put, methods=["POST"]),
    Route("/lux/update", endpoint=update_route, methods=["PUT"]),
    Mount("/lux/static", app=StaticFiles(directory="static"), name="static"),
]

app = Starlette(debug=True, routes=routes)

print("Updating lux to the newest version")
update()

app_vars = ChainMap(os.environ, app_defaults)

if __name__ == "__main__":
    uvicorn.run(
        app, host=app_vars["SERVER_HOST"], port=int(app_vars["SERVER_PORT"])
    )
