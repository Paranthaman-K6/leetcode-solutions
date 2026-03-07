double findMedianSortedArrays(int* nums1, int nums1Size, int* nums2, int nums2Size) {
    int i=nums1Size+nums2Size,temp[i],m=0,o=0;
    for(int j=0;j<i;j++){
        if(m<nums1Size&&o<nums2Size)
        temp[j]=(nums1[m]>nums2[o])?nums2[o++]:nums1[m++];
        else if(m<nums1Size) temp[j]=nums1[m++];
        else temp[j]=nums2[o++];
    }
    if(i%2==1) return temp[i/2];
    else return (double)(temp[i/2-1]+temp[i/2])/2;
}
