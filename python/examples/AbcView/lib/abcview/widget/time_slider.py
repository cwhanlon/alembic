#! /usr/bin/env python
#-******************************************************************************
#
# Copyright (c) 2012-2013,
#  Sony Pictures Imageworks Inc. and
#  Industrial Light & Magic, a division of Lucasfilm Entertainment Company Ltd.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# *       Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# *       Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
# *       Neither the name of Sony Pictures Imageworks, nor
# Industrial Light & Magic, nor the names of their contributors may be used
# to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#-******************************************************************************

import os
import sys

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

class Slider(QtGui.QSlider):
    def __init__(self, parent):
        super(Slider, self).__init__(QtCore.Qt.Horizontal, parent)
        self.setMouseTracking(True)
        self.mouse_pos_x = 0
        self.__paint_mouse_frame = False
        self.__paint_slider_frame = True
        self.__mouse_down = False
        self.setSingleStep(1)
        self.setPageStep(1)

    def draw_text(self, rect, qp, value):
        qp.drawText(rect, QtCore.Qt.AlignLeft, str(value))

    def length(self):
        return self.maximum() - self.minimum()

    ## base class overrides

    def value(self, xpos=None):
        if xpos is None:
            return super(Slider, self).value()
        if xpos <= 0:
            return self.minimum()
        elif xpos >= self.width():
            return self.maximum()
        else:
            return int(round((self.length() / (self.width() / float(xpos))) + self.minimum()))

    def sliderPosition(self):
        if self.value() <= self.minimum():
            return 0
        elif self.value() >= self.maximum():
            return self.width()
        else:
            return int(self.width() / (self.length()  / float(self.value() - self.minimum())))

    def enterEvent(self, event):
        self.__paint_mouse_frame = True
        self.repaint()
        super(Slider, self).enterEvent(event)

    def leaveEvent(self, event):
        self.__paint_mouse_frame = False
        self.repaint()
        super(Slider, self).leaveEvent(event)

    def mousePressEvent(self, event):
        self.setSliderPosition(self.value(event.pos().x()))
        self.__paint_mouse_frame = False
        self.__mouse_down = True
        super(Slider, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.__mouse_down:
            self.__paint_mouse_frame = False
        else:
            self.__paint_mouse_frame = True
        self.mouse_pos_x = event.pos().x()
        self.repaint()
        super(Slider, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.__mouse_down = False
        self.__paint_mouse_frame = True
        super(Slider, self).mouseReleaseEvent(event)

    def paintEvent(self, event):
        super(Slider, self).paintEvent(event)
        qp = QtGui.QPainter()
        qp.begin(self)

        # default text style
        qp.setPen(QtGui.QColor(155, 165, 155))
        qp.setFont(QtGui.QFont('Arial', 10))
        
        rect_s = event.rect()
        rect_s.setY(2)
        sr = rect_s.getRect()

        # start position
        if 0:
            self.draw_text(rect_s, qp, self.minimum())
        
        # end position
        if 0:
            rect_e = QtCore.QRect(sr[0], sr[1], sr[2], sr[3])
            rect_e.setX(self.width() - 25)
            self.draw_text(rect_e, qp, self.maximum())
        
        opt = QtGui.QStyleOptionSlider()
        self.initStyleOption(opt)
        style = self.style()
        handle = style.subControlRect(style.CC_Slider, opt, 
                                      style.SC_SliderHandle, self) 
        # slider position
        if self.__paint_slider_frame and self.length() > 0:
            rect_s = QtCore.QRect(sr[0], sr[1], sr[2], sr[3])
            rect_s.setX(handle.x()+6)
            qp.fillRect(rect_s.x()-6, rect_s.y()-10, rect_s.width(), 20,
                        QtGui.QColor(55, 55, 55))
            qp.setPen(QtGui.QColor(55, 255, 95))
            self.draw_text(rect_s, qp, self.value())

        # mouse position
        if self.__paint_mouse_frame:
            rect_m = QtCore.QRect(sr[0], sr[1], sr[2], sr[3])
            rect_m.setX(self.mouse_pos_x)
            qp.setPen(QtGui.QColor(145, 245, 145))
            self.draw_text(rect_m, qp, self.value(self.mouse_pos_x))

        qp.end()

class TimeSlider(QtGui.QGroupBox):
    signal_play_fwd = QtCore.pyqtSignal()
    signal_play_stop = QtCore.pyqtSignal()
    signal_frame_changed = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super(TimeSlider, self).__init__(parent)
        self.setObjectName("time_slider")
        self.setLayout(QtGui.QHBoxLayout())
        self.setFixedHeight(20)
        self.layout().setSpacing(0)
        self.layout().setMargin(0)

        # slider
        self.slider = Slider(self)
        self.slider.setFixedHeight(20)
        self.slider.valueChanged.connect(self.handle_frame_change)

        # buttons
        self.play_button = QtGui.QPushButton(self)
        self.play_button.setObjectName("play_button")
        self.play_button.setFixedSize(50, 20)
        self.play_button.clicked.connect(self.handle_play)
        self.stop_button = QtGui.QPushButton(self)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setFixedSize(50, 20)
        self.stop_button.clicked.connect(self.handle_stop)
        self.stop_button.hide()

        # labels
        self.first_frame_label = QtGui.QLabel()
        self.first_frame_label.setFixedSize(40, 20)
        self.first_frame_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.last_frame_label = QtGui.QLabel()
        self.last_frame_label.setFixedSize(40, 20)
        self.last_frame_label.setAlignment(QtCore.Qt.AlignHCenter)

        self.layout().addWidget(self.first_frame_label)
        self.layout().addWidget(self.slider)
        self.layout().addWidget(self.last_frame_label)
        self.layout().addWidget(self.play_button)
        self.layout().addWidget(self.stop_button)

        self.set_minimum(0)
        self.set_maximum(0)

    def set_minimum(self, value):
        self.slider.setMinimum(value)
        self.first_frame_label.setText(str(int(value)))

    def set_maximum(self, value):
        self.slider.setMaximum(value)
        self.last_frame_label.setText(str(int(value)))

    def length(self):
        return self.slider.length()

    def value(self):
        return self.slider.value()

    def set_value(self, value):
        self.slider.setValue(value)

    def handle_frame_change(self, value):
        self.signal_frame_changed.emit(value)

    def handle_stop(self):
        self.signal_play_stop.emit()
        self.play_button.show()
        self.stop_button.hide()

    def handle_play(self):
        if self.length() == 0:
            return
        self.signal_play_fwd.emit()
        self.play_button.hide()
        self.stop_button.show()

    ## base class overrides

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            if self.play_button.isHidden():
                self.handle_stop()
            else:
                self.handle_play()
            return
        event.accept()
        super(TimeSlider, self).keyPressEvent(event)

