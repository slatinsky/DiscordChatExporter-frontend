import functools
import os
import sys
from fastapi import FastAPI

from .status import get_status
from .guilds import get_guilds
from .channels import get_channels
from .roles import get_roles
from .search import get_searchcategories
from .search import search
from .search import get_autocomplete
from .messages import get_messages

# fix PIPE encoding error on Windows, auto flush print
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

app = FastAPI(
	title="DCEF backend api",
	description="This is the backend api for the DCEF viewer.",
	version="0.2.0",
	root_path="/api"
)


app.include_router(get_status.router)
app.include_router(get_guilds.router)
app.include_router(get_channels.router)
app.include_router(get_roles.router)
app.include_router(get_searchcategories.router)
app.include_router(search.router)
app.include_router(get_autocomplete.router)

app.include_router(get_messages.router)








