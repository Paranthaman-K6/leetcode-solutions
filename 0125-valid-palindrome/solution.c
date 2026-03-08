bool isPalindrome(char* s) {
    int n=0;
    char temp[strlen(s)+1];
    for(int i=0;s[i]!='\0';i++)
        if(isalnum(s[i]))
            temp[n++]=tolower(s[i]);
    temp[n]='\0';
    for(int i=0;i<n;i++)
        if(temp[i]!=temp[n-i-1]) return false;
    return true;
}
