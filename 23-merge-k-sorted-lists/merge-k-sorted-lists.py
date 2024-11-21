# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:

        if not lists:
            return None


        def mergeList(l1,l2):

            dummy = ListNode()
            tail = dummy

            while l1 and l2:
                if l1.val < l2.val:
                    tail.next = l1
                    l1 = l1.next
                else:
                    tail.next = l2
                    l2 = l2.next
                    
                tail = tail.next
            
            if l1:
                tail.next = l1
            if l2:
                tail.next = l2

            return dummy.next
        
        while len(lists)>1:
            merged = []

            for i in range(0,len(lists),2):
                l1 = lists[i]

                if i+1 <len(lists):
                    merged.append(mergeList(lists[i],lists[i+1]))
                else:
                    merged.append(l1)

            lists = merged

        return lists[0]

        

        
        