#  We are pulling the following tensorflow image which satisfies our tensorflow version
ARG BASE_IMG=tensorflow/tensorflow:2.1.0-py3-jupyter
FROM $BASE_IMG

ARG PROJECT_ROOT="."
ARG PROJECT_MOUNT_DIR="/"

ADD $PROJECT_ROOT $PROJECT_MOUNT_DIR

WORKDIR $PROJECT_MOUNT_DIR

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD [ "/main.py" ]