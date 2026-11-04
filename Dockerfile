FROM python:3.11-slim

WORKDIR /app

COPY . .

# A plain `.` install is the whole image: since 2026-11-01 Pillow (for the
# colour-vision simulation), fastapi and uvicorn (for the CMD below) and
# fastapi-mcp are base dependencies, so there is no extra to ask for.
RUN pip install --no-cache-dir "."

EXPOSE 8000

# Serve what the image was built for. A CMD of `--help` is a container that
# starts, prints and exits — which looks like it works and does nothing.
#
# The MCP server, not bare uvicorn on `api:app`: `sprezzature-colors-mcp`
# mounts the MCP endpoint on the same FastAPI app as the HTTP routes, so one
# container on one port answers both `/v1/...` and `/mcp`. Running uvicorn on
# `api:app` served the routes only, because nothing imported the module that
# mounts `/mcp`.
#
# Override with any of the command lines:
#
#   docker run --rm -v "$PWD:/work" IMAGE sprezzature-colors-cvd /work/hero.png
CMD ["sprezzature-colors-mcp", "--host", "0.0.0.0", "--port", "8000"]
