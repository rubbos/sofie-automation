# Use Python slim image
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    git \
    unzip \
    poppler-utils \
    tesseract-ocr=5.3.0-2 \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*  

# Install Node.js 22.x and necessary dependencies
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to /app
WORKDIR /app

# Copy node setup
COPY package*.json ./
RUN npm install

# Copy Tailwind/PostCSS configs and source CSS
COPY tailwind.config.js postcss.config.js ./
COPY app/static/css ./app/static/css/

# Build Tailwind output
RUN npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/output.css --minify

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the Flask app port
EXPOSE 5000

# Start Flask server
CMD ["flask", "run", "--host=0.0.0.0", "--debug"]
