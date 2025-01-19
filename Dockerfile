# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.13-slim-bookworm AS builder

WORKDIR /app 
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     git \
#     ca-certificates \
#     python3-cairosvg \
#     && rm -rf /var/lib/apt/lists/* \
#     && apt-get clean


# Install pip requirements
COPY requirements-docker.txt requirements.txt
RUN python -m pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt && rm -rf /root/.cache/pip

FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
     libcairo2 \
     && rm -rf /var/lib/apt/lists/* \
     && apt-get clean

WORKDIR /app
COPY . /app
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN python -m pip install --no-cache /wheels/*
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 8888
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "src/main.py", "--emulated"]
