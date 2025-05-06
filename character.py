# -*- encoding: utf-8 -*-
import ue

@ue.uclass()
class MyCharacter(ue.Character):
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        ue.LogWarning('%s Character ReceiveBeginPlay!' % self)
        
        controller = self.GetWorld().GetPlayerController()
        controller.UnPossess()
        controller.Possess(self)
        self.EnableInput(controller)

        # 设置Enhanced Input组件
        # self.setup_enhanced_input(controller)

        # 移动
        # self.InputComponent.BindAxis('MoveForward', self._move_forward)
        # self.InputComponent.BindAxis('MoveRight', self._move_right)

        # 鼠标转向
        self.InputComponent.BindAxis('Turn', self._turn_right)
        self.InputComponent.BindAxis('LookUp', self._look_up)

        # 跳跃
        self.InputComponent.BindAction('Jump', ue.EInputEvent.IE_Pressed, self._jump)

        # 枪械
        self.weapon = None
        self.InputComponent.BindAction('Fire', ue.EInputEvent.IE_Pressed, self._fire)
        
        # 配置角色移动和旋转
        self.CharacterMovement.bOrientRotationToMovement = True  # 角色朝向移动方向
        self.bUseControllerRotationYaw = False  # 禁用控制器Yaw旋转控制角色
        # self.CharacterMovement.RotationRate = ue.FRotator(0, 540, 0)  # 调整旋转速度（0, 540, 0）
        
        # 配置摄像机以角色Mesh为中心旋转
        # 1. 获取SpringArm和Camera组件
        spring_arm_class = ue.FindClass("SpringArmComponent")  # 使用FindClass获取类引用
        camera_class = ue.FindClass("CameraComponent")  # 使用FindClass获取类引用
        
        spring_arm = self.GetComponentByClass(spring_arm_class)  # 获取SpringArm组件
        camera = self.GetComponentByClass(camera_class)  # 获取Camera组件
        
        if spring_arm and self.Mesh:
            # 2. 将SpringArm附着到角色Mesh而不是CapsuleComponent
            spring_arm.DetachFromComponent(ue.EDetachmentRule.KeepWorld)  # 先分离
            spring_arm.AttachToComponent(self.Mesh, "", ue.EAttachmentRule.SnapToTarget, 
                                        ue.EAttachmentRule.SnapToTarget, ue.EAttachmentRule.SnapToTarget, True)
            
            # 3. 配置SpringArm旋转设置
            spring_arm.bUsePawnControlRotation = True  # 使用Pawn的控制器旋转
            spring_arm.bInheritPitch = True
            spring_arm.bInheritYaw = True
            spring_arm.bInheritRoll = False
            
            # 4. 调整SpringArm相对位置和旋转
            spring_arm.SetRelativeLocation(ue.Vector(0, 0, 88))  # 调整到合适的高度，与网格体原点位置相关

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