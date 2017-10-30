import esp
import gc
import webrepl
esp.osdebug(None)
gc.collect()
gc.enable()
webrepl.start()
