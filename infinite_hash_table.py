from __future__ import annotations
from typing import Generic, TypeVar, List

from data_structures.referential_array import ArrayR
from data_structures.linked_stack import LinkedStack
from algorithms.mergesort import mergesort

K = TypeVar("K")
V = TypeVar("V")

class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """


    TABLE_SIZE = 27

    def __init__(self, level: int = 0):
        """Best and worst case complexity of O(1), has a constant complexity"""
        self.level = level
        self.table = ArrayR(self.TABLE_SIZE)
        self.count = 0 

    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
       
        Complexity:
        Best case: O(1*Comp(hash))
        Worst case: O(n*Comp(hash)) where n is the number of elements in the hash table, occurs when there are collisions"""
        position = self.hash(key)

        if isinstance(self.table[position], tuple):
            if self.table[position][0] == key:
                return self.table[position][1]

        if isinstance(self.table[position], InfiniteHashTable):
            return self.table[position][key]

        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        Complexity:
        Best case: O(1*Comp(hash)), when hash position is empty
        Worst case: O(n*Comp(hash)) where n is the number of elements in the hash table, when there are collisions
        """
        position = self.hash(key)

        if self.table[position] == None:
            self.table[position] = (key, value)
            return

        if isinstance(self.table[position], tuple):
            if self.table[position][0] == key:
                self.table[position] = (key, value)
   
            old_key, old_value = self.table[position]
            self.table[position] = InfiniteHashTable(level=self.level + 1)
            self.table[position][old_key] = old_value
           

        if isinstance(self.table[position], InfiniteHashTable):
            self.table[position][key] = value

    def __delitem__(self, key: K) -> None:
        """"
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        Best case: O(1*Comp(hash))
        Worst case: O(n*Comp(hash)) where n is the number of elements in the hash table, occurs from deleting a key involved in a collision
        """
        position = self.hash(key)
        remaining = []

        if self.table[position] is None:
            raise KeyError(key)

        if isinstance(self.table[position], tuple):
            if self.table[position][0] == key:
                self.table[position] = None

            for index in self.table:
                if index is not None:
                    remaining.append(index)
       
            if len(remaining) == 1:
                if isinstance(remaining[0], tuple):
                    return True
            return False

        if isinstance(self.table[position], InfiniteHashTable):
            delete_internal = self.table[position].__delitem__(key)
       
            if delete_internal:
                internal_remaining = []
                for entry in self.table[position].table:
                    if entry is not None:
                        internal_remaining.append(entry)
                if len(internal_remaining) == 1:
                    self.table[position] = internal_remaining[0]
               
                    remaining_keys = []
                    for entry in self.table:
                        if entry is not None:
                            remaining_keys.append(entry)
                    if len(remaining_keys) == 1:
                        if isinstance(remaining_keys[0], tuple):
                            return True
            return False

        raise KeyError(key)

    def __len__(self) -> int:
        """Best case complexity: O(1), only one element in the table
        Worst case complexity: O(n), where n is the number of elements in the hash table, where it iterates through all elements to find the length """
        current_length = 0
        for position in self.table:
            if isinstance(position, tuple):
                current_length += 1
            elif isinstance(position, InfiniteHashTable):
                current_length += len(position)
            else:
                continue
        return current_length

    def get_location(self, key: K) -> List[int]:
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.
        Best case complexity: O(1*O(hash)), where location is found immediately
        Worst case complexity: O(n*O(hash)), where n is the number of elements in the hash table, when collsions occur and needs to traverse over internal hash tables
        """
        position = self.hash(key)
        location = [position]

        if isinstance(self.table[position], tuple):
            if self.table[position][0] == key:
                return location

        if isinstance(self.table[position], InfiniteHashTable):
            location = location + self.table[position].get_location(key)
            return location

        raise KeyError(key)
   
    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def sort_keys(self) -> List[str]:
        """
        Returns all keys currently in the table in lexicographically sorted order.
        Has a best case and worst case complexity of O(n*logn) using mergesort where n refers to the total number of elements in the table
        """
        keys = []
        for position in self.table:
            if isinstance(position, tuple):
                keys.append(position[0])
            elif isinstance(position, InfiniteHashTable):
                for key in position.sort_keys():
                    keys.append(key)
            else:
                continue
        return mergesort(keys, key=lambda x: x)
