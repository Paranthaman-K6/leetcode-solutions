class Solution {
    public int removeElement(int[] nums, int val) {
        int varlen=nums.length;
        for(int i=0;i<varlen;i++){
            if(nums[i]==val){
                for(int j=i;j<varlen-1;j++){
                    nums[j]=nums[j+1];
                }
                if(nums[i]==val) i--;
                varlen--;
            }
        }
        return varlen;
    }
}
