# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Set PYTHONPATH to include the 'taxi' module directory
ENV PYTHONPATH=/app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Git, Linux Dependencies for Selenium docker
RUN apt-get update && \
    apt-get install -y git gnupg wget apt-utils chromium

# Install Microsoft Edge
RUN wget -O - https://packages.microsoft.com/keys/microsoft.asc | \
    gpg --dearmor | \
    tee /usr/share/keyrings/microsoft.gpg && \
    sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list' && \
    apt update

# Finally, install gathered MS_EDGE
RUN apt install microsoft-edge-stable -y

# Copy the rest of the application code into the container
COPY . .

# Define the command to run the application
ENTRYPOINT ["python", "./taxi/features/launch_datamining.py"]
