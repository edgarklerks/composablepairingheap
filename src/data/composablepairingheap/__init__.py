from data.optional import Result,NoResult

debug_pq = False

class Coobject(object):
    def __init__(self, coobject):
        self.coobject = coobject

    def insert(self, value, obj):
        if value is not None:
            self.coobject.insert(value, obj)
        return self

    def delete(self, value, heapCaller = False):
        if not heapCaller:
            if self.coobject.exists(value):
                self.coobject.get(value).deleteFirst()
            return self
        else:
            if self.coobject.exists(value):
                self.coobject.delete(value)
            return self





class HashTable(object):
    """
    Bogus implementation of a hash table.
    It shows the interface needed for the coobject object.
    Usage:
    t = Coobject(HashTable)
    p = PairingHeap(coobject=t)
    p.insert(5)
    p.insert(2)
    p.insert(7)
    p.insert(4)
    p.insert(6)
    p.insert(3)
    p.delete(2)
    p.delete(5)
    """
    def __init__(self):
        self.dict = {}

    def insert(self, value, obj, froms=None):
        """
        This has a dirty implication, that the value
        has to be something, which can be injected into
        a dict as a key
        """
        self.dict[value] =  obj

    def delete(self, value):
        del self.dict[value]


    def get(self, value):
        return self.dict[value]

    def exists(self, value):
        return value in self.dict

class PairingHeap(object):
    def __init__(self, ordering = None, coobject = None):
        self.ordering = ordering
        self.coobject = coobject
        self.node = PairingHeapWrapper(self.ordering, self.coobject)

    def _fold(self, method, res=None):
        """
        Fold over the whole structure, useful for integrity
        checks
        """
        res = method(self, res, "PairingHeap")
        return self.node._fold(method, res)

    def insert(self, value):
        self.node = self.node.insert(value)
        return self

    def findFirst(self):
        return self.node.findFirst()

    def deleteFirst(self):
        self.node = self.node.deleteFirst()
        return self

    def fromList(self, xs):
        self.node = self.node.fromList(xs)
        return self

    def toList(self):
        return self.node.toList()

    @staticmethod
    def heapSort(xs):
        return PairingHeap().fromList(xs).toList()

    @property
    def isEmpty(self):
        return self.node.isEmpty



class PairingHeapWrapper(PairingHeap):
    """
    A pairing heap implementation, which supports composition with
    other container types.

    The internal classes are not for
    public use and touching them is in general a bad idea.

    To be able to keep references to a node, we need to pack them into another object, which
    have the same operations, but allows us to modify the inner object,
    otherwise we would have to mutate nodes, which is very ugly.

    The wrapping and unwrapping is very hard  to get right, because of duck typing and
    The nodes need to share behaviour. This is a case, where if it quacks like a duck and
    shits like a duck, but wears a goose skin, we certainly wouldn't like to think it is a
    normal duck.

    Another hard thing is keeping the coobject up to date.

    So I needed to add some identification, that it is actually a duck jacked into a goose skin.
    That is this shit, you are looking at.

    I seemed to have it sealed everywhere.

    """


    # Interface
    def __init__(self, ordering = None, coobject = None):
        """
        Accepts a custom ordering method, which should accept two objects and
        state if one object is smaller or bigger than another object:
        Eg:

        def test(x,y):
           return x > y

        The coobject, also needs an insert method and a delete method, which will be used to
        insert a node or delete a node in the tree.
        """
        ords = ordering or (lambda x,y: x < y)
        self.ordering = ords
        self.coobject = coobject

        self.node = PairingHeapWrapper.EmptyNodeFactory(self.ordering, self.coobject)
    def _fold(self, method, res):
        res = method(self, res, "PairingHeapWrapper")
        return self.node._fold(method, res)

    def storecoobject(self, queue,msg=None):
        if self.coobject:
            self.coobject.insert(queue.findFirst().extract, queue)
            if msg and debug_pq:
                print(self.findFirst().extract, queue.findFirst().extract, self, queue, msg)

    def deletecoobject(self, value,msg=None):
        if self.coobject:
            self.coobject.delete(value, True)
            if msg and debug_pq:
                print(self.findFirst().extract, value, msg)
    @property
    def wrapper(self):
        """
        identify that it is a wrapper.
        """
        return True

    @staticmethod
    def wrapped(node):
        """
        Wrapped, wraps a node into a PairingHeapWrapper
        """
        t = PairingHeapWrapper(coobject=node.coobject, ordering=node.ordering)
        t.node = node
        t.storecoobject(t, "PairingHeapWrapper: wrapped")
        return t


    def singleton(self, value):
        return PairingHeapWrapper.wrapped(PairingHeapWrapper.NodeFactory(self.ordering, value, self.coobject))

    def findFirst(self):
        return self.node.findFirst()

    def merge(self, heap):
        res = heap.node.merge(self)
        self.storecoobject(res, "Node: merge heap after")
        return res

    def insert(self, value):
        return self.merge(self.singleton(value))

    def deleteFirst(self):
        p = self.findFirst()
        if self.coobject:
            self.coobject.delete(p.extract, True)

        self.node = self.node.deleteFirst().node
        self.storecoobject(self, "PairingHeapWrapper: deleteFirst")
        return self

    def fromList(self, xs):
        return reduce(lambda z, x: z.insert(x), xs, self)

    def toList(self):
        """
        A destructive operation
        """
        lst = []
        while(not self.isEmpty):
            lst.append(self.findFirst().extract)
            self.deleteFirst()
        return lst

    @staticmethod
    def EmptyNodeFactory(ordering, coobject):
        return EmptyNode(ordering, coobject)

    @staticmethod
    def NodeFactory(ordering,value, coobject):
       return Node(ordering,value, coobject)

class EmptyNode(PairingHeapWrapper):
    def __init__(self, ordering, coobject):
        self.ordering = ordering
        self.value = None
        self.coobject = coobject
    def _fold(self, method, res):
        return method(self, res, "EmptyNode")



    @property
    def wrapper(self):
        return False

    @property
    def isEmpty(self):
        return True

    def findFirst(self):
        return NoResult()

    def deleteFirst(self):
        return PairingHeapWrapper.wrapped(self)

    def merge(self, queue):
        # print(self.findFirst().extract, queue.findFirst().extract, self, queue, "EmptyNode: merge")
        return queue

class Node(PairingHeapWrapper):
    def __init__(self, ordering, value, coobject):
        self.ordering = ordering
        self.value = value
        self.nodes = []
        self.coobject = coobject
    def _fold(self, method, res):
        res = method(self, res, "Node")
        res = method(self.value, res, "Value")
        for node in self.nodes:
            res = node._fold(method, res)
        return res


    @property
    def wrapper(self):
        return False

    def merge(self, queue):

        if queue.isEmpty:
            res =  PairingHeapWrapper.wrapped(self)
            return res


        elif self.ordering(self.findFirst().extract, queue.findFirst().extract):
            self.nodes.append(queue)
            res =  PairingHeapWrapper.wrapped(self)
            return res
        else:
            queue.node.nodes.append(PairingHeapWrapper.wrapped(self))
            return queue

    def findFirst(self):
        return Result(self.value)

    @property
    def isEmpty(self):
        return False

    def deleteFirst(self):
        def pair(lst):

            lstNew = []
            while(True):
                if not len(lst):
                    return lstNew
                a = lst.pop()
                # Don't worry len is O(1) in python, in every other language it would be a bad idea
                if len(lst):
                    b = lst.pop()
                    res = a.merge(b)
                    lstNew.append(res)
                else:

                    lstNew.append(a)
                    return lstNew

        res =  reduce(lambda z, x: x.merge(z), pair(self.nodes), PairingHeapWrapper(self.ordering, self.coobject))
        return res
