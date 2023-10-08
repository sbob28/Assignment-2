from __future__ import annotations

from mountain import Mountain
from algorithms.mergesort import mergesort


class MountainOrganiser:

    def __init__(self) -> None:
        """Best case time complexity: O(1), initialization of an empty list is a constant time operation.
        Worst case time complexity: O(1), also constant since it doesn't depend on the size of the list."""
        self.mountains = []


    def cur_position(self, mountain: Mountain) -> int:
        """Best case time complexity: O(1)
    # occurs when the mountain is found at the beginning of the list
    # resulting in constant time.

    # Worst case time complexity: O(n)
    # occurs when the mountain is not in the list or is located at the end
    # resulting in a linear search through all elements """
        for position, current_mountain in enumerate(self.mountains):
            if current_mountain == mountain:
                return position
        raise KeyError("Mountain not found")
   


    def add_mountains(self, mountains: list[Mountain]) -> None:
       """ Best and worst case time complexity: O(n log n)
       #  because it divides the list into halves (logarithmic divisions)
       # and efficiently merges them (linear time),
       # divide-and-conquer approach."""
       for mountain in mountains:
           self.mountains.append(mountain)
       self.mountains = mergesort(self.mountains, key=lambda x: (x.difficulty_level, x.name))