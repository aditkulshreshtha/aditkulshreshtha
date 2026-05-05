class ContextOS:
    def __init__(self):
        self.fresh = []
        self.recent = []
        self.old = []
        self.archive = []

    def add(self, data, age='fresh'):
        getattr(self, age).append(data)

    def get_context(self):
        return self.fresh + self.recent[:5] + self.old[:2]

    def age_context(self):
        self.archive += self.old
        self.old = self.recent
        self.recent = self.fresh
        self.fresh = []
