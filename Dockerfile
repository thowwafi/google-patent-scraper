FROM python:3.9-slim

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your scraper code
COPY . .

# Run the scraper
CMD ["python", "patent_scraper.py"]