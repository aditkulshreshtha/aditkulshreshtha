class Scheduler:
    """Priority-aware queue with retries and expiration."""

    PRIORITY_ORDER = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    def __init__(self):
        self.queue = []

    def submit(self, request, system_load, current_tick):
        priority = request["priority"]

        if system_load > 0.95 and priority == "low":
            return "rejected"

        if system_load > 0.92 and priority == "medium":
            self.enqueue(request, current_tick)
            return "queued"

        if system_load > 0.80 and priority == "low":
            self.enqueue(request, current_tick)
            return "queued"

        return "processed"

    def enqueue(self, request, current_tick):
        queued_request = dict(request)
        queued_request["queued_at"] = current_tick
        queued_request["attempts"] = queued_request.get("attempts", 0) + 1
        self.queue.append(queued_request)

    def drain_ready(self, system_load, current_tick):
        if system_load > 0.78 or not self.queue:
            return None

        self.queue.sort(
            key=lambda request: (
                self.PRIORITY_ORDER.get(request["priority"], 1),
                request["queued_at"],
            )
        )

        return self.queue.pop(0)

    def expire(self, current_tick):
        expired = []
        retained = []

        for request in self.queue:
            deadline = request.get("deadline_tick", current_tick + 1)
            if current_tick > deadline:
                expired.append(request)
            else:
                retained.append(request)

        self.queue = retained
        return expired

    def queue_size(self):
        return len(self.queue)
