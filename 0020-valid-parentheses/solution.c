bool isValid(char* s) {
    int top=-1,n=strlen(s)/2;char stack[n+1];
for(int i=0;s[i]!='\0';i++){
    if((s[i]=='{'||s[i]=='['||s[i]=='(')&&top+1<n) stack[++top]=s[i];
    else if(top==-1) return false;
    else if(s[i]==')'&&stack[top]=='('||
            s[i]==']'&&stack[top]=='['||
            s[i]=='}'&&stack[top]=='{') top--;
    else return false;
    }
    if(top==-1) return true;
    return false;
}
