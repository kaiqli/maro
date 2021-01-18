# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.


import json

import redis
from redis.lock import Lock


class RedisController:
    def __init__(self, host: str, port: int):
        self._redis = redis.Redis(host=host, port=port, encoding="utf-8", decode_responses=True)

    """Master Details Related."""

    def get_master_details(self, cluster_name: str) -> dict:
        return json.loads(
            self._redis.get(f"{cluster_name}:master_details")
        )

    def set_master_details(self, cluster_name: str, master_details: dict) -> None:
        self._redis.set(
            f"{cluster_name}:master_details",
            json.dumps(master_details)
        )

    def delete_master_details(self, cluster_name: str) -> None:
        self._redis.delete(f"{cluster_name}:master_details")

    """Node Details Related."""

    def get_name_to_node_details(self, cluster_name: str) -> dict:
        name_to_node_details = self._redis.hgetall(
            f"{cluster_name}:name_to_node_details"
        )
        for node_name, node_details_str in name_to_node_details.items():
            name_to_node_details[node_name] = json.loads(node_details_str)
        return name_to_node_details

    def get_node_details(self, cluster_name: str, node_name: str) -> dict:
        node_details = self._redis.hget(
            f"{cluster_name}:name_to_node_details",
            node_name
        )
        if node_details is None:
            return {}
        else:
            return json.loads(node_details)

    def set_node_details(self, cluster_name: str, node_name: str, node_details: dict) -> None:
        self._redis.hset(
            f"{cluster_name}:name_to_node_details",
            node_name,
            json.dumps(node_details)
        )

    def delete_node_details(self, cluster_name: str, node_name: str) -> None:
        self._redis.hdel(
            f"{cluster_name}:name_to_node_details",
            node_name
        )

    def push_resource_usage(self,
        cluster_name: str,
        node_name: str,
        cpu_usage: list,
        memory_usage: float,
        gpu_memory_usage: list
    ):
        # Push cpu usage to redis
        self._redis.rpush(
            f"{cluster_name}:{node_name}:cpu_usage_per_core",
            json.dumps(cpu_usage)
        )

        # Push memory usage to redis
        self._redis.rpush(
            f"{cluster_name}:{node_name}:memory_usage",
            json.dumps(memory_usage)
        )

        # Push gpu memory usage to redis
        self._redis.rpush(
            f"{cluster_name}:{node_name}:gpu_memory_usage",
            json.dumps(gpu_memory_usage)
        )

    def get_resource_usage(self, cluster_name: str, node_name: str, condition: str):
        if condition == "cpu":
            resource_usage = self._redis.lrange(
                f"{cluster_name}:{node_name}:cpu_usage_per_core",
                0, -1
            )
        elif condition == "memory":
            resource_usage = self._redis.lrange(
                f"{cluster_name}:{node_name}:memory_usage",
                0, -1
            )
        elif condition == "gpu":
            resource_usage = self._redis.lrange(
                f"{cluster_name}:{node_name}:gpu_memory_usage",
                0, -1
            )
        else:
            raise KeyError(f"Unsupport type of resource. {condition}.")

        return resource_usage

    def get_resource_usage_latest(self, cluster_name: str, node_name: str, condition: str, timeout: int):
        if condition == "cpu":
            resource_usage_latest = self._redis.brpoplpush(
                f"{cluster_name}:{node_name}:cpu_usage_per_core",
                f"{cluster_name}:{node_name}:cpu_usage_per_core",
                timeout
            )
        elif condition == "memory":
            resource_usage_latest = self._redis.brpop(
                f"{cluster_name}:{node_name}:memory_usage",
                f"{cluster_name}:{node_name}:memory_usage",
                timeout
            )
        elif condition == "gpu":
            resource_usage_latest = self._redis.brpop(
                f"{cluster_name}:{node_name}:gpu_memory_usage",
                f"{cluster_name}:{node_name}:gpu_memory_usage",
                timeout
            )
        else:
            raise KeyError(f"Unsupport type of resource. {condition}.")

    """Job Details Related."""

    def get_name_to_job_details(self, cluster_name: str) -> dict:
        name_to_job_details = self._redis.hgetall(
            f"{cluster_name}:name_to_job_details",
        )
        for job_name, job_details_str in name_to_job_details.items():
            name_to_job_details[job_name] = json.loads(job_details_str)
        return name_to_job_details

    def get_job_details(self, cluster_name: str, job_name: str) -> dict:
        return_str = self._redis.hget(
            f"{cluster_name}:name_to_job_details",
            job_name
        )
        return json.loads(return_str) if return_str is not None else None

    def set_job_details(self, cluster_name: str, job_name: str, job_details: dict) -> None:
        self._redis.hset(
            f"{cluster_name}:name_to_job_details",
            job_name,
            json.dumps(job_details)
        )

    def delete_job_details(self, cluster_name: str, job_name: str) -> None:
        self._redis.hdel(
            f"{cluster_name}:name_to_job_details",
            job_name
        )

    """Schedule Details Related."""

    def get_name_to_schedule_details(self, cluster_name: str) -> dict:
        name_to_schedule_details = self._redis.hgetall(
            f"{cluster_name}:name_to_schedule_details",
        )
        for schedule_name, schedule_details_str in name_to_schedule_details.items():
            name_to_schedule_details[schedule_name] = json.loads(schedule_details_str)
        return name_to_schedule_details

    def get_schedule_details(self, cluster_name: str, schedule_name: str) -> dict:
        return_str = self._redis.hget(
            f"{cluster_name}:name_to_schedule_details",
            schedule_name
        )
        return json.loads(return_str) if return_str is not None else None

    def set_schedule_details(self, cluster_name: str, schedule_name: str, schedule_details: dict) -> None:
        self._redis.hset(
            f"{cluster_name}:name_to_schedule_details",
            schedule_name,
            json.dumps(schedule_details)
        )

    def delete_schedule_details(self, cluster_name: str, schedule_name: str) -> None:
        self._redis.hdel(
            f"{cluster_name}:name_to_schedule_details",
            schedule_name
        )

    """Container Details Related."""

    def get_name_to_container_details(self, cluster_name: str) -> dict:
        name_to_container_details = self._redis.hgetall(
            f"{cluster_name}:name_to_container_details",
        )
        for container_name, container_details in name_to_container_details.items():
            name_to_container_details[container_name] = json.loads(container_details)
        return name_to_container_details

    def set_multiple_container_details(self, cluster_name: str, name_to_container_details: dict) -> None:
        self._redis.delete(f"{cluster_name}:container_details")
        if len(name_to_container_details) == 0:
            return
        else:
            for container_name, container_details in name_to_container_details.items():
                name_to_container_details[container_name] = json.dumps(container_details)
            self._redis.hmset(
                f"{cluster_name}:name_to_container_details",
                name_to_container_details
            )

    def set_container_details(self, cluster_name: str, container_name: str, container_details: dict) -> None:
        self._redis.hset(
            f"{cluster_name}:name_to_container_details",
            container_name,
            container_details
        )

    """Pending Job Tickets Related."""

    def get_pending_job_ticket(self, cluster_name: str):
        return self._redis.lrange(
            f"{cluster_name}:pending_job_tickets",
            0,
            -1
        )

    def push_pending_job_ticket(self, cluster_name: str, job_name: str):
        self._redis.rpush(
            f"{cluster_name}:pending_job_tickets",
            job_name
        )

    def remove_pending_job_ticket(self, cluster_name: str, job_name: str):
        self._redis.lrem(
            f"{cluster_name}:pending_job_tickets",
            0,
            job_name
        )

    def delete_pending_jobs_queue(self, cluster_name: str):
        self._redis.delete(f"{cluster_name}:pending_job_tickets")

    """Killed Job Tickets Related."""

    def get_killed_job_ticket(self, cluster_name: str):
        return self._redis.lrange(
            f"{cluster_name}:killed_job_tickets",
            0,
            -1
        )

    def push_killed_job_ticket(self, cluster_name: str, job_name: str):
        self._redis.rpush(
            f"{cluster_name}:killed_job_tickets",
            job_name
        )

    def remove_killed_job_ticket(self, cluster_name: str, job_name: str):
        self._redis.lrem(
            f"{cluster_name}:killed_job_tickets",
            0,
            job_name
        )

    def delete_killed_jobs_queue(self, cluster_name: str):
        self._redis.delete(f"{cluster_name}:killed_job_tickets")

    """Fault Tolerance Related"""

    def get_rejoin_component_name_to_container_name(self, job_id: str) -> dict:
        return self._redis.hgetall(
            f"job:{job_id}:rejoin_component_name_to_container_name"
        )

    def get_rejoin_container_name_to_component_name(self, job_id: str) -> dict:
        component_name_to_container_name = self.get_rejoin_component_name_to_container_name(job_id=job_id)
        return {v: k for k, v in component_name_to_container_name.items()}

    def delete_rejoin_container_name_to_component_name(self, job_id: str) -> None:
        self._redis.delete(
            f"job:{job_id}:rejoin_component_name_to_container_name"
        )

    def get_job_runtime_details(self, job_id: str) -> dict:
        return self._redis.hgetall(
            f"job:{job_id}:runtime_details"
        )

    def get_rejoin_component_restart_times(self, job_id: str, component_id: str) -> int:
        restart_times = self._redis.hget(
            f"job:{job_id}:component_id_to_restart_times",
            component_id
        )
        return 0 if restart_times is None else int(restart_times)

    def incr_rejoin_component_restart_times(self, job_id: str, component_id: str) -> None:
        self._redis.hincrby(
            f"job:{job_id}:component_id_to_restart_times",
            component_id,
            1
        )

    # Utils

    def get_time(self) -> int:
        """ Get current unix timestamp (seconds) from Redis server.

        Returns:
            int: current timestamp.
        """
        return self._redis.time()[0]

    def lock(self, name: str) -> Lock:
        """ Get a new lock with redis.

        Use 'with lock(name):' paradigm to do the locking.

        Args:
            name (str): name of the lock.

        Returns:
            redis.lock.Lock: lock from the redis.
        """

        return self._redis.lock(name=name)
