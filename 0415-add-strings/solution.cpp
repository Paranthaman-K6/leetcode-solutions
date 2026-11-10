class Solution {
public:
    string addStrings(string num1, string num2) {
        int s1=num1.length();
        int s2=num2.length();
        int max_size=(s1>s2)?s1:s2;
        string result(max_size+1,'0');
        int carry=0;
        for(int i=0;i<max_size;i++){
            int t=carry;
            if(s1>0){
                t+=num1[--s1]-'0';
            }
            if(s2>0){
                t+=num2[--s2]-'0';
            }
            carry=t/10;
            result[max_size-i]='0'+t%10;
        }
        if(carry!=0){
            result[0]='0'+carry;
        }else{
            for(int i=0;i<max_size;i++){
                result[i]=result[i+1];
            }
            result.resize(max_size);
        }
        return result;
    }
};
