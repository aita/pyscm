#include <assert.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>

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

static char* allocate_protected_space(int size) {
  int page = getpagesize();
  int status;
  int aligned_size = ((size + page - 1) / page) * page;
  char* p = mmap(0, aligned_size + 2 * page,
                 PROT_READ | PROT_WRITE,
                 MAP_ANONYMOUS | MAP_PRIVATE,
                 0, 0);
  if (p == MAP_FAILED) { perror("map"); exit(1); }
  status = mprotect(p, page, PROT_NONE);
  if (status != 0) { perror("mprotect"); exit(status); }
  status = mprotect(p + page + aligned_size, page, PROT_NONE);
  if (status != 0) { perror("mprotect"); exit(status); }
  return (p + page);
}

static void deallocate_protected_space(char* p, int size) {
  int page = getpagesize();
  int status;
  int aligned_size = ((size + page - 1) / page) * page;
  status = munmap(p - page, aligned_size + 2 * page);
  if (status != 0) { perror("munmap"); exit(status); }
}

int main(int argc, char **argv)
{
    int stack_size = (16 * 4096);
    char* stack_top = allocate_protected_space(stack_size);
    char* stack_base = stack_top + stack_size;
    print_ptr(scheme_entry(stack_base));
    deallocate_protected_space(stack_top, stack_size);
    return 0;
}
