FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
  g++ \
  libgl1 \
  libglib2.0-0 \
  poppler-utils \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
  && pip install --no-cache-dir spacy[cuda12x] \
  && python -m spacy download en_core_web_sm

CMD ["flask", "run", "--host=0.0.0.0", "--debug"]
