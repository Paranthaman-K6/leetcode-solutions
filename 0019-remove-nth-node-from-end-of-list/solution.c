/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* removeNthFromEnd(struct ListNode* head, int n) {
    if (head == NULL)
        return NULL;
    int size = 0;
    struct ListNode* t = head;
    while (t->next != NULL) {
        size++;
        t = t->next;
    }
    n = size+1 - n;
    if (n < 0) {
        return head;
    } else if (n == 0) {
        t=head->next;
        free(head);
        head=t;
    } else {
        struct ListNode* t1 = head;
        for (int i = 0; i < n ; i++) {
            t = t1;
            t1 = t1->next;
        }
        t->next = t1->next;
        free(t1);
    }
    return head;
}
