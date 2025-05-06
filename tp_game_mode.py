# -*- coding: utf-8 -*-

import ue
import tp_character
import actor_cube


# 默认的GameMode类，在ProjectSetting->GameMode项设置，
# 也可见Config/DefaultEngine.ini 里 GlobalDefaultGameMode=/Script/Engine.PyTPGameMode
class PyTPGameMode(ue.FindClass("GameModeBase")):
	# 注意！ 请不要在subclasing类的__init__ import 带有subclassing的模块，因为引擎要求load的时候不能GC（reload引起GC之前废弃的subclassing)
	def __init__(self):
		# 设置默认PawnClass为python定义的类
		# 这样UE会在使用了此GameMode的场景的PlayerStart出Spawn出对应Pawn
		self.DefaultPawnClass = tp_character.PyTPCharacter  # 如果使用C++中的类型则需要.Class(), 如ue.Character.Class()

	# 类似蓝图的BeginPlay, 请参考Client\Plugins\NePythonBinding\Doc\subclassing.html文档
	@ue.bp_func()
	def ReceiveBeginPlay(self):
		self.spawn_npc()
		self.spawn_cubes()

	def spawn_npc(self):
		ue_world = self.GetWorld()
		location = ue.Vector(320, -100, 430)
		rotation = ue.Rotator(0, 0, 0)
		char_cls = ue.Character.Class()  # 如果使用自己定义的subclassing类，则不需要后面的.Class(), 比如tp_character.PyTPCharacter
		npc_char = ue_world.SpawnActor(char_cls, location, rotation)

		# 设置mesh资源
		mesh = npc_char.Mesh
		mesh.SetSkeletalMesh(ue.LoadObject(ue.SkeletalMesh.Class(), '/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin'))
		mesh.SetRelativeLocation(ue.Vector(0.0, 0.0, -97.0))
		mesh.SetRelativeRotation(ue.Rotator(0.0, 270, 0.0))

		mesh.AnimationMode = ue.EAnimationMode.AnimationBlueprint  # 使用动画蓝图
		# 注意LoadClass参数的Path需要加上"_C"
		anim_bp_class = ue.LoadClass('/Game/Mannequin/Animations/ThirdPerson_AnimBP.ThirdPerson_AnimBP_C')
		# 设置Mesh使用的蓝图蓝图类具体是哪个
		mesh.SetAnimClass(anim_bp_class)

	def spawn_cubes(self):
		ue_world = self.GetWorld()
		location = ue.Vector(320, 100, 530)
		rotation = ue.Rotator(0, 0, 0)
		cube_actor = ue_world.SpawnActor(actor_cube.PyCubeActor, location, rotation)
		# 这里需要重新设置一下位置和旋转 ， why???, 因为cube_actor的RootComp到了ReceiveBeginPlay才被添加
		cube_actor.SetActorLocationAndRotation(location, rotation, False, False)

		location += ue.Vector(0, 0, 200)
		ue_world.SpawnActor(actor_cube.PyCubeActorWithSceneRoot, location, rotation)
