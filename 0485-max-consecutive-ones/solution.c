int findMaxConsecutiveOnes(int* nums, int numsSize) {
   int ml=0,temp=0;
   for(int i=0;i<numsSize;i++){
        if(nums[i]==1) temp++;
        else temp=0;
        if(temp>ml) ml=temp;
   } 
   return ml;
}
