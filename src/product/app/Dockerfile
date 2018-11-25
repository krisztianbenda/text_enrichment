FROM python:3.6-slim 

COPY . /app
WORKDIR /app
ENV PYTHONPATH /
RUN pip install -r requirements.txt

CMD python app.py

EXPOSE 5000
