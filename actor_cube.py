# -*- coding: utf-8 -*-

import ue


# Sublcassing Component 样例
class PyCubeMeshComp(ue.FindClass("StaticMeshComponent")):
	# @ue.bp_func()
	def __init__(self):
		self.SetStaticMesh(ue.LoadObject(ue.StaticMesh.Class(), '/Game/Geometry/Meshes/1M_Cube.1M_Cube'))


# Subclassing Actor 样例
class PyCubeActor(ue.FindClass("Actor")):
	@ue.bp_func()
	def ReceiveBeginPlay(self):
		# 跟蓝图不一样，c++中Actor是没有DefaultRootComponent，所以Python也需要自己添加RootComponent
		# 为什么不在__init__里添加RootComponent?
		# 因为Subclassing的对象（这里是PyCubeMeshComp的对象）若在__init__里创建，reload这个Class后再次GC时会Crash（找不到reload前的Class)
		self.mesh_root = self.AddActorRootComponent(PyCubeMeshComp, "RootComp")


# Subclassing Actor 样例, with a default root comp
class PyCubeActorWithSceneRoot(ue.Actor.Class()):
	def __init__(self):
		self.root_comp = self.CreateDefaultSubobject(ue.FindClass("SceneComponent"), "RootComp")  # 默认第一个SceneCompoent为Root

	@ue.bp_func()
	def ReceiveBeginPlay(self):
		self.mesh_comp = self.AddActorComponent(PyCubeMeshComp, "MeshComp", self.root_comp)
