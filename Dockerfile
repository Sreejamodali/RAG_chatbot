# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /RAG

# Copy the requirements file into the container
COPY ./requirements.txt /RAG/requirements.txt

# Install Streamlit
RUN pip install streamlit

# Add /usr/local/bin to the PATH
ENV PATH="/usr/local/bin:$PATH"

# Copy the entire project directory into the container
COPY . .

# Expose the port for Streamlit
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "main1.py", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
