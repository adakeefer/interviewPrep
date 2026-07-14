'''



goal: sim engine
input: list of agents, list of events

constraints:
* each event updates one agent
* some events might not reference an agent
* otherwise, inputs well formed and schema same throughout
* energy <= 100, >= 0
* 

AGENT
{
    "id": "a1",
    "energy": 50,
    "completed_work": 0,
}


WORK event
{
		"time": 1,
    "type": "work",
    "agent_id": "a1",
    "cost": 20,
}


REST event
{
	"time": 2,
    "type": "rest",
    "agent_id": "a1",
    "amount": 10,
}


when work:
* if not enough energy, ignore
* else, energy -= work cost
* completed work += 1

when rest:
* add amount to energy


{
    "time": 3,
    "type": "connect",
    "agent_id": "a1",
    "target_agent_id": "a2",
}

{
    "time": 3,
    "type": "connect",
    "agent_id": "a2",
    "target_agent_id": "a3",
}

a1 -> a2 

a1 -> [a2]
a2 -> [a1]

a2 -> a3

a1 ->[a2, a3]
a2 -> [a1, a3]
a3 -> [a2, a1]



agent[neightbors] = [a2, a3]

apply_update():
    visited()
    neighbors = agent_map[agent][neighbors]
    queue(neighbors)

'''

from collections import deque

def apply_connection(agent_map, event):
    visited = set()
    queue = deque()
    curr = agent_map['agent_id']
    targets = set(event['target_agent_id'])
    queue.append(curr)
    while len(queue) > 0:
        curr = queue.popleft()
        visited.add(curr)
        for target in targets:
            curr['neighbors'].add(target)
        targets = set(curr['neighbors'])
        for neighbor in curr['neighbors']:
            queue.append(agent_map[neighbor]) 

def apply_work(agent_map, event):
    visited = set()
    queue = deque()
    curr = agent_map['agent_id']
    cost = event['cost']
    queue.append(curr)
    while len(queue) > 0:
        curr = queue.popleft()
        visited.add(curr)
        if curr['energy'] >= cost:
            curr['energy'] -= cost
            curr['completed_work'] += 1
        for neighbor in curr['neighbors']:
            queue.append(agent_map[neighbor]) 

def apply_rest(agent_map, event):
    visited = set()
    queue = deque()
    curr = agent_map['agent_id']
    amount = event['amount']
    queue.append(curr)
    while len(queue) > 0:
        curr = queue.popleft()
        visited.add(curr)
        curr['energy'] = min(100, curr['energy'] + amount)
        for neighbor in curr['neighbors']:
            queue.append(agent_map[neighbor]) 


def build_agent_map(agents):
    res = {}
    for agent in agents:
        agent['neighbors'] = set()
        res[agent['id']] = agent
    
    return res


def apply_events(agents, events):
    agent_map = build_agent_map(agents)

    sorted_events = sorted(events, key=lambda ev: ev['time'])
    for event in sorted_events:
        target_agent = event['agent_id']
        if target_agent not in agent_map:
            continue
        agent = agent_map[target_agent]
        if event['type'] == 'work':
            apply_work(agent_map, event)
        elif event['type'] == 'rest':
            apply_rest(agent_map, event)
        else:
            if event['target_agent_id'] not in agent_map:
                continue
            else:
                apply_connection(agent_map, event)

    return agent_map.values()


input = {
  "agents": [
    {
      "id": "a1",
      "energy": 50,
      "completed_work": 0
    }
  ],
  "events": [
    {
      "time": 1,
      "type": "work",
      "agent_id": "a1",
      "cost": 20
    }
  ]
}

input = {
  "agents": [
    {
      "id": "a1",
      "energy": 50,
      "completed_work": 0
    },
    {
      "id": "a2",
      "energy": 95,
      "completed_work": 2
    },
    {
      "id": "a3",
      "energy": 10,
      "completed_work": 0
    },
    {
      "id": "a4",
      "energy": 0,
      "completed_work": 5
    }
  ],
  "events": [
    {
      "time": 1,
      "type": "work",
      "agent_id": "a1",
      "cost": 20
    },
    {
      "time": 2,
      "type": "rest",
      "agent_id": "a2",
      "amount": 10
    },
    {
      "time": 3,
      "type": "work",
      "agent_id": "a3",
      "cost": 15
    },
    {
      "time": 4,
      "type": "rest",
      "agent_id": "unknown",
      "amount": 50
    },
    {
      "time": 5,
      "type": "work",
      "agent_id": "a3",
      "cost": 10
    },
    {
      "time": 6,
      "type": "rest",
      "agent_id": "a4",
      "amount": 30
    },
    {
      "time": 7,
      "type": "work",
      "agent_id": "a1",
      "cost": 5
    }
  ]
}



print(apply_events(input['agents'], input['events']))