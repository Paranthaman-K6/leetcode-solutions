

char * mergeAlternately(char * word1, char * word2){
    char *str=malloc(strlen(word1)+strlen(word2)+1);
    int i=0,j=0,k=0;
    while(word1[i]!='\0'&&word2[k]!='\0'){
        str[j++]=word1[i++];
        str[j++]=word2[k++];
    }
    while(word1[i]!='\0') str[j++]=word1[i++];
    while(word2[k]!='\0') str[j++]=word2[k++];
    str[j]='\0';
    return str;
}
