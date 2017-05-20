FROM ubuntu:16.04

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -qq && apt-get upgrade -qq \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-setuptools \
        supervisor \
        python-opencv \
    && BUILD_DEPS='build-essential python3-dev git' \
    && apt-get install -y --no-install-recommends ${BUILD_DEPS}

COPY requirements.txt /opt/emobot/
RUN pip3 install --no-cache-dir -r /opt/emobot/requirements.txt

COPY etc/ /etc/

COPY app/ /opt/emobot/app/

WORKDIR /opt/emobot/app

RUN python3 -c 'import compileall, os; compileall.compile_dir(os.curdir, force=1)' > /dev/null

RUN apt-get autoremove -y ${BUILD_DEPS} \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["supervisord", "-n","-c", "/etc/supervisor/supervisord.conf"]
