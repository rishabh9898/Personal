
class Solution:
    def sortedListToBST(self, head: Optional[List[int]]) -> Optional[TreeNode]:
        # Helper function to find the middle node

        def middle(st,end):
            slow = st
            fast = st

            while fast!=end and fast.next!=end:
                slow = slow.next
                fast = fast.next.next
            
            return slow
        

        def rec(st,end):
            if st == end:
                return None
            
            mid = middle(st,end)
            root = TreeNode(mid.val)
            root.left = rec(st,mid)
            root.right = rec(mid.next,end)

            return root

        return rec(head,None)
