# -*- encoding: utf-8 -*-
import ue
@ue.uclass(BlueprintType=True)
class MyCharacter(ue.Character):
    # 定义元类，帮助Unreal Engine在蓝图系统中正确识别此类
    @classmethod
    def _unreal_skeleton_class(cls):
        # 这里指定我们的Python类要使用的真实蓝图类型
        # 使用与动画蓝图尝试转换到的相同类型
        return '/Game/ThirdPersonCPP/Blueprints/MyCharacterBP.MyCharacterBP_C'
    
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        ue.LogWarning('%s Character ReceiveBeginPlay!' % self)

        # 导入protobuf
        import sys
        sys.path.append("C:\\Users\\wydx\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages")

        # 确保weapon属性初始化为None
        self.weapon = None
        
        # 创建战斗数据UI
        widget_class = ue.LoadClass('/Game/ThirdPersonCPP/Blueprints/UI/BattleDataUI.BattleDataUI_C')
        if widget_class:
            # 正确使用GetPlayerController方法获取第一个玩家控制器
            battle_ui = ue.WidgetBlueprintLibrary.Create(self.GetWorld(), widget_class, self.GetWorld().GetPlayerController(0))
            # 添加到视口
            if battle_ui:
                # 设置UI引用角色
                if hasattr(battle_ui, 'MyCharacterBPUI'):
                    battle_ui.MyCharacterBPUI = self
                    ue.LogWarning('成功设置UI对角色的引用')
                else:
                    ue.LogWarning('UI没有MyCharacterBPUI属性，尝试使用SetCharacterReference')
                    # 尝试调用UI可能存在的设置角色引用的方法
                    if hasattr(battle_ui, 'SetCharacterReference'):
                        battle_ui.SetCharacterReference(self)
                        ue.LogWarning('通过SetCharacterReference方法设置角色引用')
                    
                battle_ui.AddToViewport()
                ue.LogWarning('成功创建并添加BattleDataUI到视口')
                
                # 保存UI引用以便后续使用
                self.battle_ui = battle_ui
            else:
                ue.LogError('创建BattleDataUI失败')
        else:
            ue.LogError('加载BattleDataUI类失败')
        
        # 调用属性初始化函数
        self._init_player_attributes()
        
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
        
        # 添加U键保存数据的绑定
        self.InputComponent.BindKey("U", ue.EInputEvent.IE_Pressed, self._save_game_data)
        ue.LogWarning("在ReceiveBeginPlay中直接绑定U键保存数据成功")
        
        # 添加I键加载数据的绑定
        self.InputComponent.BindKey("I", ue.EInputEvent.IE_Pressed, self._load_game_data)
        ue.LogWarning("在ReceiveBeginPlay中直接绑定I键加载数据成功")

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

        # 配置委托
        self.GetKilled.Add(self.AddKilledNumbers)
        self.ItemAddAmmunition.Add(self.AddAmmunitionFromItem)
        self.ItemAddHP.Add(self.AddHPFromItem)
        self.TickAddAmmunition.Add(self.AddAmmunitionFromTick)

    
    # 玩家属性
    MaxHP = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    CurrentHP = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    MaxEXP = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    CurrentEXP = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    AllBulletNumber = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    WeaopnBulletNumber = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    KilledEnemies = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")

    # 委托（自定义事件）
    # 击杀敌数
    GetKilled = ue.udelegate(BlueprintCallable=True, params=((int, 'KilledNumber'),))
    # self.GetKilled.Broadcast(10)
    # 道具回复弹药
    ItemAddAmmunition = ue.udelegate(BlueprintCallable=True, params=((int, 'AddAmmunitionNums'),))
    # 道具回复生命值
    ItemAddHP = ue.udelegate(BlueprintCallable=True, params=((int, 'AddHP'),))
    # 每秒回复弹药
    TickAddAmmunition = ue.udelegate(BlueprintCallable=True, params=())

    def AddKilledNumbers(self, killed_number):
        """处理敌人击杀事件的回调函数"""
        self.KilledEnemies += killed_number
        ue.LogWarning(f"KilledEnemies:{self.KilledEnemies}")

    def AddAmmunitionFromItem(self, add_ammunition_nums):
        """处理道具回复弹药事件的回调函数"""
        self.AllBulletNumber += add_ammunition_nums
        ue.LogWarning(f"AllBulletNumber:{self.AllBulletNumber}")
    
    def AddAmmunitionFromTick(self):
        """处理每秒自动回复弹药的回调函数"""
        self.AllBulletNumber += 1
        ue.LogWarning(f"[自动回复] 弹药+1，当前总弹药数:{self.AllBulletNumber}")
    
    def AddHPFromItem(self, add_hp):
        """
        处理道具回复生命值事件的回调函数
        实现蓝图中的道具回血逻辑：
        1. 计算新的生命值 = 当前生命值 + 恢复血量
        2. 如果新的生命值超过最大生命值，则将当前生命值设为最大生命值
        3. 否则将当前生命值设为新的生命值
        
        参数:
            add_hp (int): 道具恢复的血量值
        """
        # 计算新的生命值
        new_hp = self.CurrentHP + add_hp
        
        # 检查是否超过最大生命值
        if new_hp >= self.MaxHP:
            # 如果超过最大生命值，则将当前生命值设为最大生命值
            self.CurrentHP = self.MaxHP
        else:
            # 否则将当前生命值设为新的生命值
            self.CurrentHP = new_hp
        
        # 记录日志
        ue.LogWarning(f"道具回血效果: +{add_hp} HP，当前生命值: {self.CurrentHP}/{self.MaxHP}")
    
    def _check_network_ready(self):
        """
        检查网络客户端是否已初始化并已连接到服务器
        如果未初始化则尝试初始化，如果未连接则尝试连接
        
        返回: (bool, str) - (是否就绪, 错误信息)
        """
        try:
            import ue_site
            
            # 获取网络状态单例
            network_status = ue_site.network_status
            
            # 检查网络是否初始化
            if not network_status.is_network_initialized:
                ue.LogWarning("[网络] 网络客户端尚未初始化，尝试初始化...")
                ue_site.initialize_network_client()
                
                # 重新检查初始化状态
                if not network_status.is_network_initialized:
                    return False, "[网络] 网络客户端初始化失败"
                else:
                    ue.LogWarning("[网络] 网络客户端已成功初始化")
            
            # 检查网络客户端和客户端实体是否存在
            if not network_status.network_client or not network_status.client_entity:
                return False, "[网络] 网络客户端组件未正确初始化"
            
            # 检查是否已连接
            if not network_status.is_connected or not network_status.network_client.connected:
                ue.LogWarning("[网络] 网络客户端未连接，尝试连接到服务器...")
                connected = ue_site.try_connect_server()
                if not connected:
                    return False, "[网络] 无法连接到服务器"
                
                # 确保连接状态已更新
                if not network_status.is_connected or not network_status.network_client.connected:
                    return False, "[网络] 连接状态不一致，请重试"
                    
                ue.LogWarning("[网络] 已成功连接到服务器")
            
            return True, ""
        except ImportError:
            return False, "[网络] 导入ue_site模块失败"
        except Exception as e:
            import traceback
            error_msg = f"[网络] 检查网络就绪状态时出错: {str(e)}"
            ue.LogError(f"{error_msg}\n{traceback.format_exc()}")
            return False, error_msg
    
    # 网络功能 - 玩家数据相关
    def _initialize_player_data(self):
        """初始化玩家数据 - 在游戏角色创建时尝试连接服务器"""
        try:
            import ue_site
            
            # 使用单例对象直接检查网络状态
            network_status = ue_site.network_status
            ue.LogWarning(f"[网络] 单例状态: {network_status.get_status_dict()}")
            
            # 检查网络是否已初始化并连接
            is_ready, error_msg = self._check_network_ready()
            
            if not is_ready:
                ue.LogWarning(f"{error_msg}，稍后可通过按L键手动登录")
                return
            
            ue.LogWarning("[网络] 游戏启动连接服务器成功，可通过按L键登录")
            
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
            import ue_site
            import time
            
            # 获取单例网络状态
            network_status = ue_site.network_status
            ue.LogWarning(f"[网络] 登录前状态: {network_status.get_status_dict()}")
            
            # 先检查是否已经登录
            # 两种方式检查登录状态: 通过network_status和通过client_entity
            if network_status.auth_status["is_authenticated"]:
                ue.LogWarning(f"[登录] 已经登录为用户: {network_status.auth_status['username']}，无需重复登录")
                return True
            
            # 如果有client_entity，还需要检查其认证状态
            if (network_status.client_entity and 
                hasattr(network_status.client_entity, 'authenticated') and 
                network_status.client_entity.authenticated):
                # 同步客户端状态
                network_status.auth_status["is_authenticated"] = True
                network_status.auth_status["username"] = network_status.client_entity.username
                
                # 同步token信息
                if hasattr(network_status.client_entity, 'token'):
                    network_status.auth_status["token"] = network_status.client_entity.token
                    
                ue.LogWarning(f"[登录] 已经通过客户端实体验证为用户: {network_status.client_entity.username}，无需重复登录")
                return True
                
            if network_status.auth_status["login_in_progress"]:
                # 检查是否是过期的登录进行中状态
                current_time = time.time()
                # 如果last_login_attempt不存在或为0，设置一个默认值
                last_attempt = network_status.auth_status.get("last_login_attempt", 0)
                if current_time - last_attempt < 10.0:
                    ue.LogWarning("[登录] 登录操作正在进行中，请等待...")
                    # 在等待时主动处理一次网络消息
                    ue_site._process_network_internal()
                    ue_site._process_messages_internal()
                    return False
                else:
                    ue.LogWarning("[登录] 上一次登录请求已超时，将重新尝试")
                    # 重置登录进行中状态
                    network_status.auth_status["login_in_progress"] = False
                    # 继续执行登录逻辑
            
            # 检查网络是否已初始化并连接
            is_ready, error_msg = self._check_network_ready()
            if not is_ready:
                ue.LogError(f"{error_msg}，无法登录")
                return False
            
            # 使用默认账号密码登录
            username = "netease1"
            password = "123"
            ue.LogWarning(f"[登录] 按键触发登录 - 用户名: {username}")
            
            # 立即处理网络消息，确保连接状态最新
            ue_site._process_network_internal()
            
            return self._login(username, password)
        except ImportError:
            ue.LogError("[网络] 导入ue_site模块失败，无法登录")
            return False
        except Exception as e:
            ue.LogError(f"触发登录时出错: {str(e)}")
            import traceback
            ue.LogError(f"[登录] 错误详情: {traceback.format_exc()}")
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
            
            # 先检查是否已经登录
            # 通过network_status和client_entity双重检查认证状态
            if network_status.auth_status["is_authenticated"]:
                ue.LogWarning(f"[登录] 已经登录为用户: {network_status.auth_status['username']}，无需重复登录")
                return True
            
            if (network_status.client_entity and 
                hasattr(network_status.client_entity, 'authenticated') and 
                network_status.client_entity.authenticated):
                # 同步客户端状态到network_status
                if hasattr(network_status.client_entity, 'auth_status'):
                    network_status.auth_status["is_authenticated"] = True
                    network_status.auth_status["username"] = network_status.client_entity.username
                    network_status.auth_status["login_time"] = network_status.client_entity.auth_status.get("login_time")
                    network_status.auth_status["last_token_refresh"] = network_status.client_entity.auth_status.get("last_token_refresh")
                    
                    # 同步token信息
                    if hasattr(network_status.client_entity, 'token'):
                        network_status.auth_status["token"] = network_status.client_entity.token
                    
                    ue.LogWarning(f"[登录] 已经通过客户端实体验证为用户: {network_status.client_entity.username}，同步认证状态")
                
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
            
            # 检查网络是否已初始化并连接
            is_ready, error_msg = self._check_network_ready()
            if not is_ready:
                ue.LogError(f"{error_msg}，无法登录")
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
                    
                    # 检查登录状态并记录日志
                    if ue_site.is_authenticated():
                        ue.LogWarning(f"[登录] 用户 {username} 登录成功！")
                        
                        # 检查auth_status的新增属性值
                        if network_status.auth_status["login_time"]:
                            login_time_str = time.strftime("%Y-%m-%d %H:%M:%S", 
                                                time.localtime(network_status.auth_status["login_time"]))
                            ue.LogWarning(f"[登录] 登录时间: {login_time_str}")
                    
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
            import time
            
            # 创建要保存的数据
            user_data = {
                "player_name": "玩家角色",
                "level": 10,
                "health": 100,
                "MaxHP": self.MaxHP,
                "CurrentHP": self.CurrentHP,
                "MaxEXP": self.MaxEXP,
                "CurrentEXP": self.CurrentEXP,
                "AllBulletNumber": self.AllBulletNumber,
                "WeaopnBulletNumber": self.WeaopnBulletNumber,
                "KilledEnemies": self.KilledEnemies,
                "position": {
                    "x": self.GetActorLocation().X,
                    "y": self.GetActorLocation().Y,
                    "z": self.GetActorLocation().Z
                },
                "timestamp": time.time()
            }
            
            # 记录保存前的数据快照
            self.last_saved_data = user_data.copy()
            
            success = ue_site.save_user_data(user_data)
            if success:
                ue.LogWarning(f"正在保存用户数据: {user_data}")
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
            
            # 获取当前用户数据 - 使用新版get_user_data函数
            user_data = ue_site.get_user_data()
            if not user_data:
                ue.LogWarning("[更新] 没有可用的用户数据或数据未初始化")
                return False
                
            # 验证数据格式
            if not isinstance(user_data, dict):
                ue.LogError(f"[更新] 用户数据格式错误，预期字典类型，实际为: {type(user_data)}")
                return False
            
            # 获取网络状态对象来检查数据有效性
            network_status = ue_site.network_status
            if (not network_status.client_entity):
                ue.LogWarning("[更新] 客户端实体不存在")
                return False
                
            # 检查user_data_exists属性是否存在
            user_data_exists = False
            if hasattr(network_status.client_entity, 'user_data_exists'):
                user_data_exists = network_status.client_entity.user_data_exists
            else:
                # 如果属性不存在但有user_data，也认为数据存在
                user_data_exists = hasattr(network_status.client_entity, 'user_data') and network_status.client_entity.user_data
                
            if not user_data_exists:
                ue.LogWarning("[更新] 用户数据不存在或未初始化")
                return False
            
            # 保存加载前的数据快照，用于对比显示
            old_ammo = self.AllBulletNumber
            old_weapon_ammo = self.WeaopnBulletNumber
            
            # 更新角色属性 - 添加类型检查和安全转换
            # 更新MaxHP
            if "MaxHP" in user_data:
                try:
                    self.MaxHP = int(user_data["MaxHP"])
                except (TypeError, ValueError):
                    ue.LogWarning(f"[更新] 无法将MaxHP值 '{user_data['MaxHP']}' 转换为整数，使用原值")
            
            # 更新CurrentHP
            if "CurrentHP" in user_data:
                try:
                    self.CurrentHP = int(user_data["CurrentHP"])
                except (TypeError, ValueError):
                    ue.LogWarning(f"[更新] 无法将CurrentHP值 '{user_data['CurrentHP']}' 转换为整数，使用原值")
            
            # 更新MaxEXP
            if "MaxEXP" in user_data:
                try:
                    self.MaxEXP = int(user_data["MaxEXP"])
                except (TypeError, ValueError):
                    ue.LogWarning(f"[更新] 无法将MaxEXP值 '{user_data['MaxEXP']}' 转换为整数，使用原值")
            
            # 更新CurrentEXP
            if "CurrentEXP" in user_data:
                try:
                    self.CurrentEXP = int(user_data["CurrentEXP"])
                except (TypeError, ValueError):
                    ue.LogWarning(f"[更新] 无法将CurrentEXP值 '{user_data['CurrentEXP']}' 转换为整数，使用原值")
            
            # 更新KilledEnemies
            if "KilledEnemies" in user_data:
                try:
                    self.KilledEnemies = int(user_data["KilledEnemies"])
                except (TypeError, ValueError):
                    ue.LogWarning(f"[更新] 无法将KilledEnemies值 '{user_data['KilledEnemies']}' 转换为整数，使用原值")
            
            # 更新子弹数
            if "AllBulletNumber" in user_data:
                try:
                    self.AllBulletNumber = int(user_data["AllBulletNumber"])
                except (TypeError, ValueError):
                    ue.LogWarning(f"[更新] 无法将弹药值 '{user_data['AllBulletNumber']}' 转换为整数，使用原值")
                
            if "WeaopnBulletNumber" in user_data:
                try:
                    self.WeaopnBulletNumber = int(user_data["WeaopnBulletNumber"])
                except (TypeError, ValueError):
                    ue.LogWarning(f"[更新] 无法将弹匣值 '{user_data['WeaopnBulletNumber']}' 转换为整数，使用原值")
            
            # 添加保存时间的检查和显示    
            save_time = user_data.get("save_time", "未知")
            
            ue.LogWarning(f"[更新] 从服务器更新角色数据:")
            ue.LogWarning(f"[更新] - 生命值: {self.CurrentHP}/{self.MaxHP}")
            ue.LogWarning(f"[更新] - 经验值: {self.CurrentEXP}/{self.MaxEXP}")
            ue.LogWarning(f"[更新] - 子弹从 {old_ammo} 更新为 {self.AllBulletNumber}")
            ue.LogWarning(f"[更新] - 弹匣从 {old_weapon_ammo} 更新为 {self.WeaopnBulletNumber}")
            ue.LogWarning(f"[更新] - 击杀敌人数: {self.KilledEnemies}")
            ue.LogWarning(f"[更新] 存档保存时间: {save_time}")
            
            # 打印完整的加载数据
            ue.LogWarning(f"[更新] 加载的完整数据: {user_data}")
            return True
            
        except Exception as e:
            ue.LogError(f"[更新] 更新角色属性时出错: {str(e)}")
            import traceback
            ue.LogError(f"[更新] 错误详情: {traceback.format_exc()}")
            return False
    
    @ue.ufunction(BlueprintCallable=True, Category="Network")
    def _save_game_data(self):
        """U按键触发的保存游戏数据功能"""
        try:
            import ue_site
            import time
            import threading
            
            # 检查是否已登录
            is_authenticated = ue_site.is_authenticated()
            if not is_authenticated:
                ue.LogWarning("[保存] 用户未登录，无法保存游戏数据。请先按L键登录")
                return False
            
            ue.LogWarning("====== U按键触发保存游戏数据 ======")
            
            # 创建当前游戏状态的数据对象
            game_data = {
                "player_name": "玩家角色",
                "level": 10,
                "health": 100,
                "MaxHP": self.MaxHP,
                "CurrentHP": self.CurrentHP,
                "MaxEXP": self.MaxEXP,
                "CurrentEXP": self.CurrentEXP,
                "AllBulletNumber": self.AllBulletNumber,
                "WeaopnBulletNumber": self.WeaopnBulletNumber,
                "KilledEnemies": self.KilledEnemies,
                "position": {
                    "x": self.GetActorLocation().X,
                    "y": self.GetActorLocation().Y,
                    "z": self.GetActorLocation().Z
                },
                "save_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": time.time()
            }
            
            # 打印保存前的数据状态
            ue.LogWarning(f"[保存] 当前角色状态:")
            ue.LogWarning(f"[保存] - 生命值: {self.CurrentHP}/{self.MaxHP}")
            ue.LogWarning(f"[保存] - 经验值: {self.CurrentEXP}/{self.MaxEXP}")
            ue.LogWarning(f"[保存] - 总弹药: {self.AllBulletNumber}")
            ue.LogWarning(f"[保存] - 当前弹匣: {self.WeaopnBulletNumber}")
            ue.LogWarning(f"[保存] - 击杀敌人数: {self.KilledEnemies}")
            ue.LogWarning(f"[保存] - 位置: ({game_data['position']['x']:.2f}, {game_data['position']['y']:.2f}, {game_data['position']['z']:.2f})")
            
            # 获取网络状态单例
            network_status = ue_site.network_status
            
            # 保存数据 - 使用ue_site中的方法
            success = ue_site.save_user_data(game_data)
            
            if success:
                ue.LogWarning("[保存] 游戏数据保存请求已发送")
                ue.LogWarning(f"[保存] 完整保存数据: {game_data}")
                
                # 设置一个定时器来检查保存操作的结果
                def check_save_result():
                    # 每0.5秒检查一次保存状态，最多检查10次（5秒）
                    max_attempts = 10
                    attempts = 0
                    
                    while attempts < max_attempts:
                        # 调用消息处理函数，确保最新消息得到处理
                        ue_site._process_network_internal()
                        ue_site._process_messages_internal()
                        
                        time.sleep(0.5)
                        attempts += 1
                        
                        # 检查保存状态 - 同时检查NetworkStatus和ClientEntity的状态
                        save_in_progress = network_status.save_status["in_progress"]
                        
                        # 检查ClientEntity的data_operations状态
                        if network_status.client_entity and hasattr(network_status.client_entity, 'data_operations'):
                            client_save_op = network_status.client_entity.data_operations.get("save", {})
                            client_save_pending = client_save_op.get("pending", False)
                            
                            # 判断两边的状态
                            if not save_in_progress or not client_save_pending:
                                # 保存操作已完成
                                save_success = network_status.save_status["success"] or client_save_op.get("success", False)
                                
                                if save_success:
                                    ue.LogWarning("[保存] ✓ 保存操作已完成: 数据已成功保存到服务器")
                                    ue.LogWarning(f"[保存] 保存状态: {network_status.save_status['message']}")
                                    ue.LogWarning(f"[保存] 保存时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                                else:
                                    error_message = network_status.save_status["message"] or client_save_op.get("error_message", "未知错误")
                                    ue.LogError(f"[保存] ✗ 保存操作失败: {error_message}")
                                
                                ue.LogWarning("=================================")
                                break
                        
                        ue.LogWarning(f"[保存] 等待保存操作完成... ({attempts}/{max_attempts})")
                        
                        # 每次检查都主动处理一次消息
                        ue_site._process_network_internal()
                        ue_site._process_messages_internal()
                    
                    if attempts >= max_attempts:
                        ue.LogError("[保存] 保存操作超时，未收到服务器确认")
                        # 重置保存状态，防止卡住
                        network_status.save_status["in_progress"] = False
                        if network_status.client_entity and hasattr(network_status.client_entity, 'data_operations'):
                            if "save" in network_status.client_entity.data_operations:
                                network_status.client_entity.data_operations["save"]["pending"] = False
                        ue.LogWarning("=================================")
                
                # 启动定时器线程
                threading.Thread(target=check_save_result).start()
            else:
                ue.LogError("[保存] 保存游戏数据请求发送失败")
                ue.LogWarning("=================================")
                
            return success
        except Exception as e:
            ue.LogError(f"[保存] 触发保存游戏数据时出错: {str(e)}")
            import traceback
            ue.LogError(f"[保存] 错误详情: {traceback.format_exc()}")
            ue.LogWarning("=================================")
            return False
    
    @ue.ufunction(BlueprintCallable=True, Category="Network")
    def _load_game_data(self):
        """I按键触发的加载游戏数据功能"""
        try:
            import ue_site
            import time
            import threading
            
            # 检查是否已登录
            is_authenticated = ue_site.is_authenticated()
            if not is_authenticated:
                ue.LogWarning("[加载] 用户未登录，无法加载游戏数据。请先按L键登录")
                return False
            
            ue.LogWarning("====== I按键触发加载游戏数据 ======")
            
            # 打印加载前的数据状态
            ue.LogWarning(f"[加载] 当前角色状态:")
            ue.LogWarning(f"[加载] - 总弹药: {self.AllBulletNumber}")
            ue.LogWarning(f"[加载] - 当前弹匣: {self.WeaopnBulletNumber}")
            
            # 获取网络状态单例
            network_status = ue_site.network_status
            
            # 先从服务器加载最新数据
            success = ue_site.load_user_data()
            
            if success:
                ue.LogWarning("[加载] 游戏数据加载请求已发送，正在处理...")
                
                # 设置一个检查加载状态的定时器
                def check_load_result():
                    # 每0.5秒检查一次加载状态，最多检查10次（5秒）
                    max_attempts = 10
                    attempts = 0
                    
                    while attempts < max_attempts:
                        # 调用消息处理函数，确保最新消息得到处理
                        ue_site._process_network_internal()
                        ue_site._process_messages_internal()
                        
                        time.sleep(0.5)
                        attempts += 1
                        
                        # 检查加载状态 - 使用新的data_operations状态机制
                        load_in_progress = network_status.load_status["in_progress"]
                        
                        # 检查ClientEntity的data_operations状态
                        if network_status.client_entity and hasattr(network_status.client_entity, 'data_operations'):
                            client_load_op = network_status.client_entity.data_operations.get("load", {})
                            client_load_pending = client_load_op.get("pending", False)
                            
                            # 判断两边的状态
                            if not load_in_progress or not client_load_pending:
                                # 加载操作已完成
                                load_success = network_status.load_status["success"] or client_load_op.get("success", False)
                                
                                if load_success:
                                    ue.LogWarning("[加载] ✓ 加载操作已完成: 数据已成功从服务器获取")
                                    ue.LogWarning(f"[加载] 加载状态: {network_status.load_status['message']}")
                                    
                                    # 检查user_data_exists属性
                                    user_data_exists = hasattr(network_status.client_entity, 'user_data_exists') and network_status.client_entity.user_data_exists
                                    
                                    if user_data_exists:
                                        # 从加载的数据更新角色
                                        update_success = self._update_from_server_data()
                                        
                                        if update_success:
                                            ue.LogWarning("[加载] 已成功更新角色数据")
                                            
                                            # 获取当前用户数据
                                            user_data = ue_site.get_user_data()
                                            if user_data and "save_time" in user_data:
                                                ue.LogWarning(f"[加载] 加载的存档时间: {user_data.get('save_time', '未知')}")
                                        else:
                                            ue.LogError("[加载] 更新角色数据失败")
                                    else:
                                        ue.LogError("[加载] 用户数据不存在或未初始化")
                                else:
                                    error_message = network_status.load_status["message"] or client_load_op.get("error_message", "未知错误")
                                    ue.LogError(f"[加载] ✗ 加载操作失败: {error_message}")
                                
                                ue.LogWarning("=================================")
                                break
                        
                        ue.LogWarning(f"[加载] 等待加载操作完成... ({attempts}/{max_attempts})")
                        
                        # 每次检查都主动处理一次消息
                        ue_site._process_network_internal()
                        ue_site._process_messages_internal()
                    
                    if attempts >= max_attempts:
                        ue.LogError("[加载] 加载操作超时，未收到服务器确认")
                        # 重置加载状态，防止卡住
                        network_status.load_status["in_progress"] = False
                        if network_status.client_entity and hasattr(network_status.client_entity, 'data_operations'):
                            if "load" in network_status.client_entity.data_operations:
                                network_status.client_entity.data_operations["load"]["pending"] = False
                        ue.LogWarning("=================================")
                
                # 启动定时器线程
                threading.Thread(target=check_load_result).start()
            else:
                ue.LogError("[加载] 加载游戏数据请求发送失败")
                ue.LogWarning("=================================")
                
            return success
        except Exception as e:
            ue.LogError(f"[加载] 触发加载游戏数据时出错: {str(e)}")
            import traceback
            ue.LogError(f"[加载] 错误详情: {traceback.format_exc()}")
            ue.LogWarning("=================================")
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
        
    @ue.ufunction(BlueprintCallable=True, Category="PlayerAttributes")
    def _init_player_attributes(self):
        """
        初始化玩家角色的所有基础属性
        设置生命值、魔法值、经验值、弹药数等属性的初始值
        """
        ue.LogWarning("初始化玩家属性...")
        
        # 生命值初始化
        self.MaxHP = 100
        self.CurrentHP = 50
        
        # 经验值初始化
        self.MaxEXP = 100
        self.CurrentEXP = 50
        
        # 弹药数初始化
        self.AllBulletNumber = 100
        self.WeaopnBulletNumber = 20
        
        # 击杀敌人数初始化
        self.KilledEnemies = 0
        
        ue.LogWarning(f"玩家属性初始化完成:")
        ue.LogWarning(f"- 生命值: {self.CurrentHP}/{self.MaxHP}")
        ue.LogWarning(f"- 经验值: {self.CurrentEXP}/{self.MaxEXP}")
        ue.LogWarning(f"- 总弹药: {self.AllBulletNumber}")
        ue.LogWarning(f"- 当前弹匣: {self.WeaopnBulletNumber}")
        ue.LogWarning(f"- 击杀敌人数: {self.KilledEnemies}")

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
        current_weapon_ammo = self.WeaopnBulletNumber
        current_total_ammo = self.AllBulletNumber
        
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
            self.AllBulletNumber -= ammo_needed
            self.WeaopnBulletNumber = max_weapon_capacity
            ue.LogWarning(f"换弹完成：消耗{ammo_needed}发弹药，弹匣装填至{self.WeaopnBulletNumber}发，剩余总弹药{self.AllBulletNumber}发")
        else:
            # 总弹药不足，将所有剩余弹药装入武器
            self.WeaopnBulletNumber += current_total_ammo
            self.AllBulletNumber = 0
            ue.LogWarning(f"弹药不足：将剩余{current_total_ammo}发弹药全部装入，当前弹匣{self.WeaopnBulletNumber}发，总弹药已耗尽")