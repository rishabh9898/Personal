
class Solution:
    def sortedListToBST(self, head: Optional[List[int]]) -> Optional[TreeNode]:
        # Helper function to find the middle node
        def find_middle(start, end):
            slow, fast = start, start
            while fast != end and fast.next != end:
                slow = slow.next
                fast = fast.next.next
            return slow

        # Helper function to recursively build the tree
        def build_tree(start, end):
            if start == end:
                return None

            mid = find_middle(start, end)
            root = TreeNode(mid.val)
            root.left = build_tree(start, mid)  # Left subtree
            root.right = build_tree(mid.next, end)  # Right subtree
            return root

        return build_tree(head, None)
