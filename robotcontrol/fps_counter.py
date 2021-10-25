
import time

# begin local import: Change to from . import MODULE
import hudWriter
# end local import: Change to from . import MODULE

FPS_COUNTER = "FPS_COUNTER"

class FPSCounter:

    __instance = None
    SAMPLE_TIME = 2.0
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            
            cls._fps_time = 0
            cls._fps_count = -1
            cls._fps_value = 0

        return cls.__instance
    
    def notifyPoseChange(self):
        if self._fps_count == -1:
            self._fps_count = 1
            self._fps_time = time.time()

            self.__show()
        else:
            elapsed_time = abs(time.time() - self._fps_time)
            if elapsed_time >= FPSCounter.SAMPLE_TIME:
                self._fps_value = self._fps_count / elapsed_time

                print(self._fps_value, self._fps_count, elapsed_time)

                self.__show()

                self._fps_count = -1
            else:
                self._fps_count += 1

    def __show(self):
        hudWriter.HUDWriterOperator._textos[FPS_COUNTER] = hudWriter.Texto(text=f"{self._fps_value:0.2f} FPS", x=15, y=200)

    def clear(self):
        if FPS_COUNTER in hudWriter.HUDWriterOperator._textos:
            del hudWriter.HUDWriterOperator._textos[FPS_COUNTER]
