from MapDrawer import *
import sys

def GetChildren(name,caller,level,got_children={}):
	if level==0:
		return
	got_children[name]=1
	if caller.has_key(name):
		for child in caller[name]:
			got_children[child]=1
			GetChildren(child,caller,level-1,got_children=got_children)

def GetLeveledData(names,caller,called,level=10):
	root=names[0]
	got_children={}
	GetChildren(root,caller,level,got_children=got_children)
	new_names=got_children.keys()
	return [new_names,caller,called]

def main( args ):
	a=QApplication(sys.argv)					    
	map_drawer=MapDrawer()
	names=caller=called=contents=comments=None
	fd=open("sample.map","rb")
	[names,caller,called,contents]=load(fd)
	fd.close()
	
	dst_nums={}
	for src in caller.keys():
		dst_num=len(caller[src])
		if not dst_nums.has_key(dst_num):
			dst_nums[dst_num]=1
		dst_nums[dst_num]+=1
	
	for dst_num in dst_nums.keys():
		print dst_num,dst_nums[dst_num]	

	for i in range(0,1000,1):
		names.append(str(i))
	import random
	random.seed()
	for i in range(0,len(names),1):
		name=names[i]
		if not caller.has_key(name):
			caller[name]=[]
		for j in range(0,3,1):
			k=random.randint(0,len(names)-1)
			caller[name].append(names[k])
	print 'len(names)=',len(names)
	print 'len(caller)=',len(caller)
	map_drawer.SetMapData(names,caller,called,comments,layout='graphviz')
	#map_drawer.Zoom(0.1,0.1)
	a.setMainWidget(map_drawer)
	map_drawer.show()  
	a.exec_loop()

main(sys.argv)