# PyLox/Olox

All code is based on the book "Crafting Interpreters" by Robert Nystrom.

I originally set out to do this entirely in Odin. However, I decided to implement the Tree-walk interpreter in Python instead. The Python interpreter code is in the tree_walk directory. Much of the object oriented design for the tree-walk interpreter was not a great fit for Odin which was why I decided for a simple Python implementation. 

That said, I will be porting the second half of the book to Odin for the bytecode interpreter.