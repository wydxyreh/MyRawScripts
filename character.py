# -*- encoding: utf-8 -*-
import ue

@ue.uclass()
class MyCharacter(ue.Character):
    @ue.ufunction(override=True)
    # 声明组件属性
    @ue.uproperty(VisibleAnywhere=True, BlueprintReadOnly=True, Category="Camera")
    def CameraBoom(self): 
        return None
        
    @ue.uproperty(VisibleAnywhere=True, BlueprintReadOnly=True, Category="Camera")
    def FollowCamera(self): 
        return None
    
    def ReceiveBeginPlay(self):
        ue.LogWarning('%s Character ReceiveBeginPlay!' % self)
        
        controller = self.GetWorld().GetFirstPlayerController()
        if controller:
            controller.UnPossess()
            controller.Possess(self)
            self.EnableInput(controller)

        # 设置Enhanced Input组件
        # self.setup_enhanced_input(controller)

        # 移动
        # self.InputComponent.BindAxis('MoveForward', self._move_forward)
        # self.InputComponent.BindAxis('MoveRight', self._move_right)

        # 鼠标转向
        if self.InputComponent:
            self.InputComponent.BindAxis('Turn', self._turn_right)
            self.InputComponent.BindAxis('LookUp', self._look_up)

            # 跳跃
            self.InputComponent.BindAction('Jump', ue.EInputEvent.IE_Pressed, self._jump)

            # 枪械
            self.weapon = None
            self.InputComponent.BindAction('Fire', ue.EInputEvent.IE_Pressed, self._fire)
        
        # 配置角色移动和旋转
        if hasattr(self, 'CharacterMovement'):
            self.CharacterMovement.bOrientRotationToMovement = True  # 角色朝向移动方向
            self.bUseControllerRotationYaw = False  # 禁用控制器Yaw旋转控制角色
            self.CharacterMovement.RotationRate = ue.FRotator(0, 540, 0)  # 调整旋转速度

    def setup_enhanced_input(self, controller):
        ue.LogWarning(f"Hello setup_enhanced_input, {self}!")
        """设置Enhanced Input系统"""
        # 检查控制器是否有EnhancedInputLocalPlayerSubsystem
        subsystem = controller.GetLocalPlayer().GetSubsystem(ue.EnhancedInputLocalPlayerSubsystem.StaticClass())
        if not subsystem:
            ue.LogError("EnhancedInputLocalPlayerSubsystem不可用")
            return
            
        # 清除映射，防止重复
        subsystem.ClearMappingContext()
        
        # 加载输入映射上下文
        input_mapping_context = ue.LoadObject(
            ue.InputMappingContext.StaticClass(),
            "/Game/ThirdPerson/Input/IMC_Default.IMC_Default"
        )
        if not input_mapping_context:
            ue.LogError("无法加载输入映射上下文")
            return
        
        # 将映射上下文添加到子系统
        subsystem.AddMappingContext(input_mapping_context, 0)
        
        # 获取Enhanced Input组件
        enhanced_input = controller.FindComponentByClass(ue.EnhancedInputComponent.StaticClass())
        if not enhanced_input:
            ue.LogError("无法获取EnhancedInputComponent")
            return
            
        # 加载Input Actions
        move_action = ue.LoadObject(
            ue.InputAction.StaticClass(),
            "/Game/ThirdPerson/Input/Actions/IA_Move.IA_Move"
        )
        look_action = ue.LoadObject(
            ue.InputAction.StaticClass(),
            "/Game/ThirdPerson/Input/Actions/IA_Look.IA_Look"
        )
        jump_action = ue.LoadObject(
            ue.InputAction.StaticClass(),
            "/Game/ThirdPerson/Input/Actions/IA_Jump.IA_Jump"
        )
        fire_action = ue.LoadObject(
            ue.InputAction.StaticClass(),
            "/Game/ThirdPerson/Input/Actions/IA_Fire.IA_Fire"
        )
        
        # 绑定Input Actions到回调函数
        if move_action:
            enhanced_input.BindAction(move_action, ue.ETriggerEvent.Triggered, self, "_on_move")
        if look_action:
            enhanced_input.BindAction(look_action, ue.ETriggerEvent.Triggered, self, "_on_look")
        if jump_action:
            enhanced_input.BindAction(jump_action, ue.ETriggerEvent.Triggered, self, "_on_jump")
        if fire_action:
            enhanced_input.BindAction(fire_action, ue.ETriggerEvent.Triggered, self, "_on_fire")
    
    @ue.ufunction(override=True)
    def OnConstruction(self, transform):
        """在角色构建时设置摄像机组件"""
        super().OnConstruction(transform)
        self._setup_camera()
    
    def _setup_camera(self):
        """设置摄像机和弹簧臂组件"""
        # 创建弹簧臂组件
        if not self.CameraBoom:
            self.CameraBoom = ue.USpringArmComponent(self)
            self.CameraBoom.SetupAttachment(self.RootComponent)
            self.CameraBoom.TargetArmLength = 300.0  # 摄像机距离角色的距离
            self.CameraBoom.bUsePawnControlRotation = True  # 弹簧臂随着控制器旋转
            self.CameraBoom.bInheritPitch = True
            self.CameraBoom.bInheritYaw = True
            self.CameraBoom.bInheritRoll = False
            self.CameraBoom.SocketOffset = ue.FVector(0, 0, 50)  # 摄像机高度偏移
        
        # 创建摄像机组件
        if not self.FollowCamera:
            self.FollowCamera = ue.UCameraComponent(self)
            self.FollowCamera.SetupAttachment(self.CameraBoom, "SpringEndpoint")  # 将摄像机附加到弹簧臂末端
            self.FollowCamera.bUsePawnControlRotation = False  # 摄像机不随弹簧臂旋转
    
    @ue.ufunction
    def MyNewFunction(self):
        ue.LogWarning('%s Character MyNewFunction!' % self)

    # 移动
    def _move_forward(self, value):
        if value != 0:
            self.AddMovementInput(self.GetActorForwardVector(), value)

    def _move_right(self, value):
        if value != 0:
            self.AddMovementInput(self.GetActorRightVector(), value)
    
    # 鼠标转向
    def _turn_right(self, value):
        # self.AddControllerYawInput(value * 45 * ue.GetDeltaTime())
        self.AddControllerYawInput(value * self.MouseSpeed * ue.GetDeltaTime())

    def _look_up(self, value):
        # self.AddControllerPitchInput(value * 45 * ue.GetDeltaTime())
        self.AddControllerPitchInput(value * self.MouseSpeed * ue.GetDeltaTime())

    # 跳跃
    def _jump(self):
        self.Jump()

    # Enhanced Input回调函数
    def _on_move(self, value):
        # 获取value中的输入值 (FInputActionValue)
        input_value = value.Get()
        
        if isinstance(input_value, ue.FVector2D):
            # 前进/后退
            forward_direction = self.GetActorForwardVector()
            right_direction = self.GetActorRightVector()
            
            # 添加移动输入
            self.AddMovementInput(forward_direction, input_value.Y)
            self.AddMovementInput(right_direction, input_value.X)
    
    def _on_look(self, value):
        input_value = value.Get()
        
        if isinstance(input_value, ue.FVector2D):
            # 添加视角输入
            self.AddControllerYawInput(input_value.X)
            self.AddControllerPitchInput(input_value.Y * -1.0)  # 反转Y轴
    
    def _on_jump(self, value):
        self.Jump()
    
    def _on_fire(self, value):
        if self.weapon:
            self.weapon.fire()

    # 拾取武器
    def pick_up_weapon(self, weapon):
        # type: (ue.Actor) -> None
        attachment_rule = ue.EAttachmentRule.SnapToTarget
        weapon.AttachToComponent(self.Mesh, 'WeaponSocket',
            attachment_rule, attachment_rule, attachment_rule, True)
        
        self.weapon = weapon
    
    def _fire(self):
        if self.weapon:
            self.weapon.fire()