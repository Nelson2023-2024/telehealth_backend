# Base image: Python 3.13 on Debian "Trixie", slim variant (minimal OS extras, smaller image)
FROM python:3.13.12-slim-trixie

# Don’t create .pyc files -> .pyc files are compiled versions of Python files. Inside Docker, they’re usually unnecessary.
ENV PYTHONDONTWRITEBYTECODE=1

# print output immediately -> Without this, logs may not show instantly in Docker logs. Very useful for debugging.
ENV PYTHONUNBUFFERED=1

# All future commands will run inside the /usr/src/app folder.
WORKDIR /app

# curl is only needed if you want to add a HEALTHCHECK later or debug network calls from inside the container.
# Single RUN line so "update" and "install" are always cached/invalidated together, then clean apt's package
# index afterwards so it doesn't bloat the image.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

    # . -> /app -> ./
COPY requirements.txt .

# . -> /app -> ./
# -> built time: install/upgrade pip, then install dependencies.
# --no-cache-dir stops pip from keeping downloaded package files on disk, keeping the image smaller.
RUN pip install --upgrade pip --no-cache-dir \
    && pip install -r requirements.txt --no-cache-dir


# host -> container: copy the rest of the project code last, since it changes far more often
# than dependencies, so this doesn't bust the pip-install cache layer above.
COPY . .

# Create a non-root user and switch to it. Running as root inside the container is a security risk
# (if the app is ever compromised, an attacker has root inside the container, not just app-level access).
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# -> runtime
# 0.0.0.0 - means  server inside the container will accept connections on all network interfaces with in the container
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]