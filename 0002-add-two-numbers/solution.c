/*
  struct ListNode {
      int val;
     struct ListNode *next;
 };
*/
struct ListNode* addTwoNumbers(struct ListNode* l1, struct ListNode*  l2){
    int reminder=0,sum=0;struct ListNode *r=NULL,*temp2;
    r=(struct ListNode*)malloc(sizeof(struct ListNode));
    struct ListNode* temp=r;
    while(l1!=NULL||l2!=NULL){
        if(l1==NULL){ 
            sum=l2->val+reminder;
            l2=l2->next;
        }
        else if(l2==NULL) {
            sum=l1->val+reminder;
            l1=l1->next;
        }
        else {
            sum=l1->val+l2->val+reminder;
            l1=l1->next;
            l2=l2->next;
        }
        temp->val=sum%10;
        reminder=sum/10;
        temp->next=(struct ListNode*)malloc(sizeof(struct ListNode));
        temp2=temp;
        temp=temp->next;
    }
    if(reminder>0) {
        temp->val=1;
        temp->next=NULL;
    }
    else{
        free(temp);
        temp2->next=NULL;
    }
    return r;
}
 
