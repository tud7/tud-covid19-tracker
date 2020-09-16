FROM python:3.7
LABEL maintainer "Tu Duong <tduongcs@gmail.com>"
COPY ./ /code
WORKDIR /code
COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt
EXPOSE 8050
ENTRYPOINT ["python", "./app.py"]