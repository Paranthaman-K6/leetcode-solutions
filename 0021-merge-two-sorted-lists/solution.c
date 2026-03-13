/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* mergeTwoLists(struct ListNode* list1, struct ListNode* list2) {
    struct ListNode *r,*head=malloc(sizeof(struct ListNode));
    r=head;
    while(list1!=NULL&&list2!=NULL){
        r->next=(struct ListNode*)malloc(sizeof(struct ListNode));
        r=r->next;
        if(list1->val>list2->val){
            r->val=list2->val;
            list2=list2->next;
        }
        else{
            r->val=list1->val;
            list1=list1->next;
        }
    }
    while(list2!=NULL){
        r->next=(struct ListNode*)malloc(sizeof(struct ListNode));
        r=r->next;
        r->val=list2->val;
        list2=list2->next;
    }
    while(list1!=NULL){
        r->next=(struct ListNode*)malloc(sizeof(struct ListNode));
        r=r->next;
        r->val=list1->val;
        list1=list1->next;
    }
    r->next=NULL;
    r=head->next;
    free(head);
    return r;
}
