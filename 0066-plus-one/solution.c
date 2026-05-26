/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
int* plusOne(int* digits, int digitsSize, int* returnSize) {
    if (digitsSize == 0) {
        *returnSize = 0;
        return NULL;
    }
    if (digits[digitsSize - 1] < 9) {
        int* arr = malloc(sizeof(int) * digitsSize);
        for (int i = 0; i < digitsSize; i++)
            arr[i] = digits[i];
        arr[digitsSize - 1]++;
        *returnSize = digitsSize;
        return arr;
    }
    int ext = 0, i = 0;
    for (int i = digitsSize - 1; i >= 0; i--) {
        if (digits[i] == 9 && i == 0)
            ext++;
        if(digits[i]<9) break;
    }
    int* arr = calloc(ext + digitsSize, sizeof(int));
    i = digitsSize-1;
    while (i >= 0) {
        if (digits[i] == 9) {
            i--;
            continue;
        } else {
            arr[i] = digits[i] + 1;
            i--;
            break;
        }
    }
    if (ext == 0) {
        while (i >= 0) {
            arr[i] = digits[i];
            i--;
        }
        *returnSize = digitsSize;
        return arr;
    }
    arr[0] = 1;
    *returnSize = digitsSize + 1;
    return arr;
}

