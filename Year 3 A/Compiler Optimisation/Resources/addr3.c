/* The following routine cg_expr() is a simple generator of 3-address   */
/* code instructions from a parser tree.  It takes as argument an       */
/* (Expr *) and calls emitc/emitv/emitr to output 3-address             */
/* instructions.                                                        */

typedef enum { s_integer, s_variable, s_neg,
               s_plus, s_minus, s_times, s_divide } OpSort;

typedef struct Expr
{    OpSort op;
     union
     {   int cnst;
         char *var;
         struct Expr *monad;
         struct { struct Expr *left, *right; } diad;
    } u;
} Expr;

typedef int Reg;

static Reg next = 0;

static Reg nextreg() { return ++next; }

extern void emitc(OpSort op, Reg r1, int cnst);
extern void emitv(OpSort op, Reg r1, char *var);
extern void emitr(OpSort op, Reg r1, Reg r2, Reg r3);
extern void syserr(char *reason);

Reg cg_expr(Expr *e)
{   Reg r = nextreg();
    OpSort op = e->op;
    switch (op)
    {
default:        syserr("unexpected op");
case s_integer: emitc(op, r, e->u.cnst);
                break;
case s_variable: emitv(op, r, e->u.var);
                break;
case s_neg:     emitr(op, r, 0, cg_expr(e->u.monad));
                break;
/* The diad case is sloppy in that we allow the C compiler to choose    */
/* whether to calculate the left or right child first; choosing the     */
/* one needing least temporaries first is a better strategy.            */
case s_plus:
case s_times:
case s_minus:
case s_divide:  emitr(op, r, cg_expr(e->u.diad.left),
                             cg_expr(e->u.diad.right));
                break;
    }
    return r;
}

/* Exercise:  consider the code generation of 3*x + y*((-z)-1).         */
