#include <stdio.h>

#include <tm.h>
//#include <pbs_ifl.h>

int main(int argc, char *argv)
{
    struct tm_roots roots;

    fflush(stdout);
    int result = tm_init(NULL, &roots);
    printf("success: %d\n", TM_SUCCESS);
    //int result = pbs_connect("ab");
    tm_finalize();

    printf("tm_init: %d\n", result);

    return 0;
}

