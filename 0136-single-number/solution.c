int singleNumber(int* nums, int numsSize) {
    int x=0;
    for(int i=0;i<numsSize;i++){
        for(int j=0;j<numsSize;j++){
            if(i!=j&&nums[i]==nums[j]) break;
            if(j+1==numsSize) return nums[i];
        } 
    }
    return 0;
}
