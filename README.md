# user-access-simulator


## cacheHitSimulations.py

This script runs simulations to analyze cache hit rates under different configurations.

It varies:

- Number of scenes requested per request
- Cache expiration time

For each combination, it simulates cache requests and counts the number of "cold storage hits". This represents when a request cannot be served from cache and must fetch from cold storage.

The hit rate is calculated as:

```
cold_storage_hits / number_of_requests
```

Results are saved to `results.csv` including:

- Number of requests
- Cache expiration
- Scenes per request
- Cold storage hits
- Hit rate

Rows are sorted by highest to lowest hit rate.

This allows analyzing which factors increase the cache hit rate and reduce trips to slow cold storage.
