from typing import Callable, Hashable, Generator, Iterable

class FibHeap:

    class Node:
        def __init__(self, Id, key):
            self.parent = None
            self.child = None
            self.prev_sibling = None
            self.next_sibling = None
            self.key = key
            self.is_loser = False
            self.degree = 0
            self.Id = Id

    #---------------------------------------------
    # The main functions (push, decreasekey, popmin) are presented as
    #     push(x), decreasekey(x), x = popmin()
    # where x is any old object. For this to work, the FibHeap needs to be able
    # to lookup two ways: (1) given x find its FibHeap.Node in the heap,
    # (2) given a FibHeap.Node, find its x.
    # We could assume that every object x has an identity Id, and store two
    # hashtables {Id: x} and {Id: FibHeap.Node}.
    # If we have a sensible set of vertex labels to use, this makes sense.
    # But in Python, an arbitrary object x already has an identity id(x),
    # and so you can use an arbitrary object as the lookup key for a hashtable.
    # So we don't actually need the first hashtable, and the second hashtable
    # is really {x: FibHeap.Node}. (We will still keep a set of all the x that
    # we're storing, so that it's fast to find out whether or not the
    # FibHeap contains a given element x. This will save iterating over the entire heap.)
    #
    # We define these main functions here, but the real work is done by
    # internal implementations _push, _decreasedkey, and _popmin,
    # which only care about FibHeap.Node, not about values and identities and so on.

    def __init__(self, xs: Iterable[Hashable]=None, *, sortkey: Callable[[Hashable],float]):
        # This cunning syntax allows it to be called either as FibHeap(sortkey=f) or FibHeap(xs, sortkey=f)
        self.nodes = {}
        self.values = set()
        self.minroot = None
        self.keyfunc = sortkey
        if xs is not None:
            for x in xs:
                self.push(x)

    def push(self, x: Hashable) -> None:
        if x in self.values:
            raise IndexError(x)
        self.values.add(x)
        n = FibHeap.Node(Id=x, key=self.keyfunc(x))
        self.nodes[x] = n
        self._push(n)

    def decreasekey(self, x: Hashable) -> None:
        n = self.nodes[x]  # raises IndexError if missing
        n.key = self.keyfunc(x)
        self._decreasedkey(n)

    def popmin(self) -> Hashable:
        n = self._popmin()
        x = n.Id
        del self.nodes[x]
        self.values.remove(x)
        return x

    def __bool__(self) -> bool:
        # For a Python collection, the usual way to test if it's
        # nonempty is to cast it to a bool. For example, "x=[1,2,3]; if x: ..."
        return (self.minroot is not None)

    def is_empty(self) -> bool:
        return not bool(self)

    def __contains__(self, x: Hashable) -> bool:
        # For a Python collection, to test if it contains an element, "if x in mylist".
        # We can support this usage by defining a __contains__ method.
        return (x in self.values)
    
        
    #---------------------------------------------
    # The internal implementations (_push, _decreasekey, _popmin) work on nodes,
    #     _push(node), _decreasekey(node), node = _popmin()
    # They only deal with FibHeap nodes, and they don't assume any sort of hashtable.
    # (But they do use/modify FibHeap.minroot, so they're not static methods.)
    
    def _push(self, n: 'FibHeap.Node'):
        # If this is the first node in the heap, just stick it in
        # Otherwise, splice it in just after minroot
        if self.minroot is None:
            (n.prev_sibling, n.next_sibling) = (n,n)
            self.minroot = n
        else:
            self._add_sibling(self.minroot, n, n)
            if n.key < self.minroot.key:
                self.minroot = n

    def _decreasedkey(self, n: 'FibHeap.Node'):
        # (Assumes that n.key has just been decreased.)
        # If we can decrease in-place, that's it (apart from updating minroot if needed).
        if n.parent is None:
            if n.key < self.minroot.key:
                self.minroot = n
        elif n.key >= n.parent.key:
            pass
        # Otherwise, walk up the tree, dumping node into rootlist
        else:
            while n.parent is not None:
                self._make_orphan(n)
                u = n.parent
                (n.parent, n.is_loser) = (None, False)
                self._add_sibling(self.minroot, n, n)
                if n.key < self.minroot.key:
                    self.minroot = n
                # If n's parent is a root node, stop
                if u.parent is None:
                    break
                # If n's parent is not a loser, mark it a loser then stop
                if not u.is_loser:
                    u.is_loser = True
                    break
                n = u
                
    def _popmin(self) -> 'FibHeap.Node':
        if self.minroot is None:
            raise IndexError("popmin from empty heap")
        res = self.minroot
        # Let u -- minroot -- v
        # If minroot is the only node in the heap, nothing much to do
        u,v = (self.minroot.prev_sibling, self.minroot.next_sibling)
        if u == self.minroot and self.minroot.child is None:
            self.minroot = None
            return res
        # Else splice out minroot and promote any children
        if self.minroot.child is not None:
            for t in FibHeap._siblings(self.minroot.child):
                t.parent = None
                t.is_loser = False
        if u == self.minroot: # i.e. if this is the only tree
            self.minroot = self.minroot.child
        else:
            (u.next_sibling, v.prev_sibling) = (v,u)
            if self.minroot.child is not None:
                self._add_sibling(u, self.minroot.child, self.minroot.child.prev_sibling)
            self.minroot = u
        # Merge any trees of equal degree
        root_array = {}
        for t in FibHeap._siblings(self.minroot):
            (t.prev_sibling, t.next_sibling) = (t,t)
            x = t
            while x.degree in root_array:
                u = root_array[x.degree]
                del root_array[x.degree]
                x = FibHeap._merge(x, u)
            root_array[x.degree] = x
        # Put them all back into a circular rootlist
        u,v = None,None
        for w in root_array.values():
            if u is None:
                u,v = w,w
            else:
                v.next_sibling = w
                w.prev_sibling = v
                v = w
            if w.key <= self.minroot.key:
                self.minroot = w
        (v.next_sibling, u.prev_sibling) = (u,v)
        # All done!
        return res

    @staticmethod
    def _siblings(n: 'FibHeap.Node') -> Generator['FibHeap.Node', None, None]:
        """Iterate over n's siblings"""
        # Why store next_u? So that I can yield u, and the caller can mess
        # u's siblings fields, and I can still reach (what used to be) next.
        start, u, next_u = (n, n, n.next_sibling)
        yield u
        while next_u != start:
            u, next_u = (next_u, next_u.next_sibling)
            yield u

    @staticmethod
    def _add_sibling(n: 'FibHeap.Node', c: 'FibHeap.Node', d: 'FibHeap.Node') -> None:
        """Splice c-...-d into the sibling list just after n"""
        m = n.next_sibling
        (n.next_sibling, c.prev_sibling) = (c,n)
        (d.next_sibling, m.prev_sibling) = (m,d)

    @staticmethod
    def _merge(x: 'FibHeap.Node', y: 'FibHeap.Node') -> 'FibHeap.Node':
        """Merge two trees and return the result"""
        if x.key > y.key: (x,y) = (y,x)
        x.degree = x.degree + 1
        y.parent = x
        if x.child is None:
            x.child = y
        else:
            FibHeap._add_sibling(x.child, y, y)
        return x
            
    @staticmethod
    def _make_orphan(n: 'FibHeap.Node'):
        (u,v) = (n.prev_sibling, n.next_sibling)
        if v == n: # only child
            n.parent.child = None
            n.parent.degree = 0
        else:
            if n.parent.child == n:
                n.parent.child = v
            n.parent.degree = n.parent.degree - 1
            (u.next_sibling, v.prev_sibling) = (v,u)
        
    #---------------------------------------------
    # Rather intricate pretty-printing routine, to show the trees as in lectures
    # (but rotated 90 degrees anticlockwise)

    def __str__(self) -> str:
        if self.minroot is None:
            return "Empty heap"
        res = '\n'.join(self._nodestr(c) for c in FibHeap._siblings(self.minroot))
        res = ['.'] + ['|'+r for r in res.splitlines()] + ["'"]
        return '\n'.join(res)

    def _nodestr(self, n: 'FibHeap.Node') -> str:
        self_str = f'{n.Id}({n.key})'
        if n.is_loser: self_str = '{'+self_str+'}'
        if n.child is None:
            return self_str
        res = []
        cs = [self._nodestr(c) for c in FibHeap._siblings(n.child)]
        imax = len(cs) - 1
        for i,c in enumerate(cs):
            ls = c.splitlines()
            jmax = len(ls) - 1
            for j,l in enumerate(ls):
                if j>0 and i==imax:
                    pipe = ' '
                elif j>0:
                    pipe = '|'
                elif imax==0:
                    pipe = '-'
                elif i<imax:
                    pipe = '+'
                else:
                    pipe = '\\'
                r = self_str if i==0 and j==0 else ' '*len(self_str)
                res.append(r + pipe + l)
        return '\n'.join(res)
   