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

#===============================================
# Install Linux Dependencies for Selenium docker
#===============================================
RUN apt-get update
RUN apt-get install -y chromium

# Copy the rest of the application code into the container
COPY . .


# Define the command to run the application
ENTRYPOINT ["python", "./taxi/features/launch_datamining.py"]
CMD ["--help"]
