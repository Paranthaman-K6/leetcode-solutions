class Solution {
    public int[] twoSum(int[] nums, int target) {
        int i,j;
        for(i=0;i<nums.length;i++){
            int a;
            a=target-nums[i];
            for(j=i+1;j<nums.length;j++){
                if(a==nums[j]) return new int[]{i,j};
            }
        }
        return new int[]{};
    }
}
