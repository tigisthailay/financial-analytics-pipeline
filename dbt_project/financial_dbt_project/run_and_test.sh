#!/bin/bash
# dbt run && dbt test
#!/bin/bash

# Run dbt models
dbt run

# Run dbt tests
dbt test

# You can add more commands here, e.g., for logging or error handling
if [ $? -eq 0 ]; then
  echo "dbt run and test completed successfully."
else
  echo "dbt run or test failed."
  exit 1
fi