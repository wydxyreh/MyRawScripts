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
        self.setup_enhanced_input(controller)

        # 移动
        self.InputComponent.BindAxis('MoveForward', self._move_forward)
        self.InputComponent.BindAxis('MoveRight', self._move_right)

        # 鼠标转向
        self.InputComponent.BindAxis('Turn', self._turn_right)
        self.InputComponent.BindAxis('LookUp', self._look_up)

        # 跳跃
        self.InputComponent.BindAction('Jump', ue.EInputEvent.IE_Pressed, self._jump)
        
        # 直接添加Shift键的绑定
        self.InputComponent.BindKey("LeftShift", ue.EInputEvent.IE_Pressed, self._run_start)
        self.InputComponent.BindKey("LeftShift", ue.EInputEvent.IE_Released, self._run_stop)
        ue.LogWarning("在ReceiveBeginPlay中直接绑定LeftShift键成功")
        
        # 枪械
        self.weapon = None
        self.InputComponent.BindAction('Fire', ue.EInputEvent.IE_Pressed, self._fire)
        
        # 配置角色移动和旋转 - 针对相机方向移动进行优化
        self.CharacterMovement.bOrientRotationToMovement = True  # 角色朝向移动方向
        self.bUseControllerRotationYaw = False  # 禁用控制器Yaw旋转控制角色
        self.CharacterMovement.RotationRate = ue.Rotator(0, 540, 0)  # 较高的旋转速度，让角色更快地转向移动方向
        
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

        # 设置鼠标灵敏度
        self.MouseSpeed = 45.0  # 添加鼠标灵敏度属性

    def setup_enhanced_input(self, controller):
        ue.LogWarning(f"Hello setup_enhanced_input, {self}!")
        """设置Enhanced Input系统"""
        
        # 检查控制器是否有Enhanced Input组件
        if hasattr(controller, "EnhancedInputComponent"):
            enh_input = controller.EnhancedInputComponent
            ue.LogWarning("成功获取EnhancedInputComponent")
        elif hasattr(controller, "InputComponent"):
            # 尝试确定是否是EnhancedInputComponent
            enh_input = controller.InputComponent
            if hasattr(enh_input, "BindAction"):
                ue.LogWarning("使用常规InputComponent")
            else:
                ue.LogError("InputComponent不支持绑定动作")
                return
        else:
            ue.LogError("无法获取任何InputComponent")
            return
                
        # 设置默认行走和奔跑速度
        self.CharacterMovement.MaxWalkSpeed = 600.0  # 默认行走速度
        ue.LogWarning(f"初始行走速度设置为: {self.CharacterMovement.MaxWalkSpeed}")
        
        try:
            # Enhanced Input 绑定
            if hasattr(enh_input, "BindActionByName"):
                enh_input.BindActionByName("MyRun", ue.EInputEvent.IE_Pressed, self._run_start)
                enh_input.BindActionByName("MyRun", ue.EInputEvent.IE_Released, self._run_stop)
                ue.LogWarning("使用Enhanced Input特有方法绑定成功")
        except Exception as e:
            ue.LogError(f"绑定动作失败: {str(e)}")
            return
        
        ue.LogWarning("输入系统设置完成")
    
    @ue.ufunction
    def MyNewFunction(self):
        ue.LogWarning('%s Character MyNewFunction!' % self)

    # 移动 - 以相机方向为中心
    def _move_forward(self, value):
        if value != 0:
            # 获取控制器的旋转（即相机的方向）
            controller_rotation = self.Controller.GetControlRotation()
            # 只使用Yaw旋转创建新的旋转器（保持水平平面移动）
            yaw_rotation = ue.Rotator(0.0, controller_rotation.Yaw, 0.0)
            # 从旋转器获取前进方向向量 - 使用正确的数学库函数
            if hasattr(ue, "KismetMathLibrary"):
                # 如果存在KismetMathLibrary
                forward_direction = ue.KismetMathLibrary.GetForwardVector(yaw_rotation)
            else:
                # 备选方案：使用旋转直接获取前向向量
                # 在一些版本的NePythonBinding中可能不需要通过KismetMathLibrary
                forward_direction = yaw_rotation.GetForwardVector()
            
            # 应用移动输入
            self.AddMovementInput(forward_direction, value)

    def _move_right(self, value):
        if value != 0:
            # 获取控制器的旋转（即相机的方向）
            controller_rotation = self.Controller.GetControlRotation()
            # 只使用Yaw旋转创建新的旋转器（保持水平平面移动）
            yaw_rotation = ue.Rotator(0.0, controller_rotation.Yaw, 0.0)
            # 从旋转器获取右方向向量 - 使用正确的数学库函数
            if hasattr(ue, "KismetMathLibrary"):
                # 如果存在KismetMathLibrary
                right_direction = ue.KismetMathLibrary.GetRightVector(yaw_rotation)
            else:
                # 备选方案：使用旋转直接获取右向向量
                right_direction = yaw_rotation.GetRightVector()
                
            # 应用移动输入
            self.AddMovementInput(right_direction, value)
    
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

    # Enhanced Input回调函数 - 以相机方向为中心
    def _on_move(self, value):
        # 获取value中的输入值 (FInputActionValue)
        input_value = value.Get()
        
        # 在NePythonBinding中Vector2D代替FVector2D
        if hasattr(ue, "Vector2D") and isinstance(input_value, ue.Vector2D):
            vector2d_type = ue.Vector2D
        elif hasattr(ue, "FVector2D") and isinstance(input_value, ue.FVector2D):
            vector2d_type = ue.FVector2D
        else:
            # 不能确定具体类型，尝试直接使用
            # 假设输入值有X和Y属性
            x_value = getattr(input_value, "X", 0)
            y_value = getattr(input_value, "Y", 0)
            
            # 获取控制器的旋转（即相机的方向）
            controller_rotation = self.Controller.GetControlRotation()
            # 只使用Yaw旋转创建新的旋转器
            yaw_rotation = ue.Rotator(0.0, controller_rotation.Yaw, 0.0)
            
            # 从旋转器获取前进和右方向向量
            if hasattr(ue, "KismetMathLibrary"):
                forward_direction = ue.KismetMathLibrary.GetForwardVector(yaw_rotation)
                right_direction = ue.KismetMathLibrary.GetRightVector(yaw_rotation)
            else:
                forward_direction = yaw_rotation.GetForwardVector()
                right_direction = yaw_rotation.GetRightVector()
            
            # 添加移动输入
            self.AddMovementInput(forward_direction, y_value)
            self.AddMovementInput(right_direction, x_value)
    
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
    
    # 奔跑功能
    def _run_start(self, value=None):
        """开始奔跑时设置较高的移动速度"""
        ue.LogWarning(f"_run_start 被调用! 参数值: {value}")
        if hasattr(self, 'CharacterMovement'):
            old_speed = self.CharacterMovement.MaxWalkSpeed
            self.CharacterMovement.MaxWalkSpeed = 1200.0
            ue.LogWarning(f"开始奔跑 - 速度从{old_speed}更改为1200")
        else:
            ue.LogError("无法找到CharacterMovement组件")
    
    def _run_stop(self, value=None):
        """停止奔跑时恢复正常移动速度"""
        ue.LogWarning(f"_run_stop 被调用! 参数值: {value}")
        if hasattr(self, 'CharacterMovement'):
            old_speed = self.CharacterMovement.MaxWalkSpeed
            self.CharacterMovement.MaxWalkSpeed = 600.0
            ue.LogWarning(f"停止奔跑 - 速度从{old_speed}更改为600")
        else:
            ue.LogError("无法找到CharacterMovement组件")