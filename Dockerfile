FROM animcogn/face_recognition

# Set the working directory
WORKDIR /app

# Install required system packages for building dlib
RUN apt-get update && apt-get install -y cmake build-essential

# Copy SSL certificates
COPY ssl/localhost.crt /app/ssl/localhost.crt
COPY ssl/localhost.key /app/ssl/localhost.key

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

# Copy requirements and install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .