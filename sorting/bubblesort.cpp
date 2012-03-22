#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void bubblesort(int* array, int length)
{
    int i, j;
    for (i = 0; i < length - 1; ++i) {
       for (j = 0; j < length - i - 1; ++j) {
           if (array[j] > array[j + 1]) {
               int tmp = array[j];
               array[j] = array[j + 1];
               array[j + 1] = tmp;
           }
       }
    }
}

int main(int argc, const char** argv)
{
    FILE *f = fopen(argv[1], "r");
    int size, i, j;
    int *array, *array2;
    i = 0;
    while (i == 0) {
        i = fread(&size, sizeof(int), 1, f);
        printf("i: %d\n", i);
    }
    printf("size: %d\n", size);
    array = (int*)malloc(size * sizeof(int));
    i = size;
    while (i > 0) {
        j = fread(array, sizeof(int), i, f);
        i -= j;
    }

    //array2 = (int*)malloc(size * sizeof(int));
    printf("Sorting %d data points...\n", size);
    //for (i=0; i < 5; ++i) {
        //memcpy(array2, array, size * sizeof(int));
        //bubblesort(array2, size);
        bubblesort(array, size);
    //}

    //for (i=0; i < size; ++i) {
    //    printf("%d\n", array[i]);
    //}

    return 0;
}

