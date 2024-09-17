# Use an official Python runtime as the base image
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8501 for Streamlit
EXPOSE 8501

# Run Streamlit when the container launches
CMD ["streamlit", "run", "streamlit_app.py", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
