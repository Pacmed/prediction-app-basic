FROM python:3.7

SHELL ["/bin/bash", "-c"]
WORKDIR /www

# Copy the complete repository to the /www folder
COPY . /www

# Upgrade pip and install the required packages
RUN pip install pip==19.0.3
RUN pip install -e .

CMD ["python", "src/api.py"]