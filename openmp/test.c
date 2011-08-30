#include <stdio.h>
#include <omp.h>
#define N 10

int main(int argc, char *argv[])
{
    int i, a[N];

    omp_set_num_threads(5);

    #pragma omp parallel for
    for (i=0; i < N; i++) {
        //a[i] = 2 * i;
        a[i] = omp_get_thread_num();
    }

    #pragma omp barrier
    for (i=0; i< N; i++) {
        printf( "%d\n", a[i] );
    }

    return 0;
}

