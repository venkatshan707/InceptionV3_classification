# Use Python 3.11 as the base image
FROM python:3.11

# Set the working directory
WORKDIR /usr/src/app

# Copying the requirements file
COPY requirements.txt ./

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code to the container
COPY . .

# Set the command to run the container at startup
CMD ["python", "app.py"]
