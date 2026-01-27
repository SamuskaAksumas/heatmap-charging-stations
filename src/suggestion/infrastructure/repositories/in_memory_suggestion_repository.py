# src/suggestion/infrastructure/repositories/in_memory_suggestion_repository.py

class InMemorySuggestionRepository:
    def __init__(self):
        self._storage = {}  # Stores {id: aggregate_object}
        self._next_id = 1

    def save(self, aggregate):
        # Assign ID if the entity doesn't have one yet
        if aggregate.entity.id is None:
            aggregate.entity.id = self._next_id
            self._next_id += 1
        
        self._storage[aggregate.entity.id] = aggregate
        return aggregate

    def get_by_id(self, suggestion_id):
        return self._storage.get(suggestion_id)

    def get_all_including_deleted(self):
        return list(self._storage.values())
