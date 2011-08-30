import code

code.interact()

a = 5

ii = code.InteractiveInterpreter(locals=globals())

ii.runsource('raise Exception(5)')

