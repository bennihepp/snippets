import code, traceback, signal
import readline

def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    signal.signal(sig, signal.SIG_DFL) # Unregister handler
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal recieved : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)
    signal.signal(sig, debug)  # Register handler again

def listen(sig=signal.SIGUSR1):
    signal.signal(sig, debug)  # Register handler

