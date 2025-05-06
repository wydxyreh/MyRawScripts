# -*- coding: utf-8 -*-
import ue


# ue.FindClass("Character")等效 ue.Character.Class()
# 默认的Pawn类型， 被PyTPGameMode使用
# 大写的变量名基本是父类CPP里定义的属性
class PyTPCharacter(ue.FindClass("Character")):

	def __init__(self):
		# 设置胶囊体组件的尺寸（胶囊体用于碰撞）
		capsule_comp = self.CapsuleComponent
		capsule_comp.CapsuleRadius = 42.0
		capsule_comp.CapsuleHalfHeight = 96.0

		# 此类自己拥有的属性为小写+下划线
		self.base_turn_rate = 45.0
		self.base_lookup_rate = 45.0

		# 不使用Controller的旋转
		self.bUseControllerRotationPitch = False
		self.bUseControllerRotationYaw = False
		self.bUseControllerRotationRoll = False

		# 设置移动组件的属性
		char_move_comp = self.CharacterMovement
		# 始终朝向自己移动的方向
		char_move_comp.bOrientRotationToMovement = True
		char_move_comp.RotationRate = ue.Rotator(0.0, 540.0, 0.0)
		char_move_comp.JumpZVelocity = 600.0
		char_move_comp.AirControl = 0.2

		# 注意！！
		# AddActorComponent 里自带ReigsterComponent等需要操作
		# 它的调用时机是在ReceiveBeginPlay里，若放到__init__会有异常
		# 如果增加Component想放到__init__里，应该使用 CreateDefaultSubobject
		self.camera_boom = self.CreateDefaultSubobject(ue.SpringArmComponent.Class(), "CameraBoom")
		self.camera_boom.SetupAttachment(self.RootComponent)
		self.camera_boom.TargetArmLength = 300.0
		self.camera_boom.bUsePawnControlRotation = True

		self.follow_camera = self.CreateDefaultSubobject(ue.CameraComponent.Class(), "FollowCamera")
		self.follow_camera.SetupAttachment(self.camera_boom, 'SpringEndpoint')
		self.follow_camera.bUsePawnControlRotation = False

		# 设置Mesh资源
		self.Mesh.SetSkeletalMesh(ue.LoadObject(ue.SkeletalMesh.Class(), '/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin'))

		# 资源匹配胶囊体大小，适配朝向
		self.Mesh.SetRelativeLocation(ue.Vector(0.0, 0.0, -97.0))
		self.Mesh.SetRelativeRotation(ue.Rotator(0.0, 270, 0.0))

		self.Mesh.AnimationMode = ue.EAnimationMode.AnimationBlueprint  # 使用动画蓝图
		# 注意LoadClass参数的Path需要加上"_C"
		anim_bp_class = ue.LoadClass('/Game/Mannequin/Animations/ThirdPerson_AnimBP.ThirdPerson_AnimBP_C')
		# 设置Mesh使用的蓝图蓝图类具体是哪个
		self.Mesh.SetAnimClass(anim_bp_class)

	# 详见AActor::BeginPlay()中调用ReceiveBeginPlay
	# BlueprintImplementableEvent可以使用ue.bp_func 在python脚本implement
	@ue.bp_func()
	def ReceiveBeginPlay(self):

		# 下面是绑定输入控制事件
		# 注意只有ProjectSetting->Input里设置了对应的事件才会触发，配置保存在Config/DefaultInput.ini
		input_comp = self.GetWorld().GetPlayerController().InputComponent
		# self.Jump 为引擎定义的函数，此处可以使用NePy导出或者反射功能获取到
		input_comp.BindAction("Jump", ue.EInputEvent.IE_Pressed, self.Jump)
		input_comp.BindAction("Jump", ue.EInputEvent.IE_Released, self.StopJumping)

		# self.move_forward 为python定义的method
		input_comp.BindAxis("MoveForward", self.move_forward)
		input_comp.BindAxis("MoveRight", self.move_right)

		input_comp.BindAxis("Turn", self.AddControllerYawInput)
		input_comp.BindAxis("TurnRate", self.turn_at_rate)
		input_comp.BindAxis("LookUp", self.AddControllerPitchInput)
		input_comp.BindAxis("LookUpRate", self.look_up_at_rate)

	# 向前方向Add value, value为负则倒退
	def move_forward(self, value):
		ctrler = self.Controller
		rotation = ctrler.GetControlRotation()
		yaw_rotation = ue.Rotator(0.0, rotation.Yaw, 0.0)
		direction = ue.KismetMathLibrary.GetForwardVector(yaw_rotation)
		self.AddMovementInput(direction, value)

	# 类似上面的move_forward
	def move_right(self, value):
		ctrler = self.Controller
		rotation = ctrler.GetControlRotation()
		yaw_rotation = ue.Rotator(0.0, rotation.Yaw, 0.0)
		direction = ue.KismetMathLibrary.GetRightVector(yaw_rotation)
		self.AddMovementInput(direction, value)

	# 最终会控制相机朝向，左右健会触发
	def turn_at_rate(self, rate):
		delta_seconds = ue.GameplayStatics.GetWorldDeltaSeconds(self.GetWorld())
		self.AddControllerYawInput(rate * self.base_turn_rate * delta_seconds)

	def look_up_at_rate(self, rate):
		delta_seconds = ue.GameplayStatics.GetWorldDeltaSeconds(self.GetWorld())
		self.AddControllerPitchInput(rate * self.base_lookup_rate * delta_seconds)

	@ue.bp_func()
	def ReceiveTick(self, delta_time):
		# 注意！！！
		# 这个函数并不会触发，引擎中触发的条件没有通过（见AActor::Tick)
		# 建议通过PyGameInstance的on_tick来触发.
		pass
