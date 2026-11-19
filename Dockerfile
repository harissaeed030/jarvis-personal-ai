# Optional sidecar: build the official Stanford OpenJarvis runtime without copying or modifying its upstream repository.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPENJARVIS_HOME=/tmp/openjarvis

RUN apt-get update && apt-get install -y --no-install-recommends git build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

WORKDIR /opt/openjarvis
RUN git clone --depth 1 https://github.com/open-jarvis/OpenJarvis.git . \
    && uv pip install --system ".[server,inference-google]"

EXPOSE 10000
ENTRYPOINT ["jarvis"]
CMD ["serve", "--host", "0.0.0.0", "--port", "10000", "--engine", "cloud", "--model", "gemini-2.5-flash-lite", "--agent", "orchestrator"]
