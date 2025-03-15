from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import routers.base


# Create the FastAPI instance
app = FastAPI()


class CacheControlStaticFiles(StaticFiles):
    def __init__(self, *args, **kwargs):
        self.cache_timeout = kwargs.pop("cache_timeout", 3600)
        super().__init__(*args, **kwargs)

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = f"public, max-age={self.cache_timeout}"
        return response


app.mount(
    "/static",
    CacheControlStaticFiles(directory="static", cache_timeout=300),
    name="static",
)

templates = Jinja2Templates(directory="templates")


app.include_router(routers.base.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
