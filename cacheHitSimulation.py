import random
from scipy.spatial import KDTree
from collections import OrderedDict
import pandas as pd


class Cache:
    def __init__(self, cache_expiration, num_scenes_per_request):
        self.cache = OrderedDict()
        self.cache_time = cache_expiration
        self.cache_life = self.cache_time

    def ping_cache(self, scene_indices):
        if self.cache_life <= 0:
            num_to_evict = max(1, int(len(self.cache) * 0.1))
            keys_to_evict = random.sample(list(self.cache.keys()), num_to_evict)
            for key in keys_to_evict:
                self.cache.pop(key)
            self.cache_life = self.cache_time

        cached_scenes = []
        for idx in scene_indices:
            if idx in self.cache:
                if random.random() > 0.1:
                    cached_scenes.append(idx)
                self.cache.move_to_end(idx)
            elif self.cache_life > 0:
                cached_scenes.append(idx)
                self.cache[idx] = True

        self.cache_life -= 1
        return cached_scenes


def run_simulation(scenes, number_of_requests, number_of_scenes_per_request, cache):
    cold_storage_hits = 0
    tree = KDTree(scenes)
    for _ in range(number_of_requests):
        random_scene = random.choice(scenes)
        nearest_scene_indices = tree.query(
            random_scene, k=number_of_scenes_per_request + 1
        )[1]
        nearest_scene_indices = [
            idx for idx in nearest_scene_indices if (scenes[idx] != random_scene).any()
        ]
        requested_scenes = cache.ping_cache(
            nearest_scene_indices[:number_of_scenes_per_request]
        )
        if len(requested_scenes) < number_of_scenes_per_request:
            cold_storage_hits += 1

    return cold_storage_hits


def append_results(
    results, cache_expiration, number_of_scenes_per_request, cold_storage_hits
):
    new_row = pd.DataFrame(
        {
            "Number of Requests": [NUMBER_OF_REQUESTS],
            "Cache Expiration": [cache_expiration],
            "number of scenes per request": [number_of_scenes_per_request],
            "Cold Storage Hits": [cold_storage_hits],
            "Cold Storage Hit Rate": [cold_storage_hits / NUMBER_OF_REQUESTS],
        }
    )
    return pd.concat([results, new_row], ignore_index=True)


def run_simulations():
    results = pd.DataFrame(
        columns=[
            "Number of Requests",
            "Cache Expiration",
            "number of scenes per request",
            "Cold Storage Hits",
            "Cold Storage Hit Rate",
        ]
    )

    for number_of_scenes_per_request in SCENES_PER_REQUEST_RANGE:
        for cache_expiration in CACHE_EXPIRATION_RANGE:
            CACHE = Cache(cache_expiration, number_of_scenes_per_request)
            cold_storage_hits = run_simulation(
                SCENES, NUMBER_OF_REQUESTS, number_of_scenes_per_request, CACHE
            )
            results = append_results(
                results,
                cache_expiration,
                number_of_scenes_per_request,
                cold_storage_hits,
            )

    results = results.sort_values(by=["Cold Storage Hit Rate"])
    results.to_csv("results.csv", index=False)


if __name__ == "__main__":
    NUMBER_OF_REQUESTS = 500
    SCENES = pd.read_csv("landsat_scenes_clipped.csv").values
    CACHE_EXPIRATION_RANGE = range(1, 6)
    SCENES_PER_REQUEST_RANGE = range(2, 11)

    run_simulations()
