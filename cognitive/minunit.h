#define mu_assert(message_fail, message_succ, test) do { if (!(test)) return message_fail; else { printf("[%02d] ",tests_run+1 ); printf(message_succ); printf("\n"); } } while(0)
#define mu_run_test(test) do { char * message = test(); tests_run++; if (message) return message; } while(0)

extern int tests_run;

