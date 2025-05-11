# -*- encoding: utf-8 -*-
import ue
@ue.uclass()
class MyCharacter(ue.Character):
    # 添加弹药数属性
    MyAllBulletNumber = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    MyWeaopnBulletNumber = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")

    @ue.ufunction(BlueprintCallable=True, Category="Ammunition")
    def AddAmmunitionFromItem(self):
        """
        从物品中获取弹药的自定义事件
        这是一个可在蓝图中实现的事件，可以被Python代码调用
        在蓝图中会自动获取到一个整数参数
        """
        pass
    
    @ue.ufunction(params=(int,float))
    def FuncA(self,IntParams,FloatParams):
        pass

    @ue.ufunction(BlueprintCallable=True, Category="Ammunition")
    def AddAmmunition(self):
        """
        获得弹药函数，蓝图中会传入一个参数，但在Python定义中不显式声明
        注意：调用时需要在蓝图中传递一个整数参数
        
        在蓝图中调用时，这个函数会接受一个整数参数，表示要添加的弹药数量。
        函数返回更新后的总弹药数量。
        """
        # 通过上下文获取传入的弹药数量
        # 在实际调用时，这个参数会被传递，尽管我们在这里没有声明它
        import inspect
        # 获取当前帧和调用帧
        frame = inspect.currentframe()
        
        # 尝试从局部变量中获取传入的参数
        try:
            # 假设传入的第一个参数存储在某个位置
            if len(frame.f_locals) > 1:
                # 找到不是self的第一个参数
                for key, value in frame.f_locals.items():
                    if key != 'self':
                        ammo_count = int(value)
                        break
            else:
                ammo_count = 10  # 默认值
                ue.LogWarning("无法检测到传入的弹药数量，使用默认值10")
        except:
            ammo_count = 10  # 默认值
            ue.LogWarning("获取传入参数失败，使用默认值10")
        finally:
            if frame:
                del frame  # 避免循环引用
        
        # 更新角色的弹药数量
        old_ammo = self.MyAllBulletNumber
        self.MyAllBulletNumber += ammo_count
        
        # 尝试调用可在蓝图中实现的事件，传递添加的弹药数量
        try:
            # 触发事件，让蓝图有机会响应弹药变化
            if hasattr(self, 'AddAmmunitionFromItem'):
                self.AddAmmunitionFromItem()
                ue.LogWarning("成功触发AddAmmunitionFromItem事件")
        except Exception as e:
            ue.LogWarning(f"触发事件失败: {str(e)}")
        
        # 打印日志信息
        ue.LogWarning(f"获得弹药: +{ammo_count}, 旧弹药数: {old_ammo}, 新弹药数: {self.MyAllBulletNumber}")
        
        return self.MyAllBulletNumber
    
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        ue.LogWarning('%s Character ReceiveBeginPlay!' % self)

        # 导入protobuf
        import sys
        sys.path.append("C:\\Users\\wydx\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages")

        # 确保weapon属性初始化为None
        self.weapon = None
        
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
        
        # 添加Shift键的绑定
        self.InputComponent.BindKey("LeftShift", ue.EInputEvent.IE_Pressed, self._run_start)
        self.InputComponent.BindKey("LeftShift", ue.EInputEvent.IE_Released, self._run_stop)
        ue.LogWarning("在ReceiveBeginPlay中直接绑定LeftShift键成功")
        
        # 添加R键换弹的绑定
        self.InputComponent.BindKey("R", ue.EInputEvent.IE_Pressed, self._reload_weapon)
        ue.LogWarning("在ReceiveBeginPlay中直接绑定R键换弹成功")

        # 添加L键触发登录的绑定
        self.InputComponent.BindKey("L", ue.EInputEvent.IE_Pressed, self._trigger_login)
        ue.LogWarning("在ReceiveBeginPlay中直接绑定L键登录成功")

        # 枪械
        self.InputComponent.BindAction('Fire', ue.EInputEvent.IE_Pressed, self._fire)
        
        # 初始化玩家数据 - 尝试从服务器加载
        self._initialize_player_data()
        
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

    # 网络功能 - 玩家数据相关
    def _initialize_player_data(self):
        """初始化玩家数据 - 在游戏角色创建时尝试连接服务器"""
        try:
            # 导入网络模块
            import ue_site
            
            # 使用单例对象直接检查网络状态
            network_status = ue_site.network_status
            ue.LogWarning(f"[网络] 单例状态: {network_status.get_status_dict()}")
            
            # 如果网络尚未初始化，则尝试初始化
            if not network_status.is_network_initialized:
                ue.LogWarning("[网络] 网络客户端尚未初始化，尝试初始化...")
                ue_site.initialize_network_client()
                
                # 重新检查初始化状态
                if not network_status.is_network_initialized:
                    ue.LogWarning("[网络] 网络客户端初始化失败，稍后可通过按L键手动登录")
                    return
                else:
                    ue.LogWarning("[网络] 网络客户端已成功初始化")
            else:
                ue.LogWarning("[网络] 网络客户端已初始化")
                
            # 检查是否已连接
            if network_status.is_connected:
                ue.LogWarning("[网络] 已连接到服务器")
                return
                
            # 尝试连接服务器
            if network_status.network_client:
                ue.LogWarning("[网络] 游戏启动时尝试连接到服务器...")
                success = ue_site.try_connect_server()
                if success:
                    ue.LogWarning("[网络] 游戏启动连接服务器成功，可通过按L键登录")
                else:
                    ue.LogWarning("[网络] 游戏启动连接服务器失败，稍后可通过按L键重试")
            
        except ImportError as e:
            ue.LogError(f"[网络] 导入ue_site模块失败: {str(e)}")
        except Exception as e:
            ue.LogError(f"[网络] 初始化玩家数据时出错: {str(e)}")
            import traceback
            ue.LogError(f"[网络] 错误详情: {traceback.format_exc()}")
    
    @ue.ufunction(BlueprintCallable=True, Category="Network")
    def _trigger_login(self):
        """通过按键触发的登录函数"""
        try:
            # 导入网络模块并使用单例状态
            import ue_site
            import time
            
            # 获取单例网络状态
            network_status = ue_site.network_status
            ue.LogWarning(f"[网络] 登录前状态: {network_status.get_status_dict()}")
            
            # 先检查是否已经登录或者登录进行中
            if network_status.auth_status["is_authenticated"]:
                ue.LogWarning(f"[登录] 已经登录为用户: {network_status.auth_status['username']}，无需重复登录")
                return True
                
            if network_status.auth_status["login_in_progress"]:
                # 检查是否是过期的登录进行中状态
                current_time = time.time()
                if current_time - network_status.auth_status["last_login_attempt"] < 10.0:
                    ue.LogWarning("[登录] 登录操作正在进行中，请等待...")
                    return False
                else:
                    ue.LogWarning("[登录] 上一次登录请求已超时，将重新尝试")
                    # 继续执行登录逻辑
            
            # 确保网络已初始化
            if not network_status.is_network_initialized:
                ue.LogWarning("[网络] 网络客户端未初始化，尝试初始化")
                # 尝试初始化网络
                ue_site.initialize_network_client()
                
                # 再次检查初始化状态
                if not network_status.is_network_initialized:
                    ue.LogError("[网络] 网络客户端未初始化，无法登录")
                    return False
            
            # 检查网络连接状态，如果未连接则尝试连接
            if not network_status.is_connected or not network_status.network_client or not network_status.network_client.connected:
                ue.LogWarning("[网络] 网络客户端未连接，尝试连接到服务器...")
                connected = ue_site.try_connect_server()
                if not connected:
                    ue.LogError("[网络] 无法连接到服务器，登录失败")
                    return False
                ue.LogWarning("[网络] 已成功连接到服务器")
            
            # 使用默认账号密码登录
            username = "netease1"
            password = "123"
            ue.LogWarning(f"[登录] 按键触发登录 - 用户名: {username}")
            
            return self._login(username, password)
        except ImportError:
            ue.LogError("[网络] 导入ue_site模块失败，无法登录")
            return False
        except Exception as e:
            ue.LogError(f"触发登录时出错: {str(e)}")
            return False
    
    @ue.ufunction(BlueprintCallable=True, Category="Network", params=(str,str))
    def _login(self, username, password):
        """登录到游戏服务器"""
        try:
            import ue_site
            import time
            import sys
            
            # 获取网络状态单例
            network_status = ue_site.network_status
            
            # 先检查是否已经登录或者登录进行中
            if network_status.auth_status["is_authenticated"]:
                ue.LogWarning(f"[登录] 已经登录为用户: {network_status.auth_status['username']}，无需重复登录")
                return True
                
            if network_status.auth_status["login_in_progress"]:
                # 检查是否是过期的登录进行中状态
                current_time = time.time()
                if current_time - network_status.auth_status["last_login_attempt"] < 10.0:
                    ue.LogWarning("[登录] 登录操作正在进行中，请等待...")
                    # 主动处理一次网络消息
                    ue_site._process_network_internal()
                    ue_site._process_messages_internal()
                    return False
            
            # 确保网络客户端已初始化
            if not network_status.is_network_initialized:
                ue.LogError("[网络] 网络客户端未初始化，无法登录")
                return False
                
            # 确保网络客户端实例存在
            if not network_status.network_client:
                ue.LogError("[网络] 网络客户端对象不存在，无法登录")
                return False
            
            # 确保网络已连接
            if not network_status.is_connected or not network_status.network_client.connected:
                ue.LogWarning("[网络] 未连接到服务器，尝试重新连接")
                
                # 尝试重新连接
                if not ue_site.try_connect_server():
                    ue.LogError("[网络] 连接服务器失败，无法登录")
                    return False
            
            # 尝试登录
            success = ue_site.login(username, password)
            if success:
                ue.LogWarning(f"[登录] 正在尝试以用户名 {username} 登录...")
                
                # 登录请求发送成功后，立即主动处理一次消息
                # 确保网络消息能及时处理
                import threading
                def process_login_response():
                    # 等待短暂时间让服务器有机会响应
                    time.sleep(0.1)
                    # 直接调用消息处理函数
                    ue_site._process_network_internal()
                    ue_site._process_messages_internal()
                    # 记录登录状态
                    if ue_site.is_authenticated():
                        ue.LogWarning(f"[登录] 用户 {username} 登录成功！")
                    
                # 创建并启动线程
                threading.Thread(target=process_login_response).start()
            else:
                ue.LogError("[登录] 登录请求发送失败")
                
            return success
        except ImportError:
            ue.LogError("[网络] 导入ue_site模块失败，无法登录")
            return False
        except Exception as e:
            ue.LogError(f"[登录] 登录时出错: {str(e)}")
            import traceback
            ue.LogError(f"[登录] 错误详情: {traceback.format_exc()}")
            return False
    
    @ue.ufunction(BlueprintCallable=True, Category="Network")
    def _logout(self):
        """从游戏服务器登出"""
        try:
            import ue_site
            
            success = ue_site.logout()
            if success:
                ue.LogWarning("正在尝试登出...")
            else:
                ue.LogError("登出请求发送失败")
                
            return success
        except Exception as e:
            ue.LogError(f"登出时出错: {str(e)}")
            return False
    
    @ue.ufunction(BlueprintCallable=True, Category="Network")
    def _save_user_data(self):
        """保存用户数据到服务器"""
        try:
            import ue_site
            
            # 创建要保存的数据
            user_data = {
                "player_name": "玩家角色",
                "level": 10,
                "health": 100,
                "ammunition": self.MyAllBulletNumber,
                "weapon_ammo": self.MyWeaopnBulletNumber,
                "position": {
                    "x": self.GetActorLocation().X,
                    "y": self.GetActorLocation().Y,
                    "z": self.GetActorLocation().Z
                },
                "timestamp": time.time()
            }
            
            success = ue_site.save_user_data(user_data)
            if success:
                ue.LogWarning("正在保存用户数据...")
            else:
                ue.LogError("保存用户数据请求发送失败")
                
            return success
        except Exception as e:
            ue.LogError(f"保存用户数据时出错: {str(e)}")
            return False
    
    @ue.ufunction(BlueprintCallable=True, Category="Network")
    def _load_user_data(self):
        """从服务器加载用户数据"""
        try:
            import ue_site
            
            success = ue_site.load_user_data()
            if success:
                ue.LogWarning("正在加载用户数据...")
            else:
                ue.LogError("加载用户数据请求发送失败")
                
            return success
        except Exception as e:
            ue.LogError(f"加载用户数据时出错: {str(e)}")
            return False
    
    @ue.ufunction(BlueprintCallable=True, Category="Network")
    def _update_from_server_data(self):
        """从服务器数据更新角色属性"""
        try:
            import ue_site
            
            # 获取当前用户数据
            user_data = ue_site.get_user_data()
            if not user_data:
                ue.LogWarning("没有可用的用户数据")
                return False
                
            # 更新角色属性
            if "ammunition" in user_data:
                self.MyAllBulletNumber = user_data["ammunition"]
                
            if "weapon_ammo" in user_data:
                self.MyWeaopnBulletNumber = user_data["weapon_ammo"]
                
            ue.LogWarning(f"从服务器更新角色数据: 子弹={self.MyAllBulletNumber}, 弹匣={self.MyWeaopnBulletNumber}")
            return True
            
        except Exception as e:
            ue.LogError(f"更新角色属性时出错: {str(e)}")
            return False
    
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
                # 添加跑步动作的增强型输入绑定
                enh_input.BindActionByName("MyRun", ue.EInputEvent.IE_Pressed, self._run_start)
                enh_input.BindActionByName("MyRun", ue.EInputEvent.IE_Released, self._run_stop)
                ue.LogWarning("使用Enhanced Input特有方法绑定成功")
                # 添加换弹动作的增强型输入绑定
                enh_input.BindActionByName("MyReload", ue.EInputEvent.IE_Pressed, self._reload_weapon)
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
    def _run_start(self):
        """开始奔跑时设置较高的移动速度"""
        ue.LogWarning(f"_run_start 被调用!")
        if hasattr(self, 'CharacterMovement'):
            old_speed = self.CharacterMovement.MaxWalkSpeed
            self.CharacterMovement.MaxWalkSpeed = 1200.0
            ue.LogWarning(f"开始奔跑 - 速度从{old_speed}更改为1200")
        else:
            ue.LogError("无法找到CharacterMovement组件")
    
    def _run_stop(self):
        """停止奔跑时恢复正常移动速度"""
        ue.LogWarning(f"_run_stop 被调用!")
        if hasattr(self, 'CharacterMovement'):
            old_speed = self.CharacterMovement.MaxWalkSpeed
            self.CharacterMovement.MaxWalkSpeed = 600.0
            ue.LogWarning(f"停止奔跑 - 速度从{old_speed}更改为600")
        else:
            ue.LogError("无法找到CharacterMovement组件")
    
    @ue.ufunction(BlueprintCallable=True, Category="Ammunition")
    def _reload_weapon(self):
        """换弹功能 - 按R键触发"""
        ue.LogWarning(f"_reload_weapon 被调用! ")
        
        # 检查是否有武器
        if not hasattr(self, 'weapon') or self.weapon is None:
            ue.LogWarning("没有装备武器，无法换弹")
            return
        
        # 获取当前弹药数
        current_weapon_ammo = self.MyWeaopnBulletNumber
        current_total_ammo = self.MyAllBulletNumber
        
        # 计算需要补充的弹药数量
        max_weapon_capacity = 20
        ammo_needed = max_weapon_capacity - current_weapon_ammo
        
        if ammo_needed <= 0:
            ue.LogWarning("弹匣已满，无需换弹")
            return
        
        # 使用AnimBP PlayMontage功能
        try:
            # 获取换弹动画蒙太奇
            reload_montage = ue.LoadObject(ue.AnimMontage.Class(), 
                '/Game/Mannequin/Animations/My_Reload_Rifle_Hip1_Montage.My_Reload_Rifle_Hip1_Montage')
            
            if reload_montage and hasattr(self, 'Mesh'):
                # 使用PlayMontage，相当于蓝图中的PlayMontage节点
                if hasattr(ue, 'AnimInstance'):
                    # 获取动画实例
                    anim_instance = self.Mesh.GetAnimInstance()
                    if anim_instance:
                        # 播放动画蒙太奇
                        play_rate = 1.0
                        anim_instance.Montage_Play(reload_montage, play_rate)
                        # 可以在这里设置动画通知回调
                        ue.LogWarning("成功播放换弹动画蒙太奇")
                    else:
                        ue.LogWarning("无法获取角色的动画实例")
                else:
                    ue.LogWarning("ue模块中没有AnimInstance类")
            else:
                ue.LogWarning("无法加载换弹动画蒙太奇或角色网格体不可用")
        except Exception as e:
            ue.LogError(f"播放换弹动画失败: {str(e)}")
            
        # 检查总弹药是否足够
        if current_total_ammo >= ammo_needed:
            # 总弹药充足，补充到最大容量
            self.MyAllBulletNumber -= ammo_needed
            self.MyWeaopnBulletNumber = max_weapon_capacity
            ue.LogWarning(f"换弹完成：消耗{ammo_needed}发弹药，弹匣装填至{self.MyWeaopnBulletNumber}发，剩余总弹药{self.MyAllBulletNumber}发")
        else:
            # 总弹药不足，将所有剩余弹药装入武器
            self.MyWeaopnBulletNumber += current_total_ammo
            self.MyAllBulletNumber = 0
            ue.LogWarning(f"弹药不足：将剩余{current_total_ammo}发弹药全部装入，当前弹匣{self.MyWeaopnBulletNumber}发，总弹药已耗尽")