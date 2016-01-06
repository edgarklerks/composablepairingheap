# A composable pairing heap #

This package provides the user a pairing heap, which can be composed with another object adhering to the following minimal interface:

    class MyDataStruct:
		def insert(self, value, object)
		def delete(self, value)
		def exists(self, value)

where object is a specific node of the priority queue and value is an orderable object.

This will let the user efficiently delete from the heap if for example an value is not needed any longer.

The data structure is then wrapped by a decorator:

	t = Coobject(MyDataStruct())

And injected into the heap, together with an function specifying the ordering of the values
you want to prioritize:

	p = PairingHeap(coobject=t, ordering=f)

The co(operating) object will whenever be called, when the something on the heap is deleted or inserted. The co object also exposes the interface of the original wrapped object (in this case MyDataStruct), which will propagate any delete or insert event to the heap.

The heap is constructed so that there is exactly one instance of every node, so that it is possible to access the heap in the middle. This makes it possible to delete from the middle of the heap.

The default ordering is:

	def test(x,y):
		return x < y

The coobject is optional.

When an object is embedded, the time characteristics of insert and delete are also composed:

Say we have data structure N with time behaviour:

* Insert O(Ti)
* Delete O(Td)

Then the time behaviour of the heap will become:

* Insert O(1 + Ti)
* Delete O(log n + Td)

# Interface #


The heap provides the following interface:


## initialize ##

Create the heap:

	heap = PairingHeap(coobject=coobj, ordering=lambda x, y: x < y)

## insert ##

Insert entries:

	heap.insert(1)
	heap.insert(9)
	heap.insert(8)

## findFirst ##
Find the first entry (will return an Optional, because the heap maybe empty):

	heap.findFirst().extract == 1

## deleteFirst ##
Delete the first entry:

	heap.deleteFirst().findFirst().extract == 8

## fromList ##

Add elements to the heap from a list:

	heap.fromList([4,5,6,7,8])

	heap.findFirst().extract == 4

## coobject.delete ##

Deletion can also be done in the middle through the coobject:
	coop.delete(7)


## toList ##

Convert the heap to a list in order (destructive, it will destroy the heap!):

	heap.toList() == [4,5,6,8,8,9]
	heap.findFirst().hasResult == False

## isEmpty ##

Test if the heap is empty:

	heap.isEmpty() == True

## _fold ##

And _fold, which can be used to check for invariants, which only hold for the whole set of values and the heap:

	heap._fold(lambda node, accum, typeAsString: ..., startValue)

However one need to be careful to not change the ordered part of your value, otherwise the heap may be inconsistent! This is an internal api. Example usage:

	def pr(x,z,t):
		print (x,t)

	heap.fromList([7,6,4,9,8])
	heap._fold(pr)

_fold is extremely powerful. To show this we can define a 'real' fold as:

	def foldheap(h,f,z):
		def inner(x,z,t):
			if(t == "Value"):
				return f(x,z)
			else:
				return z
	    return h._fold(f, z)

Although usually this is not a wanted operation on these type of datastructures. _fold will allow the programmer to create arbitrary aggregation functions on the heap.

As bonus the heap has a static method, which implements the traditional heap sort as fusion of fromList and toList:

	heapSort([9,2,6,5,1]) == [1,2,5,6,9]

Note that the interface is fluid, but that the heap updates itself inplace. This is an consequence of being able to delete in the middle of the heap by adding a coobject.

For further properties of the heap, the programmer is pointed to the tests.

# Caveats #

The user shall not manipulate the reference of the node received by the heap through the insert method implemented by the user. The heap will only be able to keep both data structures synchronised if the object is exactly the same. This means that:

	x = Coobject(SomeStructure())
	PairingHeap(coobject=x)
	p.insert(1) # will call underwater x.coobject.insert
	node1 = p.someMagicMethodToGetTheInternalNodeOf(1)
	node2 = x.get(1)
	id(node1) == id(node2)

Should hold.

# Wishlist #

* Define contracts for all the methods.
* Create a better interface for Optional.
* Add more aggregrate type of functions to the heap.
* Make the heap a functor
* Implement the user to change the value (as long as the ordering is kept). This will let the user scale the priorities dynamicly if needed.
* Make it thread safe (it is not at the moment).
