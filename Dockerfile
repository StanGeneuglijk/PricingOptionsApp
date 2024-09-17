# Use the official Python image from the Docker Hub (version 3.11 as in your devcontainer setup)
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to install dependencies
COPY requirements.txt ./ 

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Streamlit (in case it's not in requirements.txt)
RUN pip install --no-cache-dir streamlit

# Copy the rest of your app code into the container
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]
