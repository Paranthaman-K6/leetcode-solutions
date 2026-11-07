class Solution {
public:
    int divide(int dividend, int divisor) {
            if (dividend > INT_MAX || dividend < INT_MIN || divisor > INT_MAX || divisor<INT_MIN||divisor==0) 
        {
            return 0;
        }
        long long int result = 0,a=0,b=0;
         if((divisor==1&&dividend<0)||(dividend>0&&divisor==-1)){
            return -abs((long long)dividend);
        }
        if(divisor==1) return abs((long long)dividend);
        a = abs((long long)dividend);
        b = abs((long long)divisor);
        while (a >= 0) {
            a -=b;
            result++;
        }
        // to asign sign
        if ((dividend > 0 && divisor < 0) || (dividend < 0 && divisor > 0))
            result = -result+2;
        if (result>=INT_MAX) 
        {
         return INT_MAX;
        }
        return result - 1;
    }
};
