from typing import List

class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:

        # Create a graph to map each course to its prerequisites
        graph = {i: [] for i in range(numCourses)}
        for course, prereq in prerequisites:
            graph[course].append(prereq)

        courseOrder = []  # To store the order of courses to be taken
        visited = set()   # To detect cycles
        processed = set() # To store fully processed nodes

        def dfs(course):
            if course in visited:
                return False  # Cycle detected
            if course in processed:
                return True   # Already processed successfully

            # Mark the course as visiting
            visited.add(course)

            # Visit all prerequisites
            for prereq in graph[course]:
                if not dfs(prereq):
                    return False

            # Mark the course as processed
            visited.remove(course)
            processed.add(course)
            courseOrder.append(course)

            return True

        # Perform DFS for each course
        for i in range(numCourses):
            if not dfs(i):
                return []

        # Return the reverse of the order to get the correct topological sort
        return courseOrder
