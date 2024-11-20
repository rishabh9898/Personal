# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:

        if not head:
            return head

        totalLen = 1
        dummy = head

        while dummy.next:
            totalLen +=1
            dummy = dummy.next
        
        #  totalLen = 5
        #  finding the no. of rotation needed 

        k = k % totalLen

        if k == 0:
            return head

        #  return the same value
        #  to reach the pivot node, we have to travel to totalLen - k -1 (index)

        curr = head
        for i in range(totalLen-k-1):
            curr = curr.next
        
        #  now curr
        newHead = curr.next
        curr.next = None
        dummy.next = head
        return newHead


        
    



        

            



        