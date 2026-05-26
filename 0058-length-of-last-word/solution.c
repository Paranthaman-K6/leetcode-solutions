int lengthOfLastWord(char* s) {
    int x = -1;
    for (int i = 0; s[i] != '\0'; i++)
        if (s[i] == ' ' && s[i + 1] != '\0'&&s[i+1]!=' ')
            x = i + 1;
    if (x == -1){
        int y=strlen(s)-1;
        while(s[y]==' ') y--;
        return y+1;
        }   
    int size = 0;
    for (int i = x; s[i] != '\0'&&s[i]!=' '; i++)
        size++;
    return size;
}
