FROM python:3.9.18-bullseye

WORKDIR /source

ARG PORT=5000
ENV PORT=${PORT}

COPY backend/requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip install --force-reinstall --no-deps frozendict==2.3.8
COPY backend .

EXPOSE ${PORT}

ENTRYPOINT ["/bin/bash", "-c", "python3 /source/main.py"]
