from __future__ import annotations
from mountain import Mountain

class MountainManager:

    def __init__(self) -> None:
        """ Best and worst case O(1), initializing an empty list is a constant-time operation."""
        self.mountains = []

    def add_mountain(self, mountain: Mountain) -> None:
        """ Best and worst case O(1), appending to a list is a constant-time operation on avg"""
        self.mountains.append(mountain)
       
    def remove_mountain(self, mountain: Mountain) -> None:
        """ Best case O(1)
        # If the mountain to be removed is the first item.

        # worst case O(n)
        # in the case where the mountain is the last item
        # or if checking for membership takes linear time
        # where n is the number of mountains.
        """
        if mountain in self.mountains:
            self.mountains.remove(mountain)
        else:
            raise ValueError("Mountain not found")


    def edit_mountain(self, old_mountain: Mountain, new_mountain: Mountain) -> None:
        """ Best case O(1), If the old mountain is the first item.
        Worst case O(n), If the old mountain is the last item or not in the list."""
        for index, mountain in enumerate(self.mountains):
            if mountain == old_mountain:
                self.mountains[index] = new_mountain
                return
        raise ValueError("Old mountain not found")


    def mountains_with_difficulty(self, diff: int) -> list[Mountain]:
        """best case and worst case O(n)
    # Always iterates through all items in the list."""
        return [mountain for mountain in self.mountains if mountain.difficulty_level == diff]




    def group_by_difficulty(self) -> list[list[Mountain]]:
        """best and worst case O(nlogn)
    # sorting is the dominant operation in this method
    # and sorting has a time complexity of O(nlogn) for n mountains"""
       
        sorted_mountains = sorted(self.mountains, key=lambda mountain: mountain.difficulty_level)
        grouped_mountains = []
        current_group = []

        for mountain in sorted_mountains:
            if not current_group or mountain.difficulty_level == current_group[0].difficulty_level:
                current_group.append(mountain)
            else:
                grouped_mountains.append(current_group)
                current_group = [mountain]

        if current_group:
            grouped_mountains.append(current_group)

        return grouped_mountains