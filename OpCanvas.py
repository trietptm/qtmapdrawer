from qt import *
from qtcanvas import *
from MathModule import *
import random
import tempfile
import re

class OpCanvas(QCanvasView):
	def __init__(self,c,parent,name,f):
		QCanvasView.__init__(self,c,parent,name,f)
		wm=QWMatrix()
		self.setWorldMatrix(wm)
		self.parent=parent
		self.__moving=0
		self.__moving_start=0
		self.last_x=-1
		self.last_y=-1
		self.zoomx=1
		self.zoomy=1

	def Zoom(self,x,y):
		if x==0 or y==0:
			return
		curx=(self.contentsX())
		origx=curx*float(1/float(self.zoomx))
		centerx=origx*x
		cury=(self.contentsY())
		origy=cury*float(1/float(self.zoomy))
		centery=origy*y

		wm=QWMatrix()
		self.zoomx=x
		self.zoomy=y
		wm.scale(x,y)
		self.setWorldMatrix(wm)
		self.setContentsPos(centerx,centery)
		curx=(self.contentsX())
		cury=(self.contentsY())

	def contentsMouseDoubleClickEvent(self,e):
		point=self.inverseWorldMatrix().map(e.pos())
		self.parent.DClicked(point)

	def contentsMousePressEvent(self,e): # QMouseEvent e
		if e.button()==Qt.LeftButton:
			point=self.inverseWorldMatrix().map(e.pos())
			ilist=self.canvas().collisions(point) #QCanvasItemList ilist
			for each_item in ilist:
				if each_item.rtti()==984376:
					if not each_item.hit(point):
						continue
				self.__moving=each_item
				self.__moving_start=point
				return
			self.__moving=0
			self.last_x=e.pos().x()
			self.last_y=e.pos().y()

	def contentsMouseReleaseEvent(self,e):
		point=self.inverseWorldMatrix().map(e.pos())
		CheckForRepeatedClick=False
		if e.button()==Qt.LeftButton:
			CheckForRepeatedClick=True
		self.parent.Clicked(point,CheckForRepeatedClick)
		self.last_x=-1
		self.last_y=-1

		if e.button()==Qt.RightButton:
			self.parent.ContextMenu(point)

	def contentsMouseMoveEvent(self,e):
		if self.last_x>0 or self.last_y>0:
			#point=self.inverseWorldMatrix().map(e.pos());
			cur_x=e.pos().x()
			cur_y=e.pos().y()
			dx=self.last_x-cur_x
			dy=self.last_y-cur_y
			self.scrollBy(dx,dy)
			self.last_x=cur_x
			self.last_y=cur_y
			print cur_x,cur_y
		"""
		COMMENTED_OUT
		if  self.__moving :
			point=self.inverseWorldMatrix().map(e.pos());
			self.__moving.moveBy(point.x() - self.__moving_start.x(),point.y() - self.__moving_start.y())
			self.__moving_start=point
		"""
			
		self.canvas().update()
		return

	def clear(self):
		ilist=self.canvas().allItems()
		for each_item in ilist:
			if each_item:
				each_item.setCanvas(None)
				del each_item
		self.canvas().update()
