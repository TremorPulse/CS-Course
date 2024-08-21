class A {};
class B : public A {};

A **p;
B **q;

void foo() {
  *p = *q;
}
void foo2() {
  p = q;
}
int main() {
  // initialise p and q before calling foo and/or foo2
  return 0;
}
