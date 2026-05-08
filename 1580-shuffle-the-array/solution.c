

/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
int* shuffle(int* nums, int numsSize, int n, int* returnSize){
    int *arr=malloc(sizeof(int)*numsSize);
    int k=0;
    for(int i=0;i<n;i++){
        arr[k]=nums[i];
        arr[++k]=nums[n+i];
        k++;
    }
    *returnSize=numsSize;
    return arr;
}
