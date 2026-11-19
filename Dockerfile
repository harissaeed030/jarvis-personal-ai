# Optional sidecar: reproducibly build the official Stanford OpenJarvis runtime.
# Pin the upstream source so a future upstream change cannot silently break deployment.
FROM python:3.12-slim

ARG OPENJARVIS_REF=c3ed63f1d2a2c0c1f7dabbc69050e1968a11dc10
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPENJARVIS_HOME=/tmp/openjarvis \
    PATH="/root/.cargo/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends git curl build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal \
    && pip install --no-cache-dir uv

WORKDIR /opt/openjarvis
RUN git init . \
    && git remote add origin https://github.com/open-jarvis/OpenJarvis.git \
    && git fetch --depth 1 origin "${OPENJARVIS_REF}" \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = "${OPENJARVIS_REF}" \
    && uv pip install --system ".[server,inference-google]"

EXPOSE 10000
ENTRYPOINT ["jarvis"]
CMD ["serve", "--host", "0.0.0.0", "--port", "10000", "--engine", "cloud", "--model", "gemini-2.5-flash", "--agent", "orchestrator"]
