class IntentClassifier:
    def classify(self, request):
        text = request.get('text','').lower()
        if 'bug' in text or 'fix' in text:
            return 'critical'
        if 'summary' in text:
            return 'low_cost'
        if 'design' in text or 'architecture' in text:
            return 'deep_reasoning'
        return 'default'
