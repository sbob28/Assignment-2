from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')

class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.

    #Best case complexity is O(1).
    #only involves simple assignments and attribute initialization

    #Worst case complexity is O(N), N is the length of 'sizes'
    #because it involves accessing and initializing 'self.TABLE_SIZES' and 'self.array'
    #based on the input list 'sizes,' which can be a linear operation
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes:list|None=None, internal_sizes:list|None=None) -> None:
        "Best and worst case complexity O(1)"
        self.sizes = sizes
        self.internal_sizes = internal_sizes

        if sizes is not None:
            self.TABLE_SIZES = self.sizes

        if internal_sizes is not None:
            self.internal_sizes = self.internal_sizes
        else:
            self.internal_sizes = self.TABLE_SIZES

        self.size_index = 0
        self.array = ArrayR(self.TABLE_SIZES[0])
        self.count = 0

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int]:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.

            #best-case complexity is O(1) when the desired pos is found immediately without collisions.

    #worst-case complexity is O(N)
    #where N is the size of the hash table, as it may require iterating through the entire table if there are many collisions
    #resulting in linear probing until an empty slot or a full table
        """
        position = self.hash1(key1)
       
        for _ in range(self.table_size):
            current_key, subtable = self.array[position] if self.array[position] else (None, None)
           
            if current_key is None:
                if is_insert:
                    subtable = LinearProbeTable(self.internal_sizes)
                    subtable.hash = lambda key2: self.hash2(key2, subtable)
                    self.array[position] = (key1, subtable)
                    self.count += 1
                    return position, subtable._linear_probe(key2, is_insert)
                else:
                    raise KeyError(key1)
            elif current_key == key1:
                return position, subtable._linear_probe(key2, is_insert)
            else:
                position = (position + 1) % self.table_size
               
        raise FullError("Table is full")


    def iter_keys(self, key:K1|None=None) -> Iterator[K1|K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.

        # best-case complexity is O(1) when 'key' is found immediately
        # at the expected pos in the hash table.

        # worst-case complexity is O(N) in scenarios where there are many hash collisions
        # as it may require iterating through the entire table or a subtable to find 'key'
        # or to enumerate all keys when 'key' is None
        # resulting in a linear time operation.
        """
       
        if key is None:
            for entry in self.array:
                if entry:
                    yield entry[0]
            raise BaseException("No keys found in the hash table.")
        else:
            top_level_key_index = self.hash1(key)
            entry = self.array[top_level_key_index]
            if entry and entry[0] == key:
                yield from entry[1].iter_keys()
            else:
                raise BaseException(f"Key '{key}' not found in the hash table.")

    def keys(self, key:K1|None=None) -> list[K1|K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.

        #best-case complexity is O(1) when 'key' is found immediately at the expected position
        # in the table or subtable
        # or when 'key' is None and there are no top-level keys.

        # worst-case complexity is O(N) when there are many top-level keys and 'key' is None
        # N represents the number of top-level keys in the hash table.
        # as it may require iterating through the entire table to collect all top-level keys
        # or O(M) when 'key' is specified
        # where M is the number of top-level keys,
        # as it may require searching through each subtable to find the bottom-level keys associated with 'key'.
        """
        if key is None:
            return [entry[0] for entry in self.array if entry is not None]
        else:
            for entry in self.array:
                if entry is not None and entry[0] == key:
                    return list(entry[1].keys())
            return []



    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.

    Best-case complexity O(1) when 'key' is found immediately at the expected pos
    and when 'key' is None and there are no top lvll keys.

    Worst-case complexity O(N) when key is none, where N is the number of top lvl keys,
    as it may require iterating through the entire table to collect all values
        """
        if key is None:
            for entry in self.array:
                if entry is not None:
                    yield from entry[1].values()
        else:
            for entry in self.array:
                if entry is not None and entry[0] == key:
                    yield from entry[1].values()

        raise KeyError(f"Key '{key}' not found in the hash table.")
   


    def values(self, key:K1|None=None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.

            # best complexity O(1) when 'key' is found immediately at the expected pos
            # and when 'key' is None and there are no top-level keys

            # Worst complexityO(N) when 'key' is None, where N is the number of top-level keys,
            # as it may require iterating through the entire table to collect all values
        """
        if key is None:
            all_values = []
            for entry in self.array:
                if entry is not None:
                    all_values.extend(entry[1].values())
            return all_values
        else:
            top_level_key_index = self.hash1(key)
            entry = self.array[top_level_key_index]
            if entry is not None and entry[0] == key:
                return list(entry[1].values())
            else:
                return []

           
    def __contains__(self, key: tuple[K1, K2]) -> bool:
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

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key
        :raises KeyError: when the key doesn't exist.

        # Best case O(1) when the desired key is found immediately at  expected pos in the hash table.

        # worstcase complexity O(N) when there are many hash collisions
        # as it may require linear probing through the table to locate the desired key
        # and then access the subtable to retrieve the value,
        # resulting in a linear time operation in the worst case.
        """
        key1, key2 = key
        position, _ = self._linear_probe(key1, key2, False)
        return self.array[position][1][key2]


    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.

        # Best case is O(1) when the desired pos for the key is found immediately without collisions.
       
        # Worst case is O(N) when there are many hash collisions and the table requires rehashing.
        # Setting a key involves linear probing in the worst case
        # rehashing operation can also be O(N) if all keys collide,
        #  where N is the size of the hash table.
        """
        position, _ = self._linear_probe(*key, True)
        self.array[position][1][key[1]] = data

        if len(self) > self.table_size // 2:
            self._rehash()
       

    def __delitem__(self, key: tuple[K1, K2]) -> None:

        """  
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
 
        # best case O(1) when the desired position for the key is found immediately without collision/s.

        # worst case O(N) in scenarios with many hash collisions
        #  as it may involve linear probing and repositioning elements within the table
        # resulting in a linear time operation in the worst case."""

        key1, key2 = key
        position1, position2 = self._linear_probe(key1, key2, False)

        if self.array[position1] is None:
            raise KeyError(key1)

        sub_table = self.array[position1][1]

        if key2 in sub_table:
            del sub_table[key2]

            if not sub_table:
                self.array[position1] = None
                self.count -= 1

            position2 = (position2 + 1) % sub_table.table_size
            while sub_table.array[position2]:
                k2, value = sub_table.array[position2]
                sub_table.array[position2] = None

                newpos = sub_table._linear_probe(k2, True)
                sub_table.array[newpos] = (k2, value)
                position2 = (position2 + 1) % sub_table.table_size

        position1 = (position1 + 1) % self.table_size
        while self.array[position1]:
            k1, sub_table = self.array[position1]
            self.array[position1] = None

            newpos, _ = self._linear_probe(k1, key2, True)
            self.array[newpos] = (k1, sub_table)
            position1 = (position1 + 1) % self.table_size



    def _rehash(self) -> None:

        """  
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        """

        current_table = self.array
        self.size_index += 1
        if self.size_index >= len(self.TABLE_SIZES):
            return
        new_size = self.TABLE_SIZES[self.size_index]
        self.array = ArrayR[tuple[K1, V]](new_size)
        self.count = 0
       
        for i in current_table:
            if i is not None:
                k1, val = i
                if isinstance(val, LinearProbeTable):
                    for n in val.array:
                        if n is not None:
                            k2, data = n
                            self[(k1, k2)] = data


    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)

        #best and worst case O(1)
        # simply returns the length of the 'array,'
        # which is a constant-time operation regardless of the array size
        """
        return len(self.array)


    def __len__(self) -> int:
        """
        Returns number of elements in the hash table

    # best and worst case time complexity for this code is both O(1),
    # as it directly returns the value of 'count,'
    # which is a constant-time operation
    # and does not depend on the number of elements in the hash table.
        """
        return self.count



    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.

        # best case O(N) when there are many elements in the hash table,
        # as it iterates through the 'array' and subtables to build the string representation,
        # resulting in linear time complexity in the best case.

        # worst case O(N) for the same reason as the best case,
        # as it always needs to process all elements and subtables to create the string representation.
        """
        result = "{\n"
        for entry in self.array:
            if entry is not None:
                key1, sub_table = entry
                result += f"  '{key1}': {str(sub_table)},\n"
        result += "}"
        return result