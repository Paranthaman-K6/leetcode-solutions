int reverse(int x){
    long int rev = 0;
    do
    {
        rev =(rev* 10)+(x % 10);
    } while (x /=10);
    if(INT_MIN>rev||rev> INT_MAX) return 0;
    return rev;
}
