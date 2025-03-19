FROM python:3.11
WORKDIR /usr/local/app

# Import code, assets into image
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt 

# Copy in source code
COPY DV_app ./
EXPOSE 8020

# Command to launch when running image
CMD [ "python", "./dash_app.py" ]