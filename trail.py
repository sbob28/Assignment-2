from __future__ import annotations
from dataclasses import dataclass

from mountain import Mountain
from data_structures.linked_stack import LinkedStack


from typing import TYPE_CHECKING, Union

# Avoid circular imports for typing.
if TYPE_CHECKING:
   from personality import WalkerPersonality

@dataclass
class TrailSplit:
    """
    A split in the trail.
       _____top______
      /              \
    -<                >-following-
      \____bottom____/
    """

    top: Trail
    bottom: Trail
    following: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        return TrailSeries(self.following.store.mountain, self.following.store.following)

@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--

    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Removing the mountain at the beginning of this series.
        """
        return Trail(TrailSeries(None, self.following))

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain in series before the current one.
        """
        new_following_trail = Trail(TrailSeries(self.mountain, self.following))
        return TrailSeries(mountain, new_following_trail)

    def add_empty_branch_before(self) -> TrailStore:
        """Returns a *new* trail which would be the result of:
        Adding an empty branch, where the current trailstore is now the following path.
        """
        new_following_trail = Trail(TrailSeries(self.mountain, self.following))
        return TrailSplit(Trail(None), Trail(None), new_following_trail)

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain after the current mountain, but before the following trail.
        """
        new_following_trail = Trail(TrailSeries(mountain, self.following))
        return TrailSeries(self.mountain, new_following_trail)

    def add_empty_branch_after(self) -> TrailStore:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch after the current mountain, but before the following trail.
        """
        new_following_trail = Trail(TrailSplit(Trail(None), Trail(None), self.following))
        return TrailSeries(self.mountain, new_following_trail)


TrailStore = Union[TrailSplit, TrailSeries, None]

@dataclass
class Trail:

    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding a mountain before everything currently in the trail.
        """               
        return Trail(TrailSeries(mountain, self))

    def add_empty_branch_before(self) -> Trail:
        """
        Returns a *new* trail which would be the result of:
        Adding an empty branch before everything currently in the trail.
        """
        return Trail(TrailSplit(Trail(), Trail(), Trail()))

    def follow_path(self, personality: WalkerPersonality) -> None:
        """Follow a path and add mountains according to a personality.
        Complexity:
        Best case: O(1) when first element doe not match any conditions
        Worst case: O(n) where n is the total number of trails, in the path, as each element is processed."""
        current_trail = LinkedStack()
        current_trail.push(self.store)

        while current_trail:
            current = current_trail.pop()

            if isinstance(current, TrailSplit):
                decision = personality.select_branch(current.top, current.bottom).name
                current_trail.push(current.following.store)

                if decision == "TOP":
                    current_trail.push(current.top.store)
                elif decision == "BOTTOM":
                    current_trail.push(current.bottom.store)
                else:
                    return

            elif isinstance(current, TrailSeries):
                personality.add_mountain(current.mountain)
                current_trail.push(current.following.store)


    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        collected_mountains = []
        stack = LinkedStack()

        stack.push(self)  

        while not stack.is_empty():
            current_trail = stack.pop()

            if isinstance(current_trail.store, TrailSeries):
                collected_mountains.append(current_trail.store.mountain)
                if current_trail.store.following:
                    stack.push(current_trail.store.following)  
            elif isinstance(current_trail.store, TrailSplit):
                if current_trail.store.top:
                    stack.push(current_trail.store.top)
                if current_trail.store.bottom:
                    stack.push(current_trail.store.bottom)  
                if current_trail.store.following:
                    stack.push(current_trail.store.following)  

        return collected_mountains

    def difficulty_maximum_paths(self, max_difficulty: int) -> list[list[Mountain]]:
        all_paths = []
        stack = [(self, [], max_difficulty)]

        while stack:
            trail, current_path, remaining_difficulty = stack.pop()

            if not trail:
                all_paths.append(current_path)
                continue

            if isinstance(trail.store, TrailSeries):
                if trail.store.mountain.difficulty_level <= remaining_difficulty:
                    new_difficulty = remaining_difficulty - trail.store.mountain.difficulty_level
                    stack.append((trail.store.following, current_path + [trail.store.mountain], new_difficulty))
                
                if trail.store.following:
                    stack.append((trail.store.following, current_path, remaining_difficulty))
            elif isinstance(trail.store, TrailSplit):
                for next_trail in [trail.store.top, trail.store.bottom, trail.store.following]:
                    stack.append((next_trail, current_path[:], remaining_difficulty))

        return all_paths

    def difficulty_difference_paths(self, max_difference: int) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        # 1054 ONLY!
        raise NotImplementedError()