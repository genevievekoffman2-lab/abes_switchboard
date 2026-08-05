from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget

# A simple rotating spinner, code provided by Claude
class LoadingSpinner(QWidget):
    def __init__(self, parent=None, size=32, line_width=4, speed=80, color='#3a7d5'):
        super().__init__(parent)
        self._angle = 0
        self._size = size
        self._line_width = line_width
        self._color = QColor(color)

        self.setFixedSize(size, size)
        #self.setAttribute(Qt.WA_TranslucentBackground)

        self._timer = QTimer()
        self._timer.timeout.connect(self._rotate)
        self._timer.setInterval(speed) # ms between frames
        self.hide() #hidden until start() is called


    def _rotate(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def start(self):
        self.show()
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(self._color)
        pen.setWidth(self._line_width)
        #pen.setCapStyle(Qt.Round)
        painter.setPen(pen)

        rect = QRect(
            self._line_width, self._line_width,
            self._size -2 * self._line_width,
            self._size -2 * self._line_width,
        )

        painter.translate(self._size/2, self._size/2)
        painter.rotate(self._angle)
        painter.translate(-self._size / 2, -self._size / 2)

        #draw an arc
        painter.drawArc(rect, 0, 270 * 16)