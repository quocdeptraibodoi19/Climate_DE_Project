FROM apache/airflow:latest
USER root

# Install OpenJDK-11
RUN apt update && \
    apt-get install -y openjdk-11-jdk procps wget && \
    apt-get install -y ant && \
    apt-get clean;

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME
RUN wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.264/aws-java-sdk-bundle-1.12.264.jar && \
    wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.1/hadoop-aws-3.3.1.jar

USER airflow
COPY requirements.txt /
# RUN pip install --no-cache-dir -r /requirements.txt
RUN  pip install pandas apache-airflow pyspark &&  pip install --no-cache-dir -r /requirements.txt