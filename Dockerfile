FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README-PYPI.md ./
RUN pip install -e .
COPY src ./src
LABEL version="0.1.4" description="Precision testing tool for AI agents"
ENTRYPOINT ["assay"]
