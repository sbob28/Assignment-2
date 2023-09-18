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
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes:list|None=None, internal_sizes:list|None=None) -> None:
        self.table_size = 0 
        #keep track of current number of internal hash tables

        self.load_factor = 0.0 #to keep track of the load factor of data structure
        # (measure of how full hash tables are)
        # 0.0 means table is empty

        self.internal_tables = ArrayR() #array to store interal hash tables

        self._initialize_table_sizes(sizes, internal_sizes)
        #to set up the sizes of the top-lvel and internal hash tables 

    def _initialize_table_sizes(self, sizes, internal_sizes):
        if sizes is None:
            self.sizes = self.TABLE_SIZES
        else:
            self.sizes = sizes
        # checks if sizes are provided for hash table (sizes) 
       

        if internal_sizes is None:
            self.internal.sizes = self.TABLE_SIZES
        else:
            self.internal_sizes = internal_sizes
        # and the internal hash tables (internal_sizes)

        #if size are not given then it uses TABLE_SIZE (predefined sizes)

        self.top_level_table = LinearProbeTable(self.sizes[self.table_size])
        #initialises 'top_level_table as new LinearProbeTable 
        #with size from sizes and current table_size index

        self.table_size += 1 
        #incrementing the index for the sizes list to prepare it for next initialisation 
        # with different size from sizes list??



    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        #this initialised 'value' is used to accumulate hash value 
        #as characters from 'key' processed

        a = 31415
        #value is used in hash calculation as multiplier 

        for char in key:
        #creates loop that iterates over each character 
        # in the input key.
            value = (ord(char) + a * value) % self.table_size
        # within the loop it calculates the new value of value using the formula
        #by adding the code point of the character to a times the current value.
            a = a * self.HASH_BASE % (self.table_size - 1)
        #updates the value of a for the next iteration.
        #helps in creating a different hash value for each character in the key???
        return value
        #represents the hash value for the input key1.

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
        """
        top_level_index = self.hash1(key1) 
        #calculates the has index for key1 using hash1
        #tells us the intial position in the top-level hash table

        if top_level_index >= self.table_size:
            #checks if top_level_index is within bounds 
            # of available top-level hash tables 
            # if index is greater than or equal to current number of top-lvl tables
            # it means data structure needs to be expanded
            if not is_insert:
                raise KeyError("Pair not found")
            #if operation is not an insertion
            else:
                self._create_internal_table(top_level_index)
            #if it is insertion, it creates a new hash table  at the calculated to_level_index
            #first time the pair with key1 is being inserted 
            #corresponding internal table needs to be created??


        internal_table = self.internal_tables[top_level_index]
        internal_index = self.hash2(key2, internal_table)
        #retrieves internal hash table associated with the calculated top_level_index
        #this internal table is where actual key-value pair is tored/retirved

        return top_level_index, internal_index
        #returns tuple?? of two values??
        #these indices are used to access or manipulate key-value pair
        
    def _create_internal_table(self, top_level_index: int) -> None:
        # integer representing the index where internal hash table should insert 
        # within internal_table array
        #corresponds to top-level key
        internal_size = self.internal_sizes[top_level_index]
        # retrieves the size of the internal hash table based on top_level_index
        # uses internal sizes to tell the size for specified top level key
        # size indicates how many slots the internal hash table should have.
        new_internal_table = LinearProbeTable(internal_size, self.hash2)
        # new instance of the LinearProbeTable class is created as new_internal_table.
        # internal hash table is initialized with the determined internal_size
        # hash2 method (used for hashing the second key) is passed as the hash function for this table.
        self.internal_tables.insert_at_index(top_level_index, new_internal_table)
        # newly created internal hash table (new_internal_table) is inserted 
        # at the specified top_level_index within the internal_tables array.

    def iter_keys(self, key:K1|None=None) -> Iterator[K1|K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        if key is None:
            for top_level_key in self.top_level_table.keys():
                yield top_level_key
        else:
            top_level_index = self.hash1(key)
            if top_level_index < self.table_size:
                internal_table = self.internal_tables[top_level_index]
                for internal_key in internal_table.keys():
                    yield internal_key

    # provides an iterator that can be used to iterate 
    # through either all top-level keys in the hash table
    # or keys within a specific internal hash table
    # based on the value of the key parameter.

    def keys(self, key:K1|None=None) -> list[K1|K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        return list(self.iter_keys(key))

    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        if key is None:
            for top_level_key in self.top_level_table.keys():
                for internal_key in self.iter_keys(top_level_key):
                    yield self[top_level_key, internal_key]
        else:
            top_level_index = self.hash1(key)
            if top_level_index < self.table_size:
                internal_table = self.internal_tables[top_level_index]
                for internal_key in internal_table.keys():
                    yield self[key, internal_key]
        # iterator that can be used to iterate through either all values in the hash table 
        # or values within a specific internal hash table 
        # associated with a top-level key based on the value of the key parameter
    
    def values(self, key:K1|None=None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        return list(self.iter_values(key))

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
        """
        top_level_key, internal_key = key
        top_level_index, internal_index = self._linear_probe(top_level_key, internal_key, False)
        return self.internal_tables[top_level_index][internal_index]

    # retrieve the value associated with a specific key pair 
    # and it handles error cases by raising a KeyError when the key pair is not found 

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """

        top_level_key, internal_key = key
        top_level_index, internal_index = self._linear_probe(top_level_key, internal_key, True)
        self.internal_tables[top_level_index][internal_index] = data

        if len(self) > self.table_size / 2:
            self._rehash()
    #inserts a key-value pair into the double hash table
    # ensures that the load factor is within an acceptable range
    # and performs rehashing when necessary 

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        top_level_key, internal_key = key
        top_level_index, internal_index = self._linear_probe(top_level_key, internal_key, False)
        del self.internal_tables[top_level_index][internal_index]

        if len(self.internal_tables[top_level_index]) == 0:
            self.internal_tables[top_level_index] = None

        if all(internal_table is None for internal_table in self.internal_tables):
            self.table_size = 0
        # ensures proper deletion of a key-value pair from the double hash table 
        # while also managing the internal structure and table size 
        # raises a KeyError if the specified key does not exist in the hash table.
            
    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_internal_tables = self.internal_tables
        old_table_size = self.table_size
        self.internal_tables = ArrayR()
        self.table_size = 0
        self._initialize_table_sizes(self.sizes, self.internal_sizes)

        for old_internal_table in old_internal_tables:
            if old_internal_table is not None:
                for key, value in old_internal_table:
                    self[key, key] = value

        # code is responsible for resizing and rehashing the double hash table 
        # to ensure it remains efficient as it grows in size
        # ensures that all values are correctly reinserted into the resized hash table
        # takes into acc best and worst scenarios ???

    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return len(self.top.level_table)
    # a way to retrieve the size of the top-level hash table 
    # in the double hash table structure
    # represents the number of available slots for storing key-value pairs 
   
    
    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return sum(len(internal_table) if internal_table is not None else 0 for internal_table in self.internal_tables)
    #calculates the total number of elements in the double hash table 
    # by summing the lengths of all internal hash tables
    # considering that some internal tables may be None
    # provides the count of key-value pairs stored in the double hash table.
        """run
        String representation.

        Not required but may be a good testing tool.
        """
    def __str__(self) -> str:
        result = ""
        for top_level_key in self.top_level_table.keys():
            result += f"Top-level key: {top_level_key}\n"
            for internal_key in self.iter_keys(top_level_key):
                result += f"  Internal key: {internal_key}, Value: {self[top_level_key, internal_key]}\n"
        return result
    #generates representation of the double hash table 
    # by iterating through its top-level 
    # and internal keys and values 
    # and formatting them for display




