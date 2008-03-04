from qt import *
from qtcanvas import *
from MathModule import *
import random
import tempfile
import re
from GraphVizProcessor import *
from cPickle import *
from OneGraphItem import *
from OpCanvas import *

def GetLeveledNames(caller,name,names=None,checked_names=None,level=-1,current_level=0):
	if not checked_names:
		checked_names={}
	if level==0 or checked_names.has_key(name):
		return []
	ret_names=[[current_level,name]]
	checked_names[name]=1
	if caller.has_key(name):
		for child_name in caller[name]:
			if not names or child_name in names:
				ret_names+=GetLeveledNames(caller,child_name,names,checked_names=checked_names,level=level-1,current_level=current_level+1)
	return ret_names

"""		
NORMAL=0
ALERT01=1
ALERT02=2
ALERT03=3
ALERT04=4
SELECT=5

		self.StateFeatures[ALERT01]=[Qt.red,Qt.yellow,Qt.blue,0]
		self.StateFeatures[ALERT02]=[Qt.white,Qt.gray,Qt.white,0]
		self.StateFeatures[ALERT03]=[Qt.green,Qt.white,Qt.gray,0]
		self.StateFeatures[ALERT04]=[Qt.blue,Qt.white,Qt.gray,0]
		self.StateFeatures[SELECT]=[Qt.red,Qt.white,Qt.gray,0]

"""
class MapDrawer(QWidget):
	FRONT_SIDE=0
	BACK_SIDE=1
	UP_SIDE=2
	DOWN_SIDE=3
	BigNodeNumber=300

	def __init__(self,parent=None,name=None):
		#DEBUGGIN
		self.state_debug=0
		#SELF
		QWidget.__init__(self,parent,name)
		#self.setFocusPolicy(self.StrongFocus)

		#VARIABLES
		self.maxx=1000
		self.maxy=1000
		self.zoomx=float(1)
		self.zoomy=float(1)

		self.SavedState={}
		self.Item2State={}
		self.StartToSaveCurrentStatesByName()
		self.ItemID={}
		self.BandItemID={}
		self.SelectionCallbacks=[]
		self.OperationCallbacks=[]
		self.SelectContinuously=False
		self.SelectedNames=[]
		self.AlertedNames=[]
		self.ElementOperations=[]
		self.contextMenu=None
		self.ContextMenuCheckInfo={}
		
		#DEFINITIONS
		self.StateFeatures={}
		#MAPDRAWER widget creation and location
		self.mapdrawer=QCanvas(self.maxx,self.maxy)
		self.mapdrawer.setAdvancePeriod(30)
		self.mapdrawer.setDoubleBuffering(True)
		self.mapdrawer_view=OpCanvas(self.mapdrawer,self,name,0)
		self.mapdrawer_view.setDragAutoScroll(True)
		grid=QGridLayout(self,1,1,1)
		grid.addWidget(self.mapdrawer_view,0,0)
		grid.setColStretch(0,1)
		grid.setRowStretch(0,1)

	def DrawGraphVizMap(self,mapdrawer,names,caller,contents,node_shape='record',offsetx=0,offsety=0,leastx=800,leasty=600,output_graphic_filename=None,aliases=None):
		ItemID={}
		[[maxx,maxy],node_attrs_map,edge_attrs_maps]=GetGVData(names,caller,contents,node_shape=node_shape,output_graphic_filename=output_graphic_filename,aliases=aliases)
		if output_graphic_filename:
			return
		maxx+=offsetx
		maxy+=offsety
		if leastx>maxx:
			maxx=leastx
		if leasty>maxy:
			maxy=leasty
	
		mapdrawer.resize(maxx,maxy)
		for name in node_attrs_map.keys():
			node_attrs=node_attrs_map[name]
			content=None
			if contents and contents.has_key(name):
				content=contents[name]
			if aliases.has_key(name):
				display_name=aliases[name]
			else:
				display_name=str(name)
			ItemID[name]=OneGraphItem(display_name,mapdrawer,node_attrs,content=content,offsetx=offsetx,offsety=offsety)

		for src in edge_attrs_maps.keys():
			for dst in edge_attrs_maps[src].keys():
				line_attrs=edge_attrs_maps[src][dst]
				key=str(src)+str(dst)
				ItemID[key]=OneGraphItem('',mapdrawer,line_attrs,offsetx=offsetx,offsety=offsety)
		return ItemID

	def Zoom(self,x,y):
		self.zoomx=x
		self.zoomy=y
		self.mapdrawer_view.Zoom(x,y)

	def SetSelectionCallbacks(self,callbacks):
		self.SelectionCallbacks=callbacks

	def SetDClickCallbacks(self,callbacks):
		self.OperationCallbacks=callbacks

	def SaveCurrentMapToFile(self,output_graphic_filename):
		self.DrawGraphVizMap(self.mapdrawer,self.names,self.caller,self.contents,node_shape=self.node_shape,output_graphic_filename=output_graphic_filename)

	def SetMapData(self,names,caller,called,comments,op='new',max_level=-1,branch_name='',type='normal',root_names=[],contents=None,layout='graphviz',aliases=None):
		if not aliases:
			aliases={}
		self.names=names
		self.caller=caller
		self.called=called
		self.contents=contents
		self.SubMapItemID={}
		self.MapBand=None
		if layout=='graphviz':
			if len(names)>1000000:
				#Save this for later examination
				#fd=open("sample.map","wb")
				#dump([names,caller,called,contents],fd)
				#fd.close()
				self.MapBand=MapBand(self.mapdrawer,names,caller,called)
				self.BandItemID=self.MapBand.GetItemID()
				[x1,y1,x2,y2]=self.MapBand.boundingRectarray()
				sizex=1024
				sizey=768
				if x2+100>sizex:
					sizex=x2+100
				if y2+100>sizey:
					sizey=y2+100
				self.mapdrawer.resize(sizex,sizey)
			else:
				self.node_shape="record"
				if len(names)>self.BigNodeNumber:
					self.node_shape="rect"
				self.ItemID=self.DrawGraphVizMap(self.mapdrawer,names,caller,contents,node_shape=self.node_shape,aliases=aliases)
				if len(names)>0:
					self.ShowNode(names[0])

	def ShowNode(self,name):
		if not self.ItemID.has_key(name):
			if self.MapBand:
				partial_names=self.MapBand.GetSurroudingNames([name])
	
				[minx,miny,maxx,maxy]=[x1,y1,x2,y2]=self.MapBand.boundingRectarray()
				self.ItemID=self.DrawGraphVizMap(self.mapdrawer,partial_names,self.caller,self.contents,offsety=maxy+50,leastx=maxx+100,leasty=maxy+100)
				for state in self.SavedState.keys():
					self.SetState(self.SavedState[state],state)

		if self.ItemID.has_key(name):
			[x,y]=self.ItemID[name].GetCenter()
			self.mapdrawer_view.center(x*self.zoomx,y*self.zoomy,1.0,1.0)

	def Clear(self):
		if self.ItemID:
			for name in self.ItemID.keys():
				item=self.ItemID[name]
				item.clear()
				del item
		self.ItemID={}
		self.SelectContinuously=False
		self.SelectedNames=[]
		self.AlertedNames=[]
		self.mapdrawer_view.clear()

	def closeEvent(self,ce):
		self.Clear()
		ce.accept()

	#def hideEvent(self,he):
	#	self.Clear()


	#### This about Pointing,Clicking,Double-clicking #####
	def IsPointInItem(self,point,item):
		x=point.x()
		y=point.y()
		rect=item.boundingRectarray()
		[x1,y1,x2,y2]=rect
		return x1<=x and y1<=y and x2>=x and y<=y2

	def GetNamesByPoint(self,point):
		SelectedNames=[]
		for name in self.ItemID.keys():
			if self.IsPointInItem(point,self.ItemID[name]):
				SelectedLabelInfo=self.ItemID[name].GetSelectedLabels(point)
				SelectedNames.append(['item',name,SelectedLabelInfo])

		if len(SelectedNames)==0:
			for name in self.BandItemID.keys():
				if self.IsPointInItem(point,self.BandItemID[name]):
					SelectedNames.append(['band',name,None])

		return SelectedNames

	def Clicked(self,point,CheckForRepeatedClick=False):
		self.setFocus()
		OldSelectedNames=self.SelectedNames
		if not self.SelectContinuously:
			self.SelectedNames=[]
			self.SelectedItems=[]

		self.SelectedNames+=self.GetNamesByPoint(point)

		if len(self.SelectedNames)>0:
			for [type,name,label_info] in OldSelectedNames:
				if type=='item':
					if self.ItemID.has_key(name):
						self.ItemID[name].SetSelected(False)
			if not self.SelectContinuously and CheckForRepeatedClick and OldSelectedNames==self.SelectedNames:
				self.SelectedNames=[]

			item_names=[]
			band_names=[]
			for [type,name,label_info] in self.SelectedNames:
				if type=='item':
					if label_info:
						item_names.append([name,label_info])
					else:
						item_names.append(name)
					if self.ItemID.has_key(name):
						self.ItemID[name].SetSelected(True)
				elif type=='band':
					band_names.append(name)
			
			if len(band_names)>0:
				partial_names=self.MapBand.GetSurroudingNames(band_names)
	
				if self.ItemID:
					for name in self.ItemID.keys():
						item=self.ItemID[name]
						item.clear()
				[minx,miny,maxx,maxy]=[x1,y1,x2,y2]=self.MapBand.boundingRectarray()
				self.ItemID=self.DrawGraphVizMap(self.mapdrawer,partial_names,self.caller,self.contents,offsety=maxy+50,leastx=maxx+100,leasty=maxy+100)
				for state in self.SavedState.keys():
					self.SetState(self.SavedState[state],state)
	
			for callback in self.SelectionCallbacks: #self.SelectionCallbacks
				if len(item_names)>0:
					callback(item_names)
		else:
			self.SelectedNames=OldSelectedNames

	def DClicked(self,point):
		self.setFocus()
		self.SelectedNames=self.GetNamesByPoint(point)
		names=[]
		for [type,name,label_info] in self.SelectedNames:
			if type=='item':
				names.append(name)
		if len(names)>0:
			for dclick_callback in self.OperationCallbacks:
				dclick_callback(names)

	def UnselectAll(self):
		for [type,name,label_info] in self.SelectedNames:
			if type=='item':
				if self.ItemID.has_key(name):
					self.ItemID[name].SetSelected(False)

	#This is about Key pressing/releasing
	def keyPressEvent(self,e):
		if e.key()==4129: #Ctrl
			self.SelectContinuously=True
		elif e.key()==4128: #Shift
			if self.SelectContinuously:
				self.SelectContinuously=False
			else:
				self.SelectContinuously=True

	def keyReleaseEvent(self,e):
		if e.key()==4129:
			self.SelectContinuously=False

	def SetElementOperations(self,ElementOperations):
		self.ElementOperations=ElementOperations

	def GetElementOperations(self,ElementOperations):
		return self.ElementOperations

	########## This is about Context menu #############
	def ContextMenu(self,point):
		if not self.contextMenu:
			self.contextMenu=QPopupMenu(self)
			self.contextMenu.setCheckable(True)

			caption=QLabel("<font color=darkblue><u><b>Operation</b></u></font>",self)
			caption.setAlignment(Qt.AlignCenter)
			self.contextMenu.insertItem(caption)
			for num in range(0,len(self.ElementOperations),1):
				self.ElementOperations[num][2]=self.contextMenu.insertItem(self.ElementOperations[num][0],self.ElementOperations[num][1],self.ElementOperations[num][3])

			"""TODO: COMMENT_OUT
			self.contextMenu.insertItem("&Clear Explanation",self.ClearExplanation,Qt.CTRL+Qt.Key_D)
			"""
			for pos in self.ContextMenuCheckInfo.keys():
				value=self.ContextMenuCheckInfo[pos]
				id=self.ElementOperations[pos][2]
				self.contextMenu.setItemChecked(id,value)
		self.contextMenu.exec_loop(QCursor.pos())

	def ToggleContextMenuChecked(self,pos):
		id=self.ElementOperations[pos][2]
		checked=self.contextMenu.isItemChecked(id)
		checked=not checked
		self.contextMenu.setItemChecked(id,checked)
		return checked

	def SetContextMenuChecked(self,pos,value):
		self.ContextMenuCheckInfo[pos]=value

	#############################################################
	# State
	def SetAlerted(self,names):
		if self.state_debug>0:
			print 'SetAlerted',names
		for name in self.AlertedNames:
			self.ItemID[name].SetAlerted(False)

		self.AlertedNames=[]
		for name in names:
			self.ItemID[name].SetAlerted(True)
			self.AlertedNames.append(name)

	def SetStateFeatures(self,id,penColor,brushColor,textColor,indicator=0):
		if self.state_debug>0:
			print 'SetStateFeatures',id,penColor,brushColor,textColor
		self.StateFeatures[id]=[penColor,brushColor,textColor,indicator]

	def SetState(self,names,state):
		if self.state_debug>0:
			print 'SetState',names,state
		self.SavedState[state]=names
		for name in names:
			if self.ItemID.has_key(name):
				self.SetStateByItem(self.ItemID[name],state)
			if self.BandItemID.has_key(name):
				self.SetStateByItem(self.BandItemID[name],state)

	def SetStateByItem(self,item,state):
		self.Item2State[self.CurrentStateName][item]=state
		if self.StateFeatures.has_key(state):
			item.SetState(self.StateFeatures[state])

	def GetState(self,item):
		if self.Item2State.has_key(item):
			return self.Item2State[item]

	def StartToSaveCurrentStatesByName(self,name=''):
		self.CurrentStateName=name
		self.Item2State[self.CurrentStateName]={}

	def RestoreStatesByName(self,name=''):
		self.ClearState()
		if self.Item2State.has_key(name):
			for item in self.Item2State[name].keys():
				self.SetStateByItem(item,self.Item2State[name][item])

	def ClearState(self):
		for name in self.ItemID.keys():
			self.ItemID[name].RestoreColors()

	def GetStateByItem(self,item):
		if self.state_debug>0:
			print 'GetStateByItem',item
		return item.GetState()

	def setExplanation(self,name,explanation_str):
		if self.state_debug>0:
			print 'setExplanation',name,explanation_str

		if self.ItemID.has_key(name):
			self.ItemID[name].SetExplanation(explanation_str)

	def ClearExplanation(self):
		if self.state_debug>0:
			print 'ClearExplanation'

		for name in self.ItemID.keys():
			self.ItemID[name].SetExplanation('')
				
if __name__=="__main__":
	def MakeName(i):
		return "Element:"+str(i)

	if 0:
		print ParseXDOTData("c 5 -black C 5 -black B 7 1003 4436 1010 4425 1018 4412 1022 4400 1054 4303 1050 4181 1045 4122")

	if 0:
		import random
		names=[]
		caller={}
		contents={}
		NumOfElement=50
		NumOfLines=NumOfElement*1.5
		for i in range(0,NumOfElement,1):
			names.append(MakeName(i))
			contents[MakeName(i)]="""hfwohfiowehofhweoif
hfoweihfiowhfoiweh
fweuiohfoiwehiofhweio
hfiowehiofhweofhoew"""
			caller[MakeName(i)]=[]
		for i in range(0,NumOfLines,1):
			src=random.randint(0,NumOfElement-1)
			dst=random.randint(0,NumOfElement-1)
			caller[MakeName(src)].append(MakeName(dst))
		GetGVData(names,caller,contents)
	
	if 0:
		import gv
		nodes=[]
		g = gv.digraph("G")
		n=gv.node(g,"hello")
		nodes.append(n)
		for i in range(0,100,1):
			m = gv.node(g,str(i))
			nodes.append(m)
			e = gv.edge(n,m)
		gv.layout(g, "dot")
		
		gv.render(g,"xdot","test.xdot")
		for node in nodes:
			print "pos=",gv.getv(node,"pos")
		#print "pos=",gv.getv(n,"pos")
		#print "pos=",gv.getv(e,"pos")
	
	
	if 0:
		g=gv.digraph("G")
		g=gv.read("test.dot")
		gv.layout(g, "dot")
		gv.render(g, "gif","test.gif")
		
	if 0:
		def main():
			app=QApplication()
			win= ()
			win.show()
			app.connect(app, SIGNAL("lastWindowClosed()")
			               , app
			               , SLOT("quit()")
			               )
			app.exec_loop()
		main()

	




