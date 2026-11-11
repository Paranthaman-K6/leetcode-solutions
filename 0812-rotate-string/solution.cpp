class Solution {
public:
    bool rotateString(string s, string goal) {
        if(s.size()!=goal.size()) return false;
        int n=s.size()-1;
        for(int i=0;i<=n;i++){           //combinator
            char head=s[0];
            for(int j=0;j<n;j++){       //roator by swapping
                s[j]=s[j+1];
            }
            s[n]=head;
            if(s==goal) return true;
        }
        return false;
    }
};
