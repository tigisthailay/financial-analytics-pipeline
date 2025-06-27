FROM ghcr.io/dbt-labs/dbt-postgres:1.6.0

WORKDIR /app

COPY . /app

#to excute dbt run cmd only
ENTRYPOINT ["dbt"]
CMD ["run"]

# to excute dbt run and dbt test
# CMD ["/bin/bash", "-c", "dbt run && dbt test"]
# RUN chmod +x /app/run_and_test.sh

# CMD ["./run_and_test.sh"]

