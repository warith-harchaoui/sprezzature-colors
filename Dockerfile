FROM python:3.11-slim

WORKDIR /app

COPY . .

# `cvd` carries Pillow, which the colour-vision simulation needs to open a
# screenshot; `api` and `mcp` carry fastapi and uvicorn, which live behind an
# extra so that nobody installing the library pays for a web server. An image
# that serves has to ask for all three — the previous `.[cvd]` build could not
# run the command its own CMD named.
RUN pip install --no-cache-dir ".[cvd,api,mcp]"

EXPOSE 8000

# Serve what the image was built for. A CMD of `--help` is a container that
# starts, prints and exits — which looks like it works and does nothing.
# Override with any of the command lines:
#
#   docker run --rm -v "$PWD:/work" IMAGE sprezzature-colors-cvd /work/hero.png
CMD ["uvicorn", "sprezzature_colors.api:app", "--host", "0.0.0.0", "--port", "8000"]
