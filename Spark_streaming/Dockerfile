FROM gettyimages/spark:2.4.1-hadoop-3.0

# Set working directory
WORKDIR /app

# Copy the streaming script and JAR connectors
# COPY custom_logger.py /app
COPY spark_stream.py /app/
COPY requirements.txt /app/ 
COPY /jars/spark-sql-kafka-0-10_2.11-2.4.5.jar /app/
COPY /jars/kafka-clients-2.2.0.jar /app/
COPY /jars/postgresql-42.3.1.jar /app/

# Install dependencies
RUN pip install --upgrade pip && pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Execute the Spark job on container start
# ENTRYPOINT ["spark-submit", "--jars", "/app/spark-sql-kafka-0-10_2.11-2.4.5.jar,/app/kafka-clients-2.2.0.jar", "--driver-class-path", "/app/kafka-clients-2.2.0.jar", "/app/spark_stream.py"]
ENTRYPOINT ["spark-submit", "--jars", "/app/spark-sql-kafka-0-10_2.11-2.4.5.jar,/app/kafka-clients-2.2.0.jar,/app/postgresql-42.3.1.jar", "--driver-class-path", "/app/kafka-clients-2.2.0.jar:/app/postgresql-42.3.1.jar", "/app/spark_stream.py"]
