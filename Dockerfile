FROM node:20 as node

WORKDIR /app

COPY package.json package-lock.json tailwind.config.js ./
RUN npm i

COPY static/input.css ./static/input.css
COPY templates/audit.html ./templates/audit.html
RUN npm run tw

FROM python:3.11

WORKDIR /app
COPY --from=node /app/static/output.css ./static/output.css

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install

COPY main.py ./
COPY static/input.css ./static/input.css
COPY templates ./templates

CMD poetry run uvicorn main:app --host 0.0.0.0 --port 8000
