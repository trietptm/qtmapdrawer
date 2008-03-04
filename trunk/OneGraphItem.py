from qt import *
from qtcanvas import *
from MathModule import *
import random
import tempfile
import re
from GraphVizProcessor import *

class MyQCanvasPolygon(QCanvasPolygon):
	def __init__(self,parent=None):
		self.parent=parent
		QCanvasPolygon.__init__(self,parent)
		self.pa=None
		self.drawn=False
		self.LinesItem=[]
		self.Brush=QBrush(Qt.white)

	def moveBy(self,mx,my):
		pass

	def real_moveBy(self,mx,my):
		QCanvasPolygon.moveBy(self,mx,my)

	def drawShape(self,p):
		p.setBrush(self.Brush)
		QCanvasPolygon.drawShape(self,p)
		if not self.drawn:
			points=[]
			for i in range(0,self.pa.size(),1):
				points.append(self.pa.point(i))
			self.DrawLines(points+[points[0]])
			self.drawn=True

	def setPoints(self,pa):
		self.pa=pa
		QCanvasPolygon.setPoints(self,pa)

	def DrawLines(self,points,z=10):
		for i in range(0,len(points)-1,1):
			[x1,y1]=points[i]
			[x2,y2]=points[i+1]
			line=QCanvasLine(self.parent)
			self.LinesItem.append(line)
			line.setPoints(x1,y1,x2,y2)
			line.setZ(z)
			line.show()
	def setColor(self,color):
		for item in self.LinesItem:
			item.setPen(QPen(color))
			
	def setBrush(self,brush):
		self.Brush=brush
		QCanvasPolygon.setBrush(self,brush)

	def __del__(self):
		for item in self.LinesItem:
			item.setCanvas(None)
			del item

class OneBandItem1(QCanvasLine):
	def __init__(self,mapdrawer,name,x1,y1,x2,y2):
		self.mapdrawer=mapdrawer
		self.name=name
		self.minx=x1
		self.miny=y1
		self.maxx=x2
		self.maxy=y2
		
		self.LineItems=[]
	
	
		QCanvasLine.__init__(self,self.mapdrawer)
		self.setPoints(x1,y1,x2,y2)
		self.setPen(QPen(Qt.white))
		self.setZ(1)
		self.show()
		self.LineItems.append(self)

	def moveBy(self,mx,my):
		pass

	def move(self,mx,my):
		pass

	def DecorateColors(self,colors):
		if colors:
			[penColor,brushColor,textColor,indicator]=colors
			if penColor:
				for item in self.LineItems:
					item.setPen(QPen(penColor))
			#TODO: indicator

	def SetState(self,colors):
		self.DecorateColors(colors)
		self.current_state_colors=colors

	def boundingRectarray(self):
		return [self.minx,self.miny,self.maxx,self.maxy]

	def SetSelected(self,selected,type='selection'):
		return False

	def GetCenter(self):
		return [(self.minx+self.maxx)/2,(self.miny+self.maxy)/2]

class OneBandItem(QCanvasRectangle):
	def __init__(self,mapdrawer,name,x,y,width,height,basey):
		self.mapdrawer=mapdrawer
		self.name=name
		self.basey=basey
		self.minx=x
		self.miny=y
		self.maxx=x+width
		self.maxy=y+height
		
		self.LineItems=[]
	
		QCanvasRectangle.__init__(self,x,y,width,height,self.mapdrawer)
		self.setBrush(QBrush(Qt.red))
		self.setPen(QPen(Qt.black))		
		self.setZ(1)
		self.show()
		self.LineItems.append(self)

	def moveBy(self,mx,my):
		pass

	def move(self,mx,my):
		pass

	def DecorateColors(self,colors):
		if colors:
			[penColor,brushColor,textColor,indicator]=colors
			if penColor:
				self.setPen(QPen(penColor))
			if brushColor:
				self.setBrush(QBrush(brushColor))
			#TODO: indicator

	def SetState(self,colors):
		self.DecorateColors(colors)

	def boundingRectarray(self):
		return [self.minx,self.basey,self.maxx,self.maxy]

	def SetSelected(self,selected,type='selection'):
		return False

	def GetCenter(self):
		return [(self.minx+self.maxx)/2,(self.miny+self.maxy)/2]

class MapBand(QCanvasRectangle):
	def __init__(self,mapdrawer,names,caller,called):
		self.mapdrawer=mapdrawer
		self.names=names
		self.caller=caller
		self.called=called

		level2names={}
		for [level,name] in GetLeveledNames(caller,names[0],names):
			if not level2names.has_key(level):
				level2names[level]=[]
			level2names[level].append(name)
		levels=level2names.keys()
		levels.sort()
		xlen=len(levels)
		maximum_y=0
		for one_level in levels:
			if len(level2names[one_level])>maximum_y:
				maximum_y=len(level2names[one_level])

		x=10
		y=10
		xlevel=10
		ylevel=2

		width=xlen*xlevel
		height=maximum_y*ylevel

		self.x1=x
		self.y1=y
		self.x2=x+width
		self.y2=y+height

		QCanvasRectangle.__init__(self,x-5,y-5,width+10,height+10,self.mapdrawer)
		self.setBrush(QBrush(Qt.yellow))
		self.setPen(QPen(Qt.black))		
		self.setZ(1)
		self.show()

		self.ItemID={}
		current_x=0
		for one_level in levels:
			current_y=len(level2names[one_level])
			x=self.x1+current_x*xlevel
			y=self.y2-current_y*ylevel
			width=xlevel
			height=ylevel*current_y
			item=OneBandItem(self.mapdrawer,name,x,y,width,height,basey=self.y1)
			for name in level2names[one_level]:
				self.ItemID[name]=item
			current_x+=1

	def GetSurroudingNames(self,names):
		ret_names=[]
		ret_names+=names
		while 1:
			new_names=[]
			for name in names:
				if self.caller.has_key(name):
					for one_name in self.caller[name]:
						if not one_name in ret_names and not one_name in new_names:
							new_names.append(one_name)
				if self.called.has_key(name):
					for one_name in self.called[name]:
						if not one_name in ret_names  and not one_name in new_names:
							new_names.append(one_name)

			if len(ret_names)+len(new_names)>100:
				break
			ret_names+=new_names
			names=new_names
				
		return ret_names

	def moveBy(self,mx,my):
		pass

	def move(self,mx,my):
		pass

	def GetItemID(self):
		return self.ItemID
		
	def boundingRectarray(self):
		return [self.x1,self.y1,self.x2,self.y2]

class OneGraphItem:
	"""
	_draw_ Drawing operations  
	_ldraw_ Label drawing  
	_hdraw_ Head arrowhead Edge only  
	_tdraw_ Tail arrowhead Edge only  
	_hldraw_ Head label Edge only  
	_tldraw_ Tail label Edge only  
	"""
	UseLineForPolygon=False
	colormap={'black':Qt.black,'white':Qt.white}
	LabelDepth=20
	TextDepth=30
	LinesDepth=50
	FilledPolygonDepth=60
	BlankPolygonDepth=0
	EllipseDepth=0

	def __init__(self,name,mapdrawer=None,attrs='',content=None,offsetx=0,offsety=0):
		self.ColorMap={}
		self.ColorMap['call']=[QColor(0xcc,0x00,0x00),QColor(0xcc,0x00,0x00),QColor(0xcc,0x00,0x00)]
		self.ColorMap['cmp']=[QColor(0x33,0xcc,0x99),QColor(0x33,0xcc,0x99),QColor(0x33,0xcc,0x99)]
		self.ColorMap['test']=[QColor(0x33,0xcc,0x99),QColor(0x33,0xcc,0x99),QColor(0x33,0xcc,0x99)]
		self.ColorMap['push']=[QColor(0x99,0xcc,0x33),QColor(0x99,0xcc,0x33),None]

		self.offsetx=offsetx
		self.offsety=offsety
		self.InitState()
		self.content=content

		self.UseDirectTextDisplay=False
		if not self.content:
			self.UseDirectTextDisplay=True
		self.name=name
		self.mapdrawer=mapdrawer
		self.minx=-1
		self.miny=-1
		self.maxx=0
		self.maxy=0
		
		#Items
		self.EllipseItems=[]
		self.PolygonItems=[]
		self.TextItems=[]
		self.LineItems=[]
	
		self.LabelObjectInfos=[]
		self.LabelObjects=[]

		for attr_name in attrs.keys():
			self.DrawByAttrs(ParseXDOTData(attrs[attr_name]))
		self.DrawLabelObjects()
		self.SaveColors()

	def DrawLabelObjects(self):
		self.LabelObjectInfos=[]
		i=0
		if not self.UseDirectTextDisplay and self.content:
			for [[[x,y,j,w],text],font_attr,prereq_attrs] in self.LabelObjects:
				if len(font_attr)>0 and len(font_attr[0])>0:
					font_size=font_attr[0][0]
				startx=x-w/2
				starty=y-font_size/2

				if i==0:
					self.DrawOneText(startx,starty,font_size,self.name,prereq_attrs=prereq_attrs)
				else:
					[address,op,[op1,op2],comment]=self.content[i-1]
					op_item=None
					op1_item=None
					op2_item=None
					op_item=self.DrawOneText(startx,starty,font_size,op,prereq_attrs=prereq_attrs)
					rect=op_item.boundingRect()
					startx=rect.right()+5

					if op1:
						op1_item=self.DrawOneText(startx,starty,font_size,op1,prereq_attrs=prereq_attrs)
						rect=op1_item.boundingRect()
						startx=rect.right()+5
				
					if op2:
						op2_item=self.DrawOneText(startx,starty,font_size,op2,prereq_attrs=prereq_attrs)
						rect=op2_item.boundingRect()

					if self.ColorMap.has_key(op):
						[op_color,op1_color,op2_color]=self.ColorMap[op]
						if op_color and op_item:
							op_item.setColor(op_color)
						if op1_color and op1_item:
							op1_item.setColor(op1_color)
						if op2_color and op2_item:
							op2_item.setColor(op2_color)

					self.LabelObjectInfos.append([self.content[i-1],[op_item,op1_item,op2_item]])
				i+=1

	def IsInPoint(self,rect,x,y):
		if rect.left()<=x and rect.top()<=y and x<=rect.right() and y<=rect.bottom():
			return True

	def GetSelectedLabels(self,point):
		x=point.x()
		y=point.y()
		pos=0
		for [content,[op_item,op1_item,op2_item]] in self.LabelObjectInfos:
			if op_item and self.IsInPoint(op_item.boundingRect(),x,y):
				return [pos,0,str(op_item.text())]
			if op1_item and self.IsInPoint(op1_item.boundingRect(),x,y):
				return [pos,1,str(op1_item.text())]
			if op2_item and self.IsInPoint(op2_item.boundingRect(),x,y):
				return [pos,2,str(op2_item.text())]
			pos+=1
		return None

	def DrawOneText(self,x,y,font_size,display_text,prereq_attrs=None):
		x+=self.offsetx
		y+=self.offsety

		display_text=str(display_text) #TODO:
		tw=QCanvasText(display_text,self.mapdrawer)
		self.TextItems.append(tw)
		self.SetPreRequisite(tw,prereq_attrs,type='text')
		tw.setX(x)
		tw.setY(y)
		tw.setZ(self.TextDepth)
		tw.show()
		return tw	

	def GetMaxValue(self,points):
		for [x,y] in points:
			x+=self.offsetx
			y+=self.offsety
		
			if x>self.maxx:
				self.maxx=x
			if y>self.maxy:
				self.maxy=y
			if self.minx==-1 or x<self.minx:
				self.minx=x
			if self.miny==-1 or y<self.miny:
				self.miny=y

	def MakePointArry(self,arr):
		qpoint_array=QPointArray(len(arr))
		i=0
		for [x,y] in arr:
			x+=self.offsetx
			y+=self.offsety
		
			qpoint_array.setPoint(i,x,y)
			i+=1
		return qpoint_array

	def SetPreRequisite(self,widget,prereq_attrs,type=''):
		if prereq_attrs==None:
			prereq_attrs={}
		color=Qt.black
		if prereq_attrs.has_key('c') and len(prereq_attrs['c'])>0:
			if self.ColorMap.has_key(prereq_attrs['c']):
				color=self.ColorMap[prereq_attrs['c']]
		if type=='text':
			widget.setColor(color)
		else:
			widget.setPen(QPen(color))
			color=Qt.black
			if prereq_attrs.has_key('C') and len(prereq_attrs['C'])>0:
				if self.ColorMap.has_key(prereq_attrs['C']):
					color=self.ColorMap[prereq_attrs['C']]
			widget.setBrush(QBrush(color))
			#TODO: process 'S'

	def DrawLines(self,points,prereq_attrs=None):
		for i in range(0,len(points)-1,1):
			[x1,y1]=points[i]
			[x2,y2]=points[i+1]
			x1+=self.offsetx
			y1+=self.offsety
			x2+=self.offsetx
			y2+=self.offsety

			line=QCanvasLine(self.mapdrawer)
			self.LineItems.append(line)
			line.setPoints(x1,y1,x2,y2)
			self.SetPreRequisite(line,prereq_attrs)
			line.setZ(self.LinesDepth)
			line.show()

	def DrawPolygon(self,points,prereq_attrs=None,filled=True):
		if not prereq_attrs:
			prereq_attrs={}
		self.GetMaxValue(points)
		if filled:
			polygon=QCanvasPolygon(self.mapdrawer)
			polygon.setPoints(self.MakePointArry(points))
			self.PolygonItems.append(polygon)
			self.SetPreRequisite(polygon,prereq_attrs)
			polygon.setZ(self.FilledPolygonDepth)
			polygon.show()
		else:
			if self.UseLineForPolygon:
				self.DrawLines(points+[points[0]],prereq_attrs=prereq_attrs)
			else:
				polygon=MyQCanvasPolygon(self.mapdrawer)
				self.PolygonItems.append(polygon)
				polygon.setPoints(self.MakePointArry(points))
				self.SetPreRequisite(polygon,prereq_attrs)
				polygon.setBrush(QBrush(Qt.white))
				polygon.setZ(self.BlankPolygonDepth)
				polygon.show()
				self.DrawLines(points+[points[0]],prereq_attrs=prereq_attrs)

	def DrawBSPLines(self,points,prereq_attrs=None):
		#line=QCanvasSpline(self.mapdrawer)
		#line.setControlPoints(self.MakePointArry([[x1,y1],[x2,y2]]),1)
		result_points=bspline(points,2)
		return self.DrawLines(result_points,prereq_attrs=prereq_attrs)

	def DrawLabels(self,text_attrs,prereq_attrs=None):
		font_size=12
		if prereq_attrs.has_key('F'):
			font_attr=prereq_attrs['F']
		if len(font_attr)>0 and len(font_attr[0])>0:
			font_size=font_attr[0][0]
		for [[x,y,j,w],text] in text_attrs:
			x+=self.offsetx
			y+=self.offsety

			if self.UseDirectTextDisplay:
				tw=QCanvasText(text,self.mapdrawer)
				self.TextItems.append(tw)
				self.SetPreRequisite(tw,prereq_attrs,type='text')
				tw.setX(x-w/2)
				tw.setY(y-font_size/2)
				tw.setZ(self.LabelDepth)
				tw.show()
			else:
				self.LabelObjects.append([[[x,y,j,w],text],font_attr,prereq_attrs])

	def DrawEllipse(self,attrs,prereq_attrs=None,filled=True):
		[x0,y0,w,h]=attrs
		x0+=self.offsetx
		y0+=self.offsety
		
		ellipse=QCanvasEllipse(w,h,self.mapdrawer)
		self.EllipseItems.append(ellipse)
		self.SetPreRequisite(ellipse,prereq_attrs)
		ellipse.move(x0,y0)
		ellipse.setZ(self.EllipseDepth)
		ellipse.show()

	def DrawByAttrs(self,parsed_attrs):
		"""
		E x0 y0 w h  Filled ellipse ((x-x0)/w)2 + ((y-y0)/h)2 = 1  
		e x0 y0 w h  Unfilled ellipse ((x-x0)/w)2 + ((y-y0)/h)2 = 1  
		P n x1 y1 ... xn yn  Filled polygon using the given n points  
		p n x1 y1 ... xn yn  Unfilled polygon using the given n points  
		L n x1 y1 ... xn yn  Polyline using the given n points  
		B n x1 y1 ... xn yn  B-spline using the given n control points  
		b n x1 y1 ... xn yn  Filled B-spline using the given n control points  
		T x y j w n -c1c2...cn  Text drawn using the baseline point (x,y). The text consists of the n characters following '-'. The text should be left-aligned (centered, right-aligned) on the point if j is -1 (0, 1), respectively. The value w gives the width of the text as computed by the library.  
		
		C n -c1c2...cn  Set fill color. The color value consists of the n characters following '-'.  
		c n -c1c2...cn  Set pen color. The color value consists of the n characters following '-'.  
		F s n -c1c2...cn  Set font. The font size is s points. The font name consists of the n characters following '-'.  
		S n -c1c2...cn  Set style attribute. The style value consists of the n characters following '-'. The syntax of the value is the same as specified for a styleItem in style.  
		"""
		prereq_attrs={}
		for command in ['F','S','C','c']:
			if parsed_attrs.has_key(command):
				prereq_attrs[command]=parsed_attrs[command]
			else:
				prereq_attrs[command]={}

		for command in parsed_attrs.keys():
			attrs=parsed_attrs[command]
			if command=='p':
				#TODO: not filling..
				self.DrawPolygon(attrs,prereq_attrs=prereq_attrs,filled=False)
			elif command=='P':
				self.DrawPolygon(attrs,prereq_attrs=prereq_attrs)
			elif command=='B':
				self.DrawBSPLines(attrs,prereq_attrs=prereq_attrs)
			elif command=='b':
				#TODO: filled one
				self.DrawBSPLines(attrs,prereq_attrs=prereq_attrs)
			elif command=='T':
				self.DrawLabels(attrs,prereq_attrs=prereq_attrs)
			elif command=='L':
				self.DrawLines(attrs,prereq_attrs=prereq_attrs)
			elif command=='E':
				self.DrawEllipse(attrs,prereq_attrs=prereq_attrs)
			elif command=='e':
				self.DrawEllipse(attrs,prereq_attrs=prereq_attrs,filled=False)
			else:
				pass

	def boundingRectarray(self):
		return [self.minx,self.miny,self.maxx,self.maxy]

	def SetSelected(self,selected,type='selection'):
		#Special case of state
		return True

	def InitState(self):
		pass

	def SaveColors(self):
		self.textColors={}
		self.penColors={}
		self.brushColors={}
		for item in self.TextItems:
			self.textColors[item]=str(item.color().name())
		for item in self.LineItems+self.PolygonItems:
			self.penColors[item]=str(item.pen().color().name())
		for item in self.PolygonItems:
			self.brushColors[item]=str(item.brush().color().name())

	def RestoreColors(self):
		for item in self.textColors.keys():
			color=QColor()
			color.setNamedColor(self.textColors[item])
			item.setColor(color)
		for item in self.penColors.keys():
			color=QColor()
			color.setNamedColor(self.penColors[item])

			item.setPen(QPen(color))
		for item in self.brushColors.keys():
			color=QColor()
			color.setNamedColor(self.brushColors[item])
			item.setBrush(QBrush(color))
		
	def DecorateColors(self,colors):
		if colors:
			[penColor,brushColor,textColor,indicator]=colors
			if textColor:
				for item in self.TextItems:
					item.setColor(textColor)
			if penColor:
				for item in self.LineItems:
					item.setPen(QPen(penColor))
			if brushColor:
				for item in self.PolygonItems:
					item.setBrush(QBrush(brushColor))
			#TODO: indicator

	def SetState(self,colors):
		self.DecorateColors(colors)

	def GetCenter(self):
		return [(self.minx+self.maxx)/2,(self.miny+self.maxy)/2]

	def clear(self):
		for item in self.PolygonItems+self.TextItems+self.LineItems+self.EllipseItems:
			item.setCanvas(None)
			del item