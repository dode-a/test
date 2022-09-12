FROM python:3.9

WORKDIR /opt/app

COPY . .

RUN pip install --no-cache-dir -r requirements-prod.txt

EXPOSE 80

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0","--port=80"]