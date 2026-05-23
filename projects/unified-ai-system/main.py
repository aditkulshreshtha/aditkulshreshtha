from scheduler import Scheduler
from token_allocator import TokenAllocator

scheduler = Scheduler()
allocator = TokenAllocator()

request = {
    'priority': 'high'
}

system_load = 0.82

state = scheduler.submit(request, system_load)

tokens = allocator.allocate('high', system_load)
model = allocator.choose_model('high', system_load)
cost = allocator.estimate_cost(tokens, model)

print('State:', state)
print('Tokens:', tokens)
print('Model:', model)
print('Estimated Cost:', round(cost, 4))
