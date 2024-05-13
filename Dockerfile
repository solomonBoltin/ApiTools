# Use a slim Python 3 base image
FROM python:3.9-slim-buster

ENV HOST 0.0.0.0

# Install poppler-utils for PDF processing
RUN apt-get update && apt-get install -y poppler-utils

# Set working directory for your application
WORKDIR /app

# Copy your application code and requirements.txt
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the port your Flask app runs on (default: 5000)
EXPOSE 8080

# Define the command to run your Flask app
CMD ["python", "src/api.py"]

# Build the Docker image  

