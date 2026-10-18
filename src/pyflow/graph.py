from heapq import heapify, heappop, heappush

from .models import Workflow


def _prepare_graph(workflow: Workflow) -> tuple[dict[str, int], dict[str, set[str]]]:
    workflow.validate()

    incoming = {name: len(task.dependencies) for name, task in workflow.tasks.items()}
    following = {name: set() for name in workflow.tasks}

    for name, task in workflow.tasks.items():
        for dependency in task.dependencies:
            following[dependency].add(name)

    return incoming, following


def topological_order(workflow: Workflow) -> list[str]:
    incoming, following = _prepare_graph(workflow)
    ready = [name for name, count in incoming.items() if count == 0]
    heapify(ready)
    order: list[str] = []

    while ready:
        name = heappop(ready)
        order.append(name)
        for next_name in following[name]:
            incoming[next_name] -= 1
            if incoming[next_name] == 0:
                heappush(ready, next_name)

    return order


def execution_layers(workflow: Workflow) -> list[list[str]]:
    incoming, following = _prepare_graph(workflow)
    ready = sorted(name for name, count in incoming.items() if count == 0)
    layers: list[list[str]] = []

    while ready:
        layers.append(ready)
        next_ready: list[str] = []

        for name in ready:
            for next_name in following[name]:
                incoming[next_name] -= 1
                if incoming[next_name] == 0:
                    next_ready.append(next_name)

        ready = sorted(next_ready)

    return layers
