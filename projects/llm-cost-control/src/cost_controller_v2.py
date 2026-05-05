class CostController:
    def __init__(self, price_per_1k=0.002):
        self.price = price_per_1k

    def compute(self, tokens):
        return (tokens / 1000.0) * self.price
