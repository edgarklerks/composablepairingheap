from hypothesis import *
import data.composablepairingheap as c
import data.optional as o
import random as r
import hypothesis.settings as hs
from hypothesis.database.backend import SQLiteBackend
from hypothesis.database import ExampleDatabase

# The reference identity is like the pointer identity,
# it will reflect that two references are really pointing to the same instance of an object.

def referenceIdentity(a,b):
    return id(a) == id(b)

# A usage example
def example():
    h = c.HashTable()
    t = c.Coobject(h)
    p = c.PairingHeap(coobject=t)
    p.insert(5)
    p.insert(2)
    p.insert(7)
    p.insert(4)
    p.insert(6)
    p.insert(3)
    t.delete(2)
    t.delete(5)
    return (t,p)

def createHeapWithHashTable():
    h = c.HashTable()
    t = c.Coobject(h)
    p = c.PairingHeap(coobject=t)
    return (t,p)

# Create an list with only unique elements
def uniqlist(xs):
    ss = set(xs)
    ts = list(ss)
    sorted(xs)
    return ts == xs

# Select a random subset of a list of something
def randomSubset(xs,count):
    ys = set()
    for _ in xrange(0,count):
        c = r.randrange(0, len(xs))
        ys.add(xs[c])
    return list(ys)



class HeapTestExceptions(Exception):
    pass

class NotEquivalentException(HeapTestExceptions):
    pass

class EquivalentException(HeapTestExceptions):
    pass

class NotInContainer(HeapTestExceptions):
    pass

class UnorderedException(HeapTestExceptions):
    pass

def negateEquiv(meth, k,v,n,msg):
    try:
        meth(k,v,n)
    except NotEquivalentException:
        return True

    raise EquivalentException(msg)



# Show that the value of two nodes are the same
def equivValue(k,v,n):
    return n.node.value == k and v.node.value == k


def equivPhkv(k,v,n):
    """
    Checks if two values are the same and implicitly checks if id actually checks if two variables
    point to an object at the same memory location
    """
    return equivValue(k,v,n) and referenceIdentity(n,v) and referenceIdentity(n.node,v.node)

def checkInPh(k,v,ph,head = True):
    """
    Tests if a value is indeed in the pairing heap
    """
    if head:
        if equivPhkv(k,v,ph.node):
            return True
        ph = ph.node
    else:
        if equivPhkv(k,v,ph):
            return True

    if ph.isEmpty:
        return True

    nodes = ph.node.nodes

    for node in nodes:
        if checkInPh(k,v,node,False):
            return True
    if head:
        raise NotInContainer()

def equivalentHt(ht,ph):
    """
    Check if values in the pairing heap are also in the coobject
    """
    def kvinht(obj,res,tp):
        if tp == "PairingHeapWrapper":
            return obj
        elif tp == "EmptyNode":
            return None
        elif tp == "Value":
            if res:
                cobj = ht[obj]
                if not equivPhkv(obj, cobj, res):
                    raise NotEquivalentException()
        else:
            return res
    ph._fold(kvinht, None)





def equivalentPh(ht,ph):
    """
    Check if values in the hashtable are also in the pairing heap and check that none of the objects are null.
    If it is, it means that the hashtable has values, which aren't in the pairing heap anymore.
    """
    for k in ht:
        if k is None:
            raise Exception("Test failed, because None is key in table")
        v = ht[k]
        if v is None:
            raise Exception("Test failed, because None is value in table")
        checkInPh(k,v,ph)

@given([int])
def test_insert_mapping_h_to_q(xs):
    """
    Check if the mapping from the
    hashtable to the queue is a monomorphism.
    """
    assume(uniqlist(xs))
    (ct, ph) = createHeapWithHashTable()
    for x in xs:
        ph.insert(x)
    equivalentHt(ct.coobject.dict, ph)

@given([int])
def test_insert_mapping_q_to_h(xs):
    """
    Check if the mapping from the hashtable to the queue
    is an epimorphism.

    """
    (ct, ph) = createHeapWithHashTable()
    for x in xs:
        ph.insert(x)
    equivalentPh(ct.coobject.dict,ph)

# Found error in checkInPh
@given([int])
def test_delete_mapping_h_to_q(xs):
    """
    Check if the properties of the mapping from the hashtable to the queue
    is preserved under deletion (in this case if it is a monomorphism)
    """
    assume(uniqlist(xs))
    assume(len(xs) > 1)
    c = len(xs) - len(xs)/2
    (ct,ph) = createHeapWithHashTable()
    for x in xs:
         ph.insert(x)
    ys = randomSubset(xs,c)
    for y in ys:
        ct.delete(y)

    equivalentPh(ct.coobject.dict, ph)

@given([int])
def test_delete_mapping_q_to_h(xs):
    """
    Check if the properties of the mapping from the hashtable to the queue
    is preserved under deletion (in this case if it is an epimorphism)
    This test will be rather slow, because we are walking over the whole tree
    """
    assume(uniqlist(xs))
    assume(len(xs) > 1)
    c = len(xs) - len(xs)/2
    (ct,ph) = createHeapWithHashTable()
    for x in xs:
         ph.insert(x)
    ys = randomSubset(xs,c)
    for y in ys:
        ct.delete(y)

    equivalentHt(ct.coobject.dict, ph)

@given([int])
def test_in_order(xs):
    """
    Check if the elements are stored in the correct order
    """
    (ct, ht) = createHeapWithHashTable()
    for x in xs:
        ht.insert(x)
    xs = sorted(xs)
    if ht.toList() != xs:
        raise UnorderedException()
@given([int])
def test_reversed_order_works_fine(xs):
    q = c.PairingHeap(ordering=lambda a,b: a > b)
    q.fromList(xs)
    xs = sorted(xs)
    xs.reverse()
    if q.toList() != xs:
        raise UnorderedException()

@given([int])
def test_heap_sort_is_ordered(xs):
    if c.PairingHeap.heapSort(xs) != sorted(xs):
        raise UnorderedException()

# Found error in interface definition (fromList was not fluid)
@given([int])
def test_from_to_list_sorts(xs):
    (ct,ht) = createHeapWithHashTable()
    if ht.fromList(xs).toList() != sorted(xs):
        raise UnorderedException()


@given([int])
def test_in_order_under_delete(xs):
    """
    Check if the order is preserved under delete
    """
    assume(uniqlist(xs))
    assume(len(xs) > 1)
    c = len(xs) - len(xs)/2

    (ct, ht) = createHeapWithHashTable()
    for x in xs:
        ht.insert(x)

    ys = randomSubset(xs, c)

    for y in ys:
        ct.delete(y)

    tt = set(xs).difference(set(ys))
    tt = sorted(tt)

    if ht.toList() != tt:
        raise UnorderedException()
