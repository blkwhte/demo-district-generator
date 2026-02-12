# 1. Base Image: Use a lightweight Python environment
FROM python:3.9-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy requirements first (for efficient caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your app code
COPY . .

# 6. Expose the port Streamlit runs on
EXPOSE 8501

# 7. The command to run the app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]