class FeedbackLoop:
    def adjust_budget(self, success_score, current_budget):
        if success_score < 0.6:
            return int(current_budget * 1.2)
        if success_score > 0.9:
            return int(current_budget * 0.8)
        return current_budget
