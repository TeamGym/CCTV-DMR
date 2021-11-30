FROM python:3.9

RUN apt-get update
RUN apt-get install -y libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
RUN apt-get install -y gstreamer1.0-libav gstreamer1.0-tools
RUN apt-get install -y python3-gst-1.0
RUN apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libfontconfig1-dev libfreetype6-dev libpng-dev libcairo2-dev libjpeg-dev libgif-dev libgstreamer-plugins-base1.0-dev
RUN apt-get install -y gir1.2-gst-rtsp-server-1.0

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src/
COPY ./doc ./doc/

VOLUME ./db

CMD [ "python", "./src/app.py" ]
EXPOSE 8080