FROM python:3.12

# Set the working directory where the application code will reside
WORKDIR /app

# Copy and install requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the app directory. This helps us keep our build clean and efficient.
COPY ./app ./app

# Expose the port
EXPOSE 8000

# Start the FastAPI server 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
