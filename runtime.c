#include <stdio.h>

#define BOOL_F 0x2F
#define BOOL_T 0x6F
#define FIXNUM_MASK 0x03
#define FIXNUM_TAG 0x00
#define FIXNUM_SHIFT 2
#define CHAR_MASK 0x0F
#define CHAR_SHIFT 8
#define NIL 0x3F

extern int scheme_entry();
typedef unsigned int ptr;


static void print_ptr(ptr x)
{
    if((x & FIXNUM_MASK) == FIXNUM_TAG)
    {
        printf("%d", ((int)x) >> FIXNUM_SHIFT);
    }
    else if(x == BOOL_T)
    {
        printf("#t");
    }
    else if(x == BOOL_F)
    {
        printf("#f");
    }
    else if ((x & 0xFF) == CHAR_MASK)
    {
        printf("#\\%c", ((int)x) >> CHAR_SHIFT);
    }
    else if (x == NIL)
    {
        printf("()");
    }
    else
    {
        printf("#<unknown 0x%08x>", x);
    }
    printf("\n");
}


int main(int argc, char **argv)
{
    print_ptr(scheme_entry());
    return 0;
}
