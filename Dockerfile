# Use official Apify Python image
FROM apify/actor-python:3.11

# Copy source code
COPY . ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entry point
CMD ["python", "main.py"]
