void rotate(int* nums, int numsSize, int k) {
     k=k%numsSize;
    if(k<=0||numsSize<=1) return;
    int temps[k];
    for(int i=0;i<k;i++) temps[k-1-i]=nums[numsSize-1-i];
    for(int i=0;i<numsSize-k;i++) nums[numsSize-1-i]=nums[numsSize-k-1-i];
    for(int i=0;i<k;i++) nums[i]=temps[i];
}
