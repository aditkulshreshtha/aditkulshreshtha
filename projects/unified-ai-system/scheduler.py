class Scheduler:
    def __init__(self):
        self.queue = []
        self.rejections = 0

    def submit(self, request, system_load):
        priority = request['priority']

        if system_load > 0.95 and priority == 'low':
            self.rejections += 1
            return 'rejected'

        if system_load > 0.80:
            self.queue.append(request)
            return 'queued'

        return 'processed'

    def queue_size(self):
        return len(self.queue)
