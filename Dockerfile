# Use the official Python image from the Docker Hub
FROM python:3.11-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy the entire src directory into the container
#COPY ./src .

# Copy the entire src directory into the container
COPY ./src .

# Set the working directory in the container
#WORKDIR /app/src

# Install the inviscopilot package and its dependencies
#RUN python -m pip install -e .

# Install the inviscopilot package and its dependencies
RUN python -m pip install -e .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
ENTRYPOINT ["python", "app.py"]
#CMD ["tail", "-f", "/dev/null"]

