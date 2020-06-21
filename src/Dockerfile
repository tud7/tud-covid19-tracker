FROM python:3.7
LABEL maintainer "Tu Duong <tduongcs@gmail.com>"
WORKDIR /code
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY ./ ./
EXPOSE 8050
CMD ["python", "./app.py"]
