/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* rotateRight(struct ListNode* head, int k) {
    if(head==NULL||head->next==NULL) return head;
    int i=0;
    struct ListNode *temp2=head;
    while(temp2!=NULL) {
        temp2=temp2->next;
        i++;
    }
    k=k%i;
    while(k>0){
        struct ListNode *temp1,*temp=head;
        while(temp->next!=NULL){
             temp1=temp;
             temp=temp->next;
        }
        temp1->next=NULL;
        temp->next=head;
        head=temp;
        k--;
    }
    return head;
}
