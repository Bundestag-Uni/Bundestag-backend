# Use an official Python runtime as a parent image
FROM python:3.10-slim

USER root
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt
    
RUN chmod -R 755 /app
# Run main.py when the container launches
CMD ["python", "main.py"]
