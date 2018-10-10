FROM is-skeletons-detector/dev

WORKDIR /opt/is

COPY src/ src
COPY setup.py .
COPY etc/conf/options.json .

RUN pip install .

CMD [ "is-skeletons-detector" ]