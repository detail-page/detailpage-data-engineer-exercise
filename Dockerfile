FROM apache/spark:3.5.3-scala2.12-java11-python3-ubuntu

USER root

RUN pip install --no-cache-dir pytest==8.3.3 pyarrow==17.0.0

# `spark` has no writable home in this image; give it one so pip/ivy/pytest work.
RUN mkdir -p /home/spark && chown -R spark:spark /home/spark
ENV HOME=/home/spark
ENV SPARK_HOME=/opt/spark
ENV PATH="/opt/spark/bin:/opt/spark/sbin:${PATH}"

WORKDIR /work
USER spark
