int lengthOfLongestSubstring(char* s) {
    if(strlen(s)==0) return 0;
    int len=0,st=0,i=0;
    for(i=0;s[i]!='\0';i++){
        for(int j=st;j<i;j++){
            if(s[i]==s[j]){
                st=j+1;
            } 
        }
        if((i-st+1)>len)//find long
        len=i-st+1;
        if(len+st>strlen(s)) return len;
    }
    return len;
}
