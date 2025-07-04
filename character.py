# -*- encoding: utf-8 -*-
import ue
@ue.uclass(BlueprintType=True)
class MyCharacter(ue.Character):
    @classmethod
    def _unreal_skeleton_class(cls):
        # 这里指定我们的Python类要使用的真实蓝图类型
        # 使用与动画蓝图尝试转换到的相同类型
        return '/Game/ThirdPersonCPP/Blueprints/MyCharacterBP.MyCharacterBP_C'
    
    # 玩家状态
    Died = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    OnHit = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    LockOrientation = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    AttackState = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    IsAutoFireMode = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    IsAutoFiring = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    LastAutoFireTime = ue.uproperty(float, BlueprintReadWrite=True, Category="MyCharacter")
    
    # 玩家属性
    MaxHP = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    CurrentHP = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    MaxEXP = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    CurrentEXP = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    MaxLevel = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    CurrentLevel = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    AllBulletNumber = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    WeaopnBulletNumber = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    KilledEnemies = ue.uproperty(int, BlueprintReadWrite=True, Category="MyCharacter")
    
    # 委托（自定义事件）
    # 击杀敌数
    GetKilled = ue.udelegate(BlueprintCallable=True, params=((int, 'KilledNumber'), (int, 'KilledExp')))
    # self.GetKilled.Broadcast(10)
    # 道具回复弹药
    ItemAddAmmunition = ue.udelegate(BlueprintCallable=True, params=((int, 'AddAmmunitionNums'),))
    # 道具回复生命值
    ItemAddHP = ue.udelegate(BlueprintCallable=True, params=((int, 'AddHP'),))
    # 每秒回复弹药
    TickAddAmmunition = ue.udelegate(BlueprintCallable=True, params=())
    # 发射子弹
    FireBullet = ue.udelegate(BlueprintCallable=True, params=())
    
    # 人物状态属性
    IsMoving = ue.uproperty(bool, BlueprintReadWrite=True, Category="Animation")
    MoveSpeed = ue.uproperty(float, BlueprintReadWrite=True, Category="Animation")
    IsIdle = ue.uproperty(bool, BlueprintReadWrite=True, Category="Animation")
    
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        ue.LogWarning('%s Character ReceiveBeginPlay!' % self)

        # 导入protobuf
        import sys
        sys.path.append("C:\\Users\\wydx\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages")
        
        # 初始化网格体
        self._initialize_mesh()
    
        # 创建战斗数据UI
        self._create_battle_ui()
    
        # 初始化玩家属性
        self._init_player_attributes()
    
        # 设置控制器
        controller = self.GetWorld().GetPlayerController()
        controller.UnPossess()
        controller.Possess(self)
        self.EnableInput(controller)

        # 设置输入和摄像机
        self._setup_input(controller)
        self._configure_camera()
    
        # 初始化玩家网络数据
        self._initialize_player_data()
    
        # 配置委托
        self._setup_delegates()

        # 播放背景音乐
        self._play_background_music()
    
        # 自动登录
        self._auto_login()
        
        # 设置连接状态监控
        self._setup_connection_monitor()
    
    @ue.ufunction(BlueprintCallable=True, Category="Tick")
    def MyCharacterTick(self):
        """接收Tick事件，相当于蓝图中的Event Tick节点"""
        # 检查角色是否移动 - 通过判断速度向量是否不为零
        velocity = self.GetVelocity()
        
        # 更新动画相关属性
        speed = velocity.Size()
        self.MoveSpeed = speed
        old_is_moving = self.IsMoving if hasattr(self, 'IsMoving') else False
        self.IsMoving = speed > 10.0  # 如果速度大于10，认为在移动
        self.IsIdle = not self.IsMoving and not self.AttackState and not self.OnHit and not self.Died
        
        # 处理开始移动时的状态变化
        if not old_is_moving and self.IsMoving:
            # 如果刚开始移动且正在换弹，则取消换弹
            if hasattr(self, '_is_reloading') and self._is_reloading:
                ue.LogWarning("[换弹] 开始移动，取消换弹操作")
                # 停止当前正在播放的换弹动画
                if self.Mesh:
                    anim_instance = self.Mesh.GetAnimInstance()
                    if anim_instance and hasattr(anim_instance, 'Montage_Stop'):
                        blend_out_time = 0.25
                        anim_instance.Montage_Stop(blend_out_time)
                # 重置换弹状态
                self._reset_state("reload")

        # 处理连射模式逻辑
        if self.IsAutoFireMode and hasattr(self, 'IsAutoFiring') and self.IsAutoFiring:
            # 初始化LastAutoFireTime属性，如果不存在
            if not hasattr(self, 'LastAutoFireTime'):
                self.LastAutoFireTime = 0
                
            # 检查是否在移动或跑步，如果是，则停止连射
            if self.IsMoving:
                ue.LogWarning("[连射] 开始移动，停止连射")
                self.IsAutoFiring = False
                return
            
            # 连射过程中，每帧都更新角色朝向，确保角色实时跟随鼠标移动
            self._calculate_target_direction()
                
            # 获取当前时间
            current_time = ue.GameplayStatics.GetTimeSeconds(self)
            
            # 计算间隔时间（控制射速）
            # 调整此值可以控制连射速度，值越小射速越快
            fire_interval = 0.1  # 100ms间隔，约每秒10发
            
            # 检查是否可以发射下一发子弹
            if current_time - self.LastAutoFireTime >= fire_interval:
                # 更新上次射击时间
                self.LastAutoFireTime = current_time
                
                # 检查弹药数量
                if self.WeaopnBulletNumber <= 0:
                    ue.LogWarning("[连射] 弹药耗尽，停止连射")
                    self.IsAutoFiring = False
                    return
                
                # 发射子弹和播放音效（不播放动画）
                self._play_sound("/Game/Sounds/S_WEP_Fire_08.S_WEP_Fire_08")
                self.FireBullet.Broadcast()
                ue.LogWarning(f"[连射] 发射子弹，剩余弹药: {self.WeaopnBulletNumber}")
    
    @ue.ufunction(override=True)
    def ReceiveEndPlay(self, EndPlayReason):
        try:
            ue.LogWarning('角色退出游戏，自动保存游戏数据...')
        
            # 停止背景音乐
            if hasattr(self, 'music_should_play'):
                try:
                    # 设置标志以停止音乐循环线程
                    self.music_should_play = False
                    ue.LogWarning('已设置停止背景音乐循环')
                    
                    # 尝试停止所有声音（如果有可用的方法）
                    try:
                        ue.GameplayStatics.SetGlobalTimeDilation(self, 1.0)  # 确保时间膨胀正常
                    except:
                        pass
                
                except Exception as audio_error:
                    ue.LogError(f'停止背景音乐失败: {str(audio_error)}')
            
            # 停止连接监控
            try:
                if hasattr(self, '_should_monitor_connection'):
                    self._should_monitor_connection = False
                    ue.LogWarning('已停止连接状态监控')
            except Exception as save_error:
                import traceback
                ue.LogError(f'停止连接监控失败: {str(save_error)}')
                ue.LogError(traceback.format_exc())
            
            
            # 自动保存游戏数据
            try:
                # 调用保存游戏数据的函数
                self._save_game_data()
                ue.LogWarning('游戏退出前自动保存完成')
            except Exception as save_error:
                import traceback
                ue.LogError(f'退出游戏时自动保存失败: {str(save_error)}')
                ue.LogError(traceback.format_exc())
        
            # 获取动画实例
            if self.Mesh:
                anim_instance = self.Mesh.GetAnimInstance()
                if anim_instance:
                    # 使用清理函数移除所有回调
                    self._clean_all_montage_callbacks(anim_instance)
                    
            ue.LogWarning('角色退出游戏，已清理所有回调')
        except Exception as e:
            import traceback
            ue.LogError(f'清理角色回调时出错: {str(e)}')
            ue.LogError(traceback.format_exc())
    
    # 初始化相关
    def _auto_login(self):
        """自动登录功能"""
        try:
            import ue_site
            import time
            import threading
            
            # 获取GameInstance并转换为MyGameInstance
            game_instance = ue.GameplayStatics.GetGameInstance(self)
            # 使用as_class替代cast进行类型转换
            my_game_instance_class = ue.LoadClass('/Game/ThirdPersonCPP/Blueprints/MyGameInstance.MyGameInstance_C')
            my_game_instance = None
            
            # 先检查类是否成功加载
            if my_game_instance_class:
                # 尝试将game_instance转换为MyGameInstance类型
                try:
                    # 尝试另一种转换方式
                    if hasattr(game_instance, 'GetClass') and game_instance.GetClass().IsChildOf(my_game_instance_class):
                        my_game_instance = game_instance
                    else:
                        ue.LogWarning("[自动登录] 使用直接引用GameInstance，而不进行转换")
                        my_game_instance = game_instance
                except Exception as ex:
                    ue.LogWarning(f"[自动登录] 转换GameInstance时出错: {ex}，使用直接引用")
                    my_game_instance = game_instance
            else:
                ue.LogError("[自动登录] 无法加载MyGameInstance类")
                return False
                
            if not my_game_instance:
                ue.LogError("[自动登录] 无法获取GameInstance")
                return False
                
            # 从GameInstance中获取账号密码
            username = my_game_instance.instance_account if hasattr(my_game_instance, 'instance_account') else "None"
            password = my_game_instance.instance_password if hasattr(my_game_instance, 'instance_password') else "None"
            
            # 输出登录信息(与蓝图中的PrintString对应)
            ue.LogWarning(f"[自动登录] 从GameInstance获取账号: {username}")
            ue.LogWarning(f"[自动登录] 从GameInstance获取密码: {password}")
            
            # 获取单例网络状态
            network_status = ue_site.network_status
            ue.LogWarning(f"[自动登录] 登录前状态: {network_status.get_status_dict()}")
            
            # 从GameInstance获取新游戏标记
            is_new_game = my_game_instance.instance_isnewgame if hasattr(my_game_instance, 'instance_isnewgame') else False
            ue.LogWarning(f"[自动登录] 是否为新游戏: {is_new_game}")
            
            # 先检查是否已经登录
            # 两种方式检查登录状态: 通过network_status和通过client_entity
            already_logged_in = False
            if network_status.auth_status["is_authenticated"]:
                ue.LogWarning(f"[自动登录] 已经登录为用户: {network_status.auth_status['username']}，无需重复登录")
                already_logged_in = True
            
            # 如果有client_entity，还需要检查其认证状态
            elif (network_status.client_entity and 
                hasattr(network_status.client_entity, 'authenticated') and 
                network_status.client_entity.authenticated):
                # 同步客户端状态
                network_status.auth_status["is_authenticated"] = True
                network_status.auth_status["username"] = network_status.client_entity.username
                
                # 同步token信息
                if hasattr(network_status.client_entity, 'token'):
                    network_status.auth_status["token"] = network_status.client_entity.token
                    ue.LogWarning(f"[自动登录] 已经通过客户端实体验证为用户: {network_status.client_entity.username}，无需重复登录")
                    already_logged_in = True
                
            if already_logged_in:
                # 用户已登录，处理玩家数据
                ue.LogWarning("[自动登录] 用户已登录，根据是否新游戏决定处理玩家数据")
                
                self._handle_player_data(is_new_game)
                my_game_instance.instance_isnewgame = False
                return True
                
            if network_status.auth_status["login_in_progress"]:
                # 检查是否是过期的登录进行中状态
                current_time = time.time()
                # 如果last_login_attempt不存在或为0，设置一个默认值
                last_attempt = network_status.auth_status.get("last_login_attempt", 0)
                if current_time - last_attempt < 10.0:
                    ue.LogWarning("[自动登录] 登录操作正在进行中，请等待...")
                    # 在等待时主动处理一次网络消息
                    ue_site._process_network_internal()
                    ue_site._process_messages_internal()
                    return False
                else:
                    ue.LogWarning("[自动登录] 上一次登录请求已超时，将重新尝试")
                    # 重置登录进行中状态
                    network_status.auth_status["login_in_progress"] = False
                    # 继续执行登录逻辑
            
            # 检查网络是否已初始化并连接
            is_ready, error_msg = self._check_network_ready()
            if not is_ready:
                ue.LogError(f"{error_msg}，无法登录")
                return False
            
            # 使用账号密码登录
            ue.LogWarning(f"[自动登录] 自动登录 - 用户名: {username}")
            
            # 立即处理网络消息，确保连接状态最新
            ue_site._process_network_internal()
            
            # 发送登录请求
            login_sent = ue_site.login(username, password, is_new_game)
            if not login_sent:
                ue.LogWarning("[自动登录] 登录请求发送失败")
                if hasattr(my_game_instance, 'instance_login_result'):
                    my_game_instance.instance_login_result = False
                
                self._disconnect_from_server()
                self._open_start_map()
                return False
            
            ue.LogWarning("[自动登录] 登录请求已发送，等待服务器响应...")
            
            # 创建一个事件来表示登录操作完成
            login_completed = threading.Event()
            login_success = [False]  # 使用列表作为可变对象存储登录结果
            
            # 创建一个函数来检查登录响应
            def check_login_response():
                # 最多等待5秒
                max_attempts = 4
                attempts = 0
                
                while attempts < max_attempts and not login_success[0]:
                    # 等待短暂时间让服务器有机会响应
                    time.sleep(0.5)
                    attempts += 1
                    
                    # 直接调用消息处理函数
                    ue_site._process_network_internal()
                    ue_site._process_messages_internal()
                    
                    # 检查登录状态
                    if ue_site.is_authenticated():
                        ue.LogWarning(f"[自动登录] 用户 {username} 登录成功！")
                        login_success[0] = True
                        break
                    
                    # 检查是否有明确的登录失败信息
                    auth_status = ue_site.network_status.auth_status
                    if "login_failed" in auth_status and auth_status["login_failed"]:
                        ue.LogWarning(f"[自动登录] 登录失败: {auth_status.get('error_message', '未知错误')}")
                        break
                    
                    # 检查网络连接是否断开
                    if not ue_site.network_status.is_connected:
                        ue.LogWarning("[自动登录] 网络连接已断开，登录过程中断")
                        break
                    
                    ue.LogWarning(f"[自动登录] 等待登录响应... ({attempts}/{max_attempts})")
                
                # 设置事件以通知主线程登录检查完成
                login_completed.set()
            
            # 启动线程检查登录响应
            threading.Thread(target=check_login_response).start()
            
            # 等待登录操作完成或超时
            login_completed.wait(6.0)  # 最多等待6秒
            
            # 设置登录结果到GameInstance
            if hasattr(my_game_instance, 'instance_login_result'):
                my_game_instance.instance_login_result = login_success[0]
            
            # 如果登录失败，打开开始地图
            if not login_success[0]:
                ue.LogWarning("[自动登录] 登录失败，打开开始地图")
                self._disconnect_from_server()
                self._open_start_map()
                return False
            else:
                ue.LogWarning(f"[自动登录] 登录成功")
                
                # 登录成功后，处理玩家数据
                self._handle_player_data(is_new_game)
                my_game_instance.instance_isnewgame = False
            
            return login_success[0]
        except ImportError:
            ue.LogError("[自动登录] 导入ue_site模块失败，无法登录")
            self._disconnect_from_server()
            ue.GameplayStatics.OpenLevelBySoftObjectPtr(self, "/Game/ThirdPersonCPP/Maps/开始地图.开始地图", True, "")
            return False
        except Exception as e:
            ue.LogError(f"触发登录时出错: {str(e)}")
            import traceback
            ue.LogError(f"[自动登录] 错误详情: {traceback.format_exc()}")
            self._disconnect_from_server()
            # 使用OpenLevel替代OpenLevelBySoftObjectPtr
            try:
                ue.LogWarning("[自动登录] 由于错误，尝试打开开始地图")
                ue.GameplayStatics.OpenLevel(self, "开始地图", True)
            except Exception as ex:
                ue.LogError(f"[自动登录] 打开关卡失败: {ex}")
                try:
                    # 备用方法
                    ue.GameplayStatics.OpenLevelByName(self, "开始地图", True)
                except Exception as ex2:
                    ue.LogError(f"[自动登录] 备用方法打开关卡也失败: {ex2}")
            return False
    
    def _handle_player_data(self, is_new_game):
        """
        根据是否为新游戏来处理玩家数据
        
        Args:
            is_new_game (bool): 是否为新游戏，True则初始化新数据，False则加载服务器数据
        """
        if is_new_game:
            # 如果是新游戏，初始化玩家数据
            ue.LogWarning("[自动登录] 新游戏，初始化玩家属性")
            self._init_player_attributes()
        else:
            # 如果是继续游戏，加载服务器数据
            ue.LogWarning("[自动登录] 继续游戏，从服务器加载玩家数据")
            self._load_game_data()
    
    def _open_start_map(self):
        """打开开始地图"""
        try:
            ue.LogWarning("[自动登录] 尝试打开开始地图")
            ue.GameplayStatics.OpenLevel(self, "开始地图", True)
        except Exception as e:
            ue.LogError(f"[自动登录] 打开开始地图失败: {e}")
            try:
                # 备用方法
                ue.GameplayStatics.OpenLevelByName(self, "开始地图", True)
            except Exception as ex:
                ue.LogError(f"[自动登录] 备用方法打开开始地图也失败: {ex}")
    
    def _disconnect_from_server(self):
        """断开与服务器的连接"""
        try:
            import ue_site
            
            # 获取网络状态单例
            network_status = ue_site.network_status
            
            ue.LogWarning("[网络] 尝试断开与服务器的连接")
            
            # 检查是否有已初始化的网络客户端
            if network_status.is_network_initialized and network_status.network_client:
                # 检查是否已连接
                if network_status.is_connected:
                    # 调用断开连接方法
                    if hasattr(network_status.network_client, 'disconnect'):
                        network_status.network_client.disconnect()
                        ue.LogWarning("[网络] 已断开与服务器的连接")
                    else:
                        ue.LogError("[网络] 网络客户端没有disconnect方法")
                    
                    # 更新连接状态
                    network_status.is_connected = False
                    
                    # 清理认证状态
                    network_status.auth_status = {
                        "is_authenticated": False,
                        "username": "",
                        "token": "",
                        "login_in_progress": False,
                        "last_login_attempt": 0,
                        "login_time": 0,
                        "last_token_refresh": 0
                    }
                    
                    # 如果有client_entity，也清理其认证状态
                    if network_status.client_entity:
                        if hasattr(network_status.client_entity, 'authenticated'):
                            network_status.client_entity.authenticated = False
                        if hasattr(network_status.client_entity, 'token'):
                            network_status.client_entity.token = ""
                else:
                    ue.LogWarning("[网络] 当前未连接服务器，无需断开")
            else:
                ue.LogWarning("[网络] 网络客户端未初始化，无需断开")
                
            return True
        except ImportError:
            ue.LogError("[网络] 导入ue_site模块失败，无法断开连接")
            return False
        except Exception as e:
            ue.LogError(f"[网络] 断开连接时出错: {str(e)}")
            import traceback
            ue.LogError(f"[网络] 错误详情: {traceback.format_exc()}")
            return False
    
    def _create_battle_ui(self):
        """创建战斗数据UI"""
        try:
            # 存储角色引用到模块级变量，使其可在整个模块中访问
            import sys
            current_module = sys.modules[__name__]
            setattr(current_module, 'current_player_character', self)
            
            # 加载UI类
            widget_class = ue.LoadClass('/Game/ThirdPersonCPP/Blueprints/UI/BattleDataUI.BattleDataUI_C')
            if not widget_class:
                ue.LogError('无法加载BattleDataUI类')
                return
                
            # 创建并添加UI到视口
            controller = self.GetWorld().GetPlayerController(0)
            battle_ui = ue.WidgetBlueprintLibrary.Create(self.GetWorld(), widget_class, controller)
            
            if battle_ui:
                # 设置UI引用角色
                if hasattr(battle_ui, 'MyCharacterBPUI'):
                    battle_ui.MyCharacterBPUI = self
                
                # 添加到视口并保存引用
                battle_ui.AddToViewport()
                self.battle_ui = battle_ui
                ue.LogWarning('战斗数据UI创建成功')
            else:
                ue.LogError('创建BattleDataUI失败')
                
        except Exception as e:
            import traceback
            ue.LogError(f'创建UI时出错: {str(e)}')
            ue.LogError(traceback.format_exc())
    
    def _setup_input(self, controller):
        """设置输入绑定和Enhanced Input"""
        ue.LogWarning(f"设置输入系统, {self}!")
        
        # 检查控制器的输入组件类型
        if hasattr(controller, "EnhancedInputComponent"):
            input_component = controller.EnhancedInputComponent
            has_enhanced_input = True
            ue.LogWarning("成功获取EnhancedInputComponent")
        elif hasattr(controller, "InputComponent"):
            input_component = controller.InputComponent
            has_enhanced_input = hasattr(input_component, "BindActionByName")
            ue.LogWarning("使用常规InputComponent")
        else:
            ue.LogError("无法获取任何InputComponent")
            return
        
        # 保存InputComponent引用
        self.InputComponent = input_component
        
        # 设置默认行走速度
        self.CharacterMovement.MaxWalkSpeed = 600.0
        ue.LogWarning(f"初始行走速度设置为: {self.CharacterMovement.MaxWalkSpeed}")
        
        # 基本移动和视角控制
        self.InputComponent.BindAxis('MoveForward', self._move_forward)
        self.InputComponent.BindAxis('MoveRight', self._move_right)
        self.InputComponent.BindAxis('Turn', self._turn_right)
        self.InputComponent.BindAxis('LookUp', self._look_up)
        self.InputComponent.BindAction('Jump', ue.EInputEvent.IE_Pressed, self._jump)
        
        # 功能键绑定
        key_bindings = {
            "LeftShift": [(ue.EInputEvent.IE_Pressed, self._run_start), 
                        (ue.EInputEvent.IE_Released, self._run_stop)],
            "R": [(ue.EInputEvent.IE_Pressed, self._reload_weapon)],
            "L": [(ue.EInputEvent.IE_Pressed, self._trigger_login)],
            "U": [(ue.EInputEvent.IE_Pressed, self._save_game_data)],
            "I": [(ue.EInputEvent.IE_Pressed, self._load_game_data)],
            "T": [(ue.EInputEvent.IE_Pressed, self._toggle_fire_mode)],
            "LeftMouseButton": [(ue.EInputEvent.IE_Pressed, self._attack_started),
                              (ue.EInputEvent.IE_Released, self._attack_ended)]
        }
        
        # 注册所有键绑定
        for key, bindings in key_bindings.items():
            for event, callback in bindings:
                self.InputComponent.BindKey(key, event, callback)
            ue.LogWarning(f"绑定{key}键成功")
            
        # 如果支持Enhanced Input，尝试绑定额外的Enhanced Input动作
        try:
            if has_enhanced_input and hasattr(input_component, "BindActionByName"):
                actions = {
                    "MyRun": [(ue.EInputEvent.IE_Pressed, self._run_start), 
                            (ue.EInputEvent.IE_Released, self._run_stop)],
                    "MyReload": [(ue.EInputEvent.IE_Pressed, self._reload_weapon)]
                }
                
                for action_name, bindings in actions.items():
                    for event, callback in bindings:
                        input_component.BindActionByName(action_name, event, callback)
                
                ue.LogWarning("使用Enhanced Input特有方法绑定成功")
        except Exception as e:
            ue.LogError(f"Enhanced Input绑定失败: {str(e)}")
        
        # 设置角色移动和旋转
        self.CharacterMovement.bOrientRotationToMovement = True  # 角色朝向移动方向
        self.bUseControllerRotationYaw = False  # 禁用控制器Yaw旋转控制角色
        self.CharacterMovement.RotationRate = ue.Rotator(0, 540, 0)  # 较高的旋转速度
        
        # 设置鼠标灵敏度
        self.MouseSpeed = 45.0
        
        ue.LogWarning("输入系统设置完成")
    
    def _configure_camera(self):
        """配置摄像机以角色Mesh为中心旋转"""
        # 获取SpringArm和Camera组件
        spring_arm_class = ue.FindClass("SpringArmComponent")
        camera_class = ue.FindClass("CameraComponent")
        
        spring_arm = self.GetComponentByClass(spring_arm_class)
        camera = self.GetComponentByClass(camera_class)
        
        if spring_arm and self.Mesh:
            # 将SpringArm附着到角色Mesh而不是CapsuleComponent
            spring_arm.DetachFromComponent(ue.EDetachmentRule.KeepWorld)
            spring_arm.AttachToComponent(self.Mesh, "", ue.EAttachmentRule.SnapToTarget, 
                                        ue.EAttachmentRule.SnapToTarget, ue.EAttachmentRule.SnapToTarget, True)
            
            # 配置SpringArm旋转设置
            spring_arm.bUsePawnControlRotation = True  # 使用Pawn的控制器旋转
            spring_arm.bInheritPitch = True
            spring_arm.bInheritYaw = True
            spring_arm.bInheritRoll = False
            
            # 调整SpringArm相对位置和旋转
            spring_arm.SetRelativeLocation(ue.Vector(0, 0, 88))
    
    def _setup_delegates(self):
        """设置委托事件回调"""
        self.GetKilled.Add(self.AddKilledNumbers)
        self.ItemAddAmmunition.Add(self.AddAmmunitionFromItem)
        self.ItemAddHP.Add(self.AddHPFromItem)
        self.TickAddAmmunition.Add(self.AddAmmunitionFromTick)
        self.FireBullet.Add(self.GenerateBullet)
        
        # 添加伤害委托绑定
        self.OnTakeAnyDamage.Add(self._on_take_any_damage)
        ue.LogWarning("已绑定OnTakeAnyDamage委托，角色将响应伤害事件")
    
    # 成就相关
    @ue.ufunction(BlueprintCallable=True, Category="Network", ret=bool)
    def get_achievement_broadcast_status(self):
        import ue_site
        network_status = ue_site.network_status
        if network_status:
            return network_status.client_entity.has_new_achievement_broadcast()
        return False
    
    @ue.ufunction(BlueprintCallable=True, Category="Network", params=bool)
    def set_achievement_broadcast_status(self, clear_flag):
        import ue_site
        network_status = ue_site.network_status
        if network_status:
            network_status.client_entity.get_recent_achievement_broadcast(clear_flag)
    
    @ue.ufunction(BlueprintCallable=True, Category="Network", ret=str)
    def get_achievement_broadcast_content(self):
        import ue_site
        network_status = ue_site.network_status
        if network_status:
            content = network_status.client_entity.get_recent_achievement_broadcast(False)
            
            # 判断content是否为None
            if content is None:
                return ""
            
            # 判断是否是自己的成就
            is_own_achievement = network_status.client_entity.username == content.username if hasattr(content, 'username') else content.get('is_own_achievement', False)
            ue.LogWarning(f"get_achievement_broadcast_content: {content}")
            
            # 构建显示信息
            if is_own_achievement:
                message = f"[成就] 恭喜! 您已达到 '{content.get('threshold_title', '')}' 成就! 击杀数: {content.get('threshold_value', 0)}"
            else:
                message = f"[系统公告] 玩家 {content.get('username', '未知')} 已达到 '{content.get('threshold_title', '')}' 成就! 击杀数: {content.get('threshold_value', 0)}"
            
            return message
        else:
            return ""
    
    # 受到伤害相关
    def _on_take_any_damage(self, damaged_actor, damage, damage_type, instigated_by, damage_causer):
        """
        OnTakeAnyDamage委托的回调函数，处理角色受到伤害的逻辑
        
        参数:
            damaged_actor: 受到伤害的Actor（即自身）
            damage: 伤害值
            damage_type: 伤害类型
            instigated_by: 造成伤害的控制器
            damage_causer: 造成伤害的Actor
        """
        try:
            # 更新角色的当前生命值
            self.CurrentHP -= damage
            
            # 记录伤害信息
            damage_causer_name = damage_causer.GetName() if damage_causer and hasattr(damage_causer, 'GetName') else "未知"
            damage_type_name = damage_type.GetName() if damage_type and hasattr(damage_type, 'GetName') else "未知"
            ue.LogWarning(f"角色受到 {damage} 点伤害，伤害类型: {damage_type_name}，来源: {damage_causer_name}")
            
            # 播放受击音效
            self._play_sound("/Game/Sounds/BeDamaged")
            ue.LogWarning("播放受击音效")
            
            # 检查生命值是否小于等于0
            if self.CurrentHP <= 0:
                # 处理角色死亡逻辑
                self.Died = True
                ue.LogWarning(f"角色受致命伤害，当前生命值: {self.CurrentHP}")
                
                # 可以在此处添加死亡动画播放或其他死亡逻辑
            else:
                # 播放受伤动画
                if not self.OnHit:  # 防止多次受击动画叠加
                    # 设置受击状态
                    self.OnHit = True
                    
                    # 使用已有的动画播放系统播放受伤动画
                    self._play_animation_montage(
                        "/Game/Mannequin/Animations/My_Hit_React_4_Montage.My_Hit_React_4_Montage",
                        lambda: self._reset_hit_state(),
                        1.0, "", "hit"
                    )
                    
                    ue.LogWarning(f"角色受到伤害后，当前生命值: {self.CurrentHP}")
                else:
                    ue.LogWarning("角色已处于受击状态，跳过受击动画")
        except Exception as e:
            import traceback
            ue.LogError(f"处理伤害时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
    
    def _reset_hit_state(self):
        """重置受击状态"""
        self.OnHit = False
        ue.LogWarning("受击状态已重置")
    
    # 击杀相关
    def AddKilledNumbers(self, killed_number, killed_exp):
            """处理敌人击杀事件的回调函数"""
            self.KilledEnemies += killed_number
            self.CurrentEXP += killed_exp
            ue.LogWarning(f"KilledEnemies:{self.KilledEnemies}, 获得经验值:{killed_exp}")
        
            # 检查是否可以升级
            if self.CurrentEXP >= self.MaxEXP and self.CurrentLevel < self.MaxLevel:
                self._level_up()
        
            # 如果经验超过上限，截断到最大值
            if self.CurrentEXP > self.MaxEXP:
                self.CurrentEXP = self.MaxEXP
            
            # 每次击杀后自动保存数据到服务器
            try:
                ue.LogWarning("击杀后自动保存游戏数据...")
                import threading
                # 使用线程异步保存数据，避免阻塞游戏
                threading.Thread(target=self._save_game_data).start()
            except Exception as e:
                import traceback
                ue.LogError(f"击杀后自动保存数据时出错: {str(e)}")
                ue.LogError(traceback.format_exc())
    
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
    
    def _level_up(self):
        """处理角色升级逻辑"""
        try:
            # 保存升级前的数据用于日志
            old_level = self.CurrentLevel
            old_max_hp = self.MaxHP
            old_max_exp = self.MaxEXP
            
            # 增加等级
            self.CurrentLevel += 1
            
            # 确保不超过最大等级
            if self.CurrentLevel > self.MaxLevel:
                self.CurrentLevel = self.MaxLevel
                ue.LogWarning(f"已达到最大等级 {self.MaxLevel}，无法继续升级")
                return
            
            # 升级后调整属性
            # 每级增加20点最大生命值
            self.MaxHP = 100 + (self.CurrentLevel - 1) * 20
            # 当前生命值增加差值
            self.CurrentHP += (self.MaxHP - old_max_hp)
            
            # 每级增加经验值上限
            self.MaxEXP = 100 + (self.CurrentLevel - 1) * 50
            
            # 重置当前经验值为0
            self.CurrentEXP = 0
            
            # 记录日志
            ue.LogWarning(f"等级: {old_level} -> {self.CurrentLevel}")
            ue.LogWarning(f"最大生命值: {old_max_hp} -> {self.MaxHP}")
            ue.LogWarning(f"经验值上限: {old_max_exp} -> {self.MaxEXP}")
            
            # 这里可以添加升级特效或动画的触发代码
            
        except Exception as e:
            import traceback
            ue.LogError(f"角色升级时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
    
    # 拾取武器
    def pick_up_weapon(self, weapon):
        # type: (ue.Actor) -> None
        attachment_rule = ue.EAttachmentRule.SnapToTarget
        weapon.AttachToComponent(self.Mesh, 'WeaponSocket',
            attachment_rule, attachment_rule, attachment_rule, True)
        
        self.weapon = weapon
    
    # 攻击相关
    def GenerateBullet(self):
        """处理子弹生成的回调函数"""
        try:
            # 检查弹药数量
            if self.WeaopnBulletNumber <= 0:
                ue.LogWarning("弹药不足，无法发射子弹")
                return False
            
            # 减少弹药数量
            self.WeaopnBulletNumber -= 1
            ue.LogWarning(f"发射子弹，剩余弹药: {self.WeaopnBulletNumber}")
            
            # 检查是否有武器引用
            if hasattr(self, 'weapon') and self.weapon:
                # 使用当前角色朝向作为子弹发射方向
                self.weapon.fire()  # 传递角色引用给fire函数
                return True
            else:
                # 如果没有武器引用，显示错误信息
                ue.LogError("角色没有绑定武器，无法发射子弹")
                return False
            
        except Exception as e:
            import traceback
            ue.LogError(f"执行发射子弹逻辑时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            return False
    
    def _toggle_fire_mode(self):
        """切换射击模式（点射/连射）"""
        self.IsAutoFireMode = not self.IsAutoFireMode
        mode_name = "连射" if self.IsAutoFireMode else "点射"
        ue.LogWarning(f"[射击模式] 切换为{mode_name}模式")
        
        # 如果当前正在连射，切换到点射模式时停止连射
        if not self.IsAutoFireMode and self.IsAutoFiring:
            self.IsAutoFiring = False
            ue.LogWarning("[射击模式] 连射状态已停止")
    
    def _attack_started(self):
        """处理攻击开始事件，对应蓝图中的MyAttack输入动作的Started事件"""
        # 检查是否已经在攻击中，避免重复触发
        if self.AttackState and not self.IsAutoFireMode:
            ue.LogWarning("已经在攻击中，忽略新的攻击请求")
            return
        
        # 检查是否正在换弹，如果在换弹过程中则不允许攻击
        if hasattr(self, '_is_reloading') and self._is_reloading:
            ue.LogWarning("正在换弹中，无法攻击")
            return
            
        # 检查是否在移动或跑步中，如果是则不允许攻击
        velocity = self.GetVelocity()
        speed = velocity.Size()
        if speed > 10.0:  # 角色正在移动
            ue.LogWarning("移动或跑步中，无法攻击")
            return
        
        # 首先更新一下朝向，无论什么模式，确保角色立即朝向鼠标位置
        self._calculate_target_direction()
        ue.LogWarning("[攻击] 立即转向鼠标指向的方位")
        
        # 如果是连射模式，设置连射状态但不立即设置AttackState
        # AttackState将由Tick函数中的连射逻辑来管理
        if self.IsAutoFireMode:
            self.IsAutoFiring = True
            # 记录上次射击时间为0，确保Tick中立即触发第一发子弹
            self.LastAutoFireTime = 0
            ue.LogWarning("[射击] 开始连射模式")
            # 设置特殊的锁定朝向标志，但允许朝向更新为鼠标方向
            self.LockOrientation = True
            return
        
        # 点射模式直接设置攻击状态
        self.AttackState = True
        # 设置特殊的锁定朝向标志，但允许朝向更新为鼠标方向
        self.LockOrientation = True
        
        try:
            # 只有在点射模式下才直接调用攻击动画播放函数
            # 连射模式下，动画由MyCharacterTick处理
            if not self.IsAutoFireMode:
                self._play_attack_animation()
                
        except Exception as e:
            import traceback
            ue.LogError(f"执行攻击功能时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            self._reset_state("attack")
    
    def _calculate_target_direction(self):
        """计算射击方向并设置角色朝向"""
        try:
            # 获取玩家控制器
            controller = self.GetWorld().GetPlayerController(0)
            if not controller:
                ue.LogError("无法获取玩家控制器")
                return
            
            # 获取玩家视角方向
            player_view_point = controller.GetPlayerViewPoint()
            if not player_view_point or len(player_view_point) != 2:
                ue.LogError("无法获取玩家视角")
                return
                
            # 解包视角信息
            camera_location = player_view_point[0]  # 相机位置
            camera_rotation = player_view_point[1]  # 相机旋转
                
            # 首先尝试获取鼠标光标下的命中位置
            hit_tuple = controller.GetHitResultUnderCursorByChannel(
                ue.ETraceTypeQuery.TraceTypeQuery1,  # 默认通道
                True  # 复杂碰撞检测
            )
            # 解包元组，获取命中状态和HitResult对象
            has_hit = hit_tuple[0]  # 第一个元素是布尔值，表示是否命中
            hit_result = hit_tuple[1]  # 第二个元素是HitResult对象
            
            # 获取角色当前位置
            actor_location = self.GetActorLocation()
            
            # 确定目标位置（无论是否命中）
            target_location = None
            
            if has_hit:
                # 如果射线命中了物体，使用命中点
                target_location = hit_result.Location
                ue.LogWarning(f"射线命中目标点：{target_location}")
            else:
                # 如果射线未命中任何物体（例如鼠标指向天空），
                # 计算一个远处的点作为目标方向
                
                # 获取鼠标位置
                mouse_position = controller.GetMousePosition()
                if mouse_position and len(mouse_position) >= 2:
                    # 明确将鼠标坐标转换为浮点数
                    try:
                        mouse_x = float(mouse_position[0])
                        mouse_y = float(mouse_position[1])
                        ue.LogWarning(f"[攻击] 鼠标坐标转换前: X={mouse_position[0]} ({type(mouse_position[0]).__name__}), Y={mouse_position[1]} ({type(mouse_position[1]).__name__})")
                        ue.LogWarning(f"[攻击] 鼠标坐标转换后: X={mouse_x} ({type(mouse_x).__name__}), Y={mouse_y} ({type(mouse_y).__name__})")
                            
                        # 将鼠标屏幕坐标转换为世界空间方向
                        world_direction = controller.DeprojectScreenPositionToWorld(mouse_x, mouse_y)
                    except (TypeError, ValueError) as e:
                        ue.LogWarning(f"[攻击] 鼠标坐标转换失败: {e}")
                        # 转换失败时的备用方案 - 使用相机前方向量
                        target_direction = ue.KismetMathLibrary.GetForwardVector(camera_rotation)
                        ue.LogWarning(f"[攻击] 使用相机朝向作为备用方向: {target_direction}")
                    if world_direction and len(world_direction) >= 2:
                        direction = world_direction[1]  # 第二个元素是方向向量
                        
                        # 沿着方向向量延伸一段距离（例如10000单位）作为目标点
                        # 使用向量计算：目标点 = 起点 + 方向 * 距离
                        target_location = ue.KismetMathLibrary.Add_VectorVector(
                            camera_location,
                            ue.KismetMathLibrary.Multiply_VectorFloat(direction, 10000.0)
                        )
                        ue.LogWarning(f"使用计算的远点作为目标：{target_location}")
                
                # 如果无法通过鼠标获取方向，使用相机前方
                if not target_location:
                    # 获取相机前方向量
                    forward_vector = ue.KismetMathLibrary.GetForwardVector(camera_rotation)
                    
                    # 计算相机前方远处的点
                    target_location = ue.KismetMathLibrary.Add_VectorVector(
                        camera_location,
                        ue.KismetMathLibrary.Multiply_VectorFloat(forward_vector, 10000.0)
                    )
                    ue.LogWarning(f"使用相机前方作为目标方向：{target_location}")
            
            # 计算角色到目标点的方向向量
            direction_vector = ue.KismetMathLibrary.Subtract_VectorVector(
                target_location,
                actor_location
            )
            
            # 忽略高度差异，将Z坐标设为0
            direction_vector.Z = 0
            
            # 归一化方向向量（确保是单位向量）
            direction_vector = ue.KismetMathLibrary.Normal(direction_vector)
            
            # 从方向向量计算旋转
            target_rotation = ue.KismetMathLibrary.MakeRotFromX(direction_vector)
            
            # 设置角色朝向
            self.SetActorRotation(target_rotation, False)
            ue.LogWarning(f"设置角色旋转至：{target_rotation}")
        except Exception as e:
            import traceback
            ue.LogError(f"计算射击方向时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
    
    def _play_attack_animation(self):
        """播放攻击动画（该方法专门负责动画播放，由_attack_started调用）"""
        montage_path = "/Game/Mannequin/Animations/My_Fire_Rifle_Hip_Montage.My_Fire_Rifle_Hip_Montage"
    
        # 在每次点射攻击前重新获取鼠标位置并更新角色朝向
        # 这确保即使点射模式下，每次点击也会根据最新的鼠标位置更新角色朝向
        self._calculate_target_direction()
        ue.LogWarning("[点射] 更新角色朝向到最新鼠标位置")
    
        # 播放前触发发射子弹事件
        if self.WeaopnBulletNumber > 0:
            # 播放射击音效
            self._play_sound("/Game/Sounds/S_WEP_Fire_08.S_WEP_Fire_08")
            # 播放射击音效
            self._play_sound("/Game/Sounds/S_WEP_Fire_08.S_WEP_Fire_08")
            self.FireBullet.Broadcast()
            ue.LogWarning("[动画] 触发发射子弹事件")
    
    
        # 播放攻击动画
        if not self._play_animation_montage(montage_path, lambda: self._reset_state("attack"), 1.0, "", "attack"):
            ue.LogError("[动画] 播放攻击动画失败")
            self._reset_state("attack")
    
    def _attack_ended(self):
        """处理攻击结束事件，对应鼠标左键释放"""
        # 如果是连射模式，停止连射
        if self.IsAutoFireMode and hasattr(self, 'IsAutoFiring') and self.IsAutoFiring:
            self.IsAutoFiring = False
            ue.LogWarning("[射击] 连射模式停止")
            
            # 如果当前不在攻击动画中，播放一次完整的攻击动画作为收尾
            if not self.AttackState:
                self.AttackState = True
                self._play_attack_animation()
        
        # 点射模式无需额外处理，状态由动画完成回调重置
    
    # reload 相关
    def _reload_weapon(self):
        """处理武器换弹逻辑，播放换弹动画蒙太奇"""
        try:
            # 如果已经在攻击中或换弹中，则不执行新的换弹动作
            if self.AttackState:
                ue.LogWarning("当前正在攻击状态，无法换弹")
                return
        
            if hasattr(self, '_is_reloading') and self._is_reloading:
                ue.LogWarning("已经在换弹中，忽略重复操作")
                return
            
            # 检查是否在移动或跑步中，如果是则不允许换弹
            velocity = self.GetVelocity()
            speed = velocity.Size()
            if speed > 10.0:  # 角色正在移动
                ue.LogWarning("移动或跑步中，无法换弹")
                return
        
            # 检查是否有备用弹药可以装填
            if not hasattr(self, 'AllBulletNumber'):
                self.AllBulletNumber = 100  # 默认总弹药数
            
            if not hasattr(self, 'WeaopnBulletNumber'):
                self.WeaopnBulletNumber = 0  # 默认当前弹药数
            
            if not hasattr(self, 'MaxWeaponBulletNumber'):
                self.MaxWeaponBulletNumber = 30  # 默认武器最大弹药数
            
            # 如果没有备用弹药或武器已满，则不执行换弹
            if self.AllBulletNumber <= 0:
                ue.LogWarning("没有备用弹药可装填")
                return
        
            if self.WeaopnBulletNumber >= self.MaxWeaponBulletNumber:
                ue.LogWarning("武器弹药已满，无需换弹")
                return
            
            # 设置换弹状态
            self._is_reloading = True
            self.LockOrientation = True  # 在换弹过程中锁定方向
            
            # 播放换弹动画
            self._play_reload_animation()
        
        except Exception as e:
            import traceback
            ue.LogError(f"执行换弹功能时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            self._reset_state("reload")
    
    def _play_reload_animation(self):
            """播放换弹动画（由_reload_weapon调用）"""
            montage_path = "/Game/Mannequin/Animations/My_Reload_Rifle_Hip_Montage.My_Reload_Rifle_Hip_Montage"
    
            # 播放换弹音效
            self._play_sound("/Game/Sounds/S_WEP_Rifle_Reload.S_WEP_Rifle_Reload")
    
            # 播放换弹动画
            if not self._play_animation_montage(montage_path, self._complete_reload, 1.0, "", "reload"):
                ue.LogError("[动画] 播放换弹动画失败")
                self._reset_state("reload")
    
    def _complete_reload(self, *args):
        """完成换弹操作，更新弹药数量
        
        参数:
            *args: 可变参数列表，用于接收由蒙太奇回调传递的额外参数
        """
        # 记录方法调用
        ue.LogWarning("[换弹] 执行换弹完成操作")
        try:
            if not hasattr(self, '_is_reloading') or not self._is_reloading:
                ue.LogWarning("尝试完成换弹，但当前不在换弹状态")
                return
        
            # 计算需要装填的弹药量
            needed_bullets = self.MaxWeaponBulletNumber - self.WeaopnBulletNumber
        
            # 实际能装填的弹药量(取决于备用弹药数量)
            actual_reload = min(needed_bullets, self.AllBulletNumber)
        
            # 更新武器弹药和备用弹药
            self.WeaopnBulletNumber += actual_reload
            self.AllBulletNumber -= actual_reload
        
            ue.LogWarning(f"换弹完成! 当前武器弹药: {self.WeaopnBulletNumber}/{self.MaxWeaponBulletNumber}, 剩余备用弹药: {self.AllBulletNumber}")
        
            # 重置换弹状态
            self._reset_state("reload")
        
        except Exception as e:
            import traceback
            ue.LogError(f"完成换弹操作时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            self._reset_state("reload")
    
    def _play_animation_montage(self, montage_path, completion_callback, play_rate=1.0, start_section_name="", tag=""):
        """
        通用的动画蒙太奇播放函数
        
        Args:
            montage_path (str): 动画蒙太奇资源路径
            completion_callback (function): 动画完成后的回调函数
            play_rate (float, optional): 播放速率. 默认为1.0.
            start_section_name (str, optional): 起始节名称. 默认为"".
            tag (str, optional): 标识此次播放的标签，用于日志输出. 默认为"".
        
        Returns:
            bool: 是否成功开始播放
        """
        try:
            # 记录函数开始执行
            ue.LogWarning(f"[动画-{tag}] -------- 开始播放动画蒙太奇 --------")
            ue.LogWarning(f"[动画-{tag}] 请求路径: {montage_path}")
            ue.LogWarning(f"[动画-{tag}] 播放速率: {play_rate}, 起始节: '{start_section_name or '默认'}'")
            
            # 检查主要角色网格体
            if not self.Mesh:
                ue.LogError(f"[动画-{tag}] 无法获取角色网格体组件")
                return False
            
            # 使用Character类的标准网格体组件
            try:
                mesh_to_use = self.GetMesh()
            except (AttributeError, TypeError):
                mesh_to_use = self.Mesh
            
            if not mesh_to_use:
                ue.LogError(f"[动画-{tag}] 获取网格体组件失败")
                return False
            
            # 打印网格体详细信息
            try:
                mesh_name = mesh_to_use.GetName()
            except (AttributeError, TypeError):
                mesh_name = "未知网格体"
            
            mesh_class = type(mesh_to_use).__name__
            
            try:
                mesh_path = mesh_to_use.GetPathName()
            except (AttributeError, TypeError):
                mesh_path = "未知路径"
            
            ue.LogWarning(f"[动画-{tag}] 网格体信息:")
            ue.LogWarning(f"[动画-{tag}] - 名称: {mesh_name}")
            ue.LogWarning(f"[动画-{tag}] - 类型: {mesh_class}")
            ue.LogWarning(f"[动画-{tag}] - 路径: {mesh_path}")
            
            # 打印角色信息
            try:
                char_name = self.GetName()
            except (AttributeError, TypeError):
                char_name = "未知角色"
                
            char_class = type(self).__name__
            
            try:
                char_path = self.GetPathName()
            except (AttributeError, TypeError):
                char_path = "未知路径"
                
            ue.LogWarning(f"[动画-{tag}] 角色信息:")
            ue.LogWarning(f"[动画-{tag}] - 名称: {char_name}")
            ue.LogWarning(f"[动画-{tag}] - 类型: {char_class}")
            ue.LogWarning(f"[动画-{tag}] - 路径: {char_path}")
            
            # 加载蒙太奇
            montage = ue.LoadObject(ue.AnimMontage, montage_path)
            if not montage:
                ue.LogError(f"[动画-{tag}] 无法加载动画蒙太奇: {montage_path}")
                return False
            
            # 打印蒙太奇详细信息
            try:
                montage_name = montage.GetName()
            except (AttributeError, TypeError):
                montage_name = "未知蒙太奇"
                
            montage_class = type(montage).__name__
            
            try:
                montage_full_path = montage.GetPathName()
            except (AttributeError, TypeError):
                montage_full_path = montage_path
            
            ue.LogWarning(f"[动画-{tag}] 蒙太奇信息:")
            ue.LogWarning(f"[动画-{tag}] - 名称: {montage_name}")
            ue.LogWarning(f"[动画-{tag}] - 类型: {montage_class}")
            ue.LogWarning(f"[动画-{tag}] - 完整路径: {montage_full_path}")
            
            # 获取蒙太奇时长
            try:
                montage_length = montage.GetPlayLength()
            except (AttributeError, TypeError):
                montage_length = "未知"
            
            ue.LogWarning(f"[动画-{tag}] - 蒙太奇时长: {montage_length}")
            
            # 获取蒙太奇章节信息
            try:
                montage.GetSectionStartTime
                ue.LogWarning(f"[动画-{tag}] - 蒙太奇章节信息:")
                try:
                    # 尝试获取蒙太奇所有章节
                    try:
                        section_names = montage.GetSectionNames()
                        for section in section_names:
                            section_start = montage.GetSectionStartTime(section)
                            ue.LogWarning(f"[动画-{tag}]   * 章节: {section}, 开始时间: {section_start}秒")
                    except (AttributeError, TypeError):
                        pass
                except Exception as section_ex:
                    ue.LogWarning(f"[动画-{tag}] 获取章节信息失败: {str(section_ex)}")
            except (AttributeError, TypeError):
                pass
            
            # 优先使用Character类的PlayAnimMontage方法
            try:
                play_anim_montage_method = self.PlayAnimMontage
                try:
                    ue.LogWarning(f"[动画-{tag}] 尝试使用Character.PlayAnimMontage方法...")
                    duration = play_anim_montage_method(montage, play_rate, start_section_name)
                    if duration > 0:
                        ue.LogWarning(f"[动画-{tag}] 通过Character.PlayAnimMontage成功播放蒙太奇，持续时间: {duration}秒")
                        
                        # 获取动画实例以设置回调
                        anim_instance = mesh_to_use.GetAnimInstance()
                        if anim_instance:
                            # 打印动画实例信息
                            try:
                                anim_instance_name = anim_instance.GetName()
                            except (AttributeError, TypeError):
                                anim_instance_name = "未知实例"
                            
                            anim_instance_class = type(anim_instance).__name__
                            
                            try:
                                anim_instance_path = anim_instance.GetPathName()
                            except (AttributeError, TypeError):
                                anim_instance_path = "未知路径"
                            
                            ue.LogWarning(f"[动画-{tag}] 动画实例信息:")
                            ue.LogWarning(f"[动画-{tag}] - 名称: {anim_instance_name}")
                            ue.LogWarning(f"[动画-{tag}] - 类型: {anim_instance_class}")
                            ue.LogWarning(f"[动画-{tag}] - 路径: {anim_instance_path}")
                            
                            # 获取骨骼信息
                            try:
                                skel_mesh_attr = getattr(mesh_to_use, 'SkeletalMesh', None)
                                if skel_mesh_attr:
                                    skel_mesh = mesh_to_use.SkeletalMesh
                                    try:
                                        skel_mesh_name = skel_mesh.GetName()
                                    except (AttributeError, TypeError):
                                        skel_mesh_name = "未知骨架网格体"
                                        
                                    try:
                                        skel_mesh_path = skel_mesh.GetPathName()
                                    except (AttributeError, TypeError):
                                        skel_mesh_path = "未知路径"
                                    
                                    ue.LogWarning(f"[动画-{tag}] 骨骼网格体信息:")
                                    ue.LogWarning(f"[动画-{tag}] - 名称: {skel_mesh_name}")
                                    ue.LogWarning(f"[动画-{tag}] - 路径: {skel_mesh_path}")
                                    
                                    # 获取骨架信息
                                    try:
                                        skeleton_attr = getattr(skel_mesh, 'Skeleton', None)
                                        if skeleton_attr:
                                            skeleton = skel_mesh.Skeleton
                                            try:
                                                skeleton_name = skeleton.GetName()
                                            except (AttributeError, TypeError):
                                                skeleton_name = "未知骨架"
                                                
                                            try:
                                                skeleton_path = skeleton.GetPathName()
                                            except (AttributeError, TypeError):
                                                skeleton_path = "未知路径"
                                            
                                            ue.LogWarning(f"[动画-{tag}] 骨架信息:")
                                            ue.LogWarning(f"[动画-{tag}] - 名称: {skeleton_name}")
                                            ue.LogWarning(f"[动画-{tag}] - 路径: {skeleton_path}")
                                            
                                            # 尝试获取骨骼数量
                                            try:
                                                get_bone_num_method = getattr(skeleton, 'GetBoneNum', None)
                                                if get_bone_num_method:
                                                    bone_count = skeleton.GetBoneNum()
                                                    ue.LogWarning(f"[动画-{tag}] - 骨骼数量: {bone_count}")
                                                    
                                                    # 列出部分关键骨骼
                                                    if bone_count > 0:
                                                        try:
                                                            get_bone_name_method = getattr(skeleton, 'GetBoneName', None)
                                                            if get_bone_name_method:
                                                                ue.LogWarning(f"[动画-{tag}] - 关键骨骼:")
                                                                important_indices = [0, min(1, bone_count-1), min(bone_count//2, bone_count-1), bone_count-1]
                                                                for idx in important_indices:
                                                                    bone_name = skeleton.GetBoneName(idx)
                                                                    ue.LogWarning(f"[动画-{tag}]   * 索引 {idx}: {bone_name}")
                                                        except (AttributeError, TypeError):
                                                            pass
                                            except (AttributeError, TypeError):
                                                pass
                                    except (AttributeError, TypeError):
                                        pass
                            except (AttributeError, TypeError):
                                pass
                            
                            # 设置回调
                            ue.LogWarning(f"[动画-{tag}] 设置动画完成回调...")
                            self._setup_animation_callbacks(anim_instance, montage, completion_callback, tag)
                        else:
                            # 如果无法获取动画实例，使用定时器作为备用
                            if completion_callback:
                                import threading
                                timer = threading.Timer(duration / play_rate, completion_callback)
                                timer.start()
                                ue.LogWarning(f"[动画-{tag}] 无法获取动画实例，使用定时器回调，将在{duration / play_rate}秒后调用")
                                
                        ue.LogWarning(f"[动画-{tag}] 播放成功，预计持续时间: {duration / play_rate}秒")
                        return True
                except Exception as e:
                    ue.LogWarning(f"[动画-{tag}] 通过Character.PlayAnimMontage播放失败: {e}，尝试其他方法")
            except (AttributeError, TypeError):
                ue.LogWarning(f"[动画-{tag}] Character类没有PlayAnimMontage方法，尝试其他方法")
            
            # 获取动画实例
            anim_instance = mesh_to_use.GetAnimInstance()
            if not anim_instance:
                ue.LogError(f"[动画-{tag}] 无法获取动画实例")
                return False
                
            # 打印动画实例详细信息
            anim_instance_class = type(anim_instance).__name__
            
            try:
                anim_instance_name = anim_instance.GetName()
            except (AttributeError, TypeError):
                anim_instance_name = "未知实例"
                
            try:
                anim_instance_path = anim_instance.GetPathName()
            except (AttributeError, TypeError):
                anim_instance_path = "未知路径"
            
            ue.LogWarning(f"[动画-{tag}] 动画实例详细信息:")
            ue.LogWarning(f"[动画-{tag}] - 名称: {anim_instance_name}")
            ue.LogWarning(f"[动画-{tag}] - 类型: {anim_instance_class}")
            ue.LogWarning(f"[动画-{tag}] - 路径: {anim_instance_path}")
            
            # 获取当前播放的其他蒙太奇
            try:
                get_current_active_montage_method = getattr(anim_instance, 'GetCurrentActiveMontage', None)
                if get_current_active_montage_method:
                    try:
                        current_montage = anim_instance.GetCurrentActiveMontage()
                        if current_montage:
                            try:
                                current_montage_name = current_montage.GetName()
                            except (AttributeError, TypeError):
                                current_montage_name = "未知蒙太奇"
                            ue.LogWarning(f"[动画-{tag}] 当前活动蒙太奇: {current_montage_name}")
                    except Exception as montage_ex:
                        ue.LogWarning(f"[动画-{tag}] 获取当前蒙太奇失败: {str(montage_ex)}")
            except (AttributeError, TypeError):
                pass

            # 如果所有方法都失败
            ue.LogError(f"[动画-{tag}] 播放失败，无法播放蒙太奇")
            return False
                
        except Exception as e:
            import traceback
            ue.LogError(f"[动画-{tag}] 播放动画时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            return False
    
    def _setup_animation_callbacks(self, anim_instance, montage, completion_callback, callback_prefix=""):
        """统一的动画回调设置函数
        
        Args:
            anim_instance: 动画实例对象
            montage: 播放的动画蒙太奇对象
            completion_callback: 动画完成时调用的回调函数
            callback_prefix: 回调函数和属性名的前缀，用于区分不同类型的动画
        """
        # 记录当前设置的回调函数，以便于后续可能需要手动调用
        setattr(self, f"_current_{callback_prefix}_completion_callback", completion_callback)
        try:
            delegate_prefix = f"_{callback_prefix}_" if callback_prefix else "_"
            
            # 保存当前激活的回调前缀，用于后续清理
            self._current_active_montage_prefix = callback_prefix
            
            # 1. 注册混出事件回调
            if hasattr(anim_instance, 'OnMontageBlendingOut'):
                # 创建新的回调函数
                def on_blend_out(blend_montage, interrupted):
                    montage_name = blend_montage.GetName() if hasattr(blend_montage, 'GetName') else "Unknown"
                    ue.LogWarning(f"[动画回调] {callback_prefix}蒙太奇混出: {montage_name}, 中断状态: {interrupted}")
                    if completion_callback:
                        completion_callback()
                
                # 保存回调引用以便之后移除
                blend_out_delegate_name = f"{delegate_prefix}blend_out_delegate"
                setattr(self, blend_out_delegate_name, on_blend_out)
                
                # 注册混出回调
                anim_instance.OnMontageBlendingOut.Add(getattr(self, blend_out_delegate_name))
                ue.LogWarning(f"[动画] 已注册{callback_prefix}蒙太奇混出回调")
            
            # 2. 注册结束事件回调
            if hasattr(anim_instance, 'OnMontageEnded'):
                # 创建新的回调函数
                def on_montage_ended(ended_montage, interrupted):
                    montage_name = ended_montage.GetName() if hasattr(ended_montage, 'GetName') else "Unknown"
                    ue.LogWarning(f"[动画回调] {callback_prefix}蒙太奇结束: {montage_name}, 中断状态: {interrupted}")
                    
                    # 动画结束时也要清理所有回调
                    self._clean_all_montage_callbacks(anim_instance)
                
                # 保存回调引用
                montage_ended_delegate_name = f"{delegate_prefix}montage_ended_delegate"
                setattr(self, montage_ended_delegate_name, on_montage_ended)
                
                # 注册结束回调
                anim_instance.OnMontageEnded.Add(getattr(self, montage_ended_delegate_name))
                ue.LogWarning(f"[动画] 已注册{callback_prefix}蒙太奇结束回调")
            
            # 3. 注册开始事件回调（可选）
            if hasattr(anim_instance, 'OnMontageStarted'):
                # 创建新的回调函数
                def on_montage_started(started_montage):
                    montage_name = started_montage.GetName() if hasattr(started_montage, 'GetName') else "Unknown"
                    ue.LogWarning(f"[动画回调] {callback_prefix}蒙太奇开始: {montage_name}")
                    
                # 保存回调引用
                montage_started_delegate_name = f"{delegate_prefix}montage_started_delegate"
                setattr(self, montage_started_delegate_name, on_montage_started)
                
                # 注册开始回调
                anim_instance.OnMontageStarted.Add(getattr(self, montage_started_delegate_name))
                ue.LogWarning(f"[动画] 已注册{callback_prefix}蒙太奇开始回调")
            
        except Exception as e:
            import traceback
            ue.LogError(f"[动画] 设置{callback_prefix}蒙太奇回调时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
    
    def _clean_montage_callback(self, anim_instance, callback_type, callback_prefix=None):
        """清理指定类型的蒙太奇回调
        
        Args:
            anim_instance: 动画实例对象
            callback_type: 回调类型，可以是 "blend_out", "ended", "started" 等
            callback_prefix: 回调前缀，如果为None则使用当前活动的前缀
        """
        try:
            # 获取当前活动的回调前缀
            prefix = callback_prefix if callback_prefix is not None else getattr(self, '_current_active_montage_prefix', "")
            delegate_prefix = f"_{prefix}_" if prefix else "_"
            
            # 构建完整的委托名称
            delegate_name = f"{delegate_prefix}{callback_type}_delegate"
            
            # 根据回调类型移除不同的回调
            if callback_type == "blend_out" and hasattr(anim_instance, 'OnMontageBlendingOut'):
                if hasattr(self, delegate_name):
                    anim_instance.OnMontageBlendingOut.Remove(getattr(self, delegate_name))
                    ue.LogWarning(f"[动画清理] 已移除{prefix}蒙太奇混出回调")
                    delattr(self, delegate_name)
                    
            elif callback_type == "ended" and hasattr(anim_instance, 'OnMontageEnded'):
                if hasattr(self, delegate_name):
                    anim_instance.OnMontageEnded.Remove(getattr(self, delegate_name))
                    ue.LogWarning(f"[动画清理] 已移除{prefix}蒙太奇结束回调")
                    delattr(self, delegate_name)
                    
            elif callback_type == "started" and hasattr(anim_instance, 'OnMontageStarted'):
                if hasattr(self, delegate_name):
                    anim_instance.OnMontageStarted.Remove(getattr(self, delegate_name))
                    ue.LogWarning(f"[动画清理] 已移除{prefix}蒙太奇开始回调")
                    delattr(self, delegate_name)
                    
        except Exception as e:
            import traceback
            ue.LogError(f"[动画清理] 清理{callback_type}回调时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
    
    def _clean_all_montage_callbacks(self, anim_instance):
        """清理所有蒙太奇回调类型
        
        Args:
            anim_instance: 动画实例对象
        """
        try:
             # 清理所有蒙太奇回调类型
            callback_types = ["blend_out", "ended", "started"]
            
            # 清理与不同前缀相关的所有回调
            prefixes = ["attack", "reload", ""]  # 包含空字符串以处理没有前缀的情况
            
            # 保存当前状态，以便可以在清理回调后恢复
            is_reloading = getattr(self, '_is_reloading', False)
            
            # 直接移除所有委托，不依赖于属性检查
            if hasattr(anim_instance, 'OnMontageBlendingOut'):
                anim_instance.OnMontageBlendingOut.Clear()
                
            if hasattr(anim_instance, 'OnMontageEnded'):
                anim_instance.OnMontageEnded.Clear()
                
            if hasattr(anim_instance, 'OnMontageStarted'):
                anim_instance.OnMontageStarted.Clear()
            
            # 如果正在换弹，则在清理回调后检查并调用换弹完成函数
            if is_reloading:
                ue.LogWarning("[动画清理] 检测到换弹回调被清理，手动触发换弹完成")
                self._complete_reload()
            
            ue.LogWarning("[动画清理] 已清理所有蒙太奇回调")
                    
        except Exception as e:
            import traceback
            ue.LogError(f"[动画清理] 清理所有回调时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
    
    def _reset_state(self, state_type="general"):
        """统一的状态重置函数，替代多个重复的状态重置函数
        
        Args:
            state_type: 状态类型，可以是 "attack", "reload" 或其他
        """
        try:
            # 根据状态类型设置不同的重置逻辑
            if state_type == "attack":
                # 获取攻击状态前的值，用于日志
                prev_state = self.AttackState
                
                # 安全地重置攻击状态
                self.AttackState = False
                self.LockOrientation = False
                
                state_name = "攻击"
                prev_state_value = prev_state
                new_state_value = self.AttackState
            
            elif state_type == "reload":
                # 获取换弹状态前的值，用于日志
                prev_state = getattr(self, '_is_reloading', False)
                
                # 安全地重置换弹状态
                self._is_reloading = False
                self.LockOrientation = False
                
                state_name = "换弹"
                prev_state_value = prev_state
                new_state_value = self._is_reloading
                
            else:
                # 通用状态重置
                self.AttackState = False
                self.LockOrientation = False
                if hasattr(self, '_is_reloading'):
                    self._is_reloading = False
                
                state_name = "通用"
                prev_state_value = True  # 假设之前是活动状态
                new_state_value = False
            
            # 确保角色回到待机状态
            if self.Mesh:
                # 停止所有当前正在播放的蒙太奇
                anim_instance = self.Mesh.GetAnimInstance()
                if anim_instance:
                    # 如果当前有蒙太奇在播放，停止它
                    if hasattr(anim_instance, 'Montage_Stop'):
                        # 使用短暂的混合时间平滑过渡
                        blend_out_time = 0.25
                        anim_instance.Montage_Stop(blend_out_time)
                        ue.LogWarning(f"[动画] 停止所有蒙太奇，混合时间: {blend_out_time}秒")
                    
                    # 可选：重置动画蓝图状态机变量
                    if hasattr(anim_instance, 'SetVariableByName'):
                        # 重置所有可能影响待机状态的变量
                        anim_instance.SetVariableByName('bIsFalling', False)
                        anim_instance.SetVariableByName('bIsAttacking', False)
                        anim_instance.SetVariableByName('bIsInAir', False)
                        ue.LogWarning("[动画] 重置动画蓝图状态机变量")
            
            ue.LogWarning(f"[状态] 重置{state_name}状态: 从 {prev_state_value} 变为 {new_state_value}")
        
        except Exception as e:
            # 捕获所有可能的异常，确保不会崩溃
            import traceback
            ue.LogError(f"[动画] 重置{state_name if 'state_name' in locals() else ''}状态时发生错误: {str(e)}")
            ue.LogError(traceback.format_exc())
            
            # 尝试最基本的重置以防止卡住
            try:
                self.AttackState = False
                self.LockOrientation = False
                if hasattr(self, '_is_reloading'):
                    self._is_reloading = False
            except:
                pass
    
    # 网络相关
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
            game_instance = ue.GameplayStatics.GetGameInstance(self)
            # 使用正确的方式获取和转换MyGameInstance
            my_game_instance_class = ue.LoadClass('/Game/ThirdPersonCPP/Blueprints/MyGameInstance.MyGameInstance_C')
            my_game_instance = None
            
            # 先检查类是否成功加载
            if my_game_instance_class:
                # 尝试将game_instance转换为MyGameInstance类型
                try:
                    # 尝试另一种转换方式
                    if hasattr(game_instance, 'GetClass') and game_instance.GetClass().IsChildOf(my_game_instance_class):
                        my_game_instance = game_instance
                    else:
                        ue.LogWarning("[登录] 使用直接引用GameInstance，而不进行转换")
                        my_game_instance = game_instance
                except Exception as ex:
                    ue.LogWarning(f"[登录] 转换GameInstance时出错: {ex}，使用直接引用")
                    my_game_instance = game_instance
            else:
                ue.LogWarning("[登录] 无法加载MyGameInstance类，使用原始GameInstance")
                my_game_instance = game_instance
                
            # 安全获取is_new_game值
            is_new_game = False
            if my_game_instance and hasattr(my_game_instance, 'instance_isnewgame'):
                is_new_game = my_game_instance.instance_isnewgame

            success = ue_site.login(username, password, is_new_game)
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
            
            # 更新等级信息
            if "MaxLevel" in user_data:
                try:
                    self.MaxLevel = int(user_data["MaxLevel"])
                except (TypeError, ValueError):
                    ue.LogWarning(f"[更新] 无法将MaxLevel值 '{user_data['MaxLevel']}' 转换为整数，使用原值")
                    
            if "CurrentLevel" in user_data:
                try:
                    self.CurrentLevel = int(user_data["CurrentLevel"])
                except (TypeError, ValueError):
                    ue.LogWarning(f"[更新] 无法将CurrentLevel值 '{user_data['CurrentLevel']}' 转换为整数，使用原值")
            
            # 添加保存时间的检查和显示    
            save_time = user_data.get("save_time", "未知")
            
            ue.LogWarning(f"[更新] 从服务器更新角色数据:")
            ue.LogWarning(f"[更新] - 生命值: {self.CurrentHP}/{self.MaxHP}")
            ue.LogWarning(f"[更新] - 经验值: {self.CurrentEXP}/{self.MaxEXP}")
            ue.LogWarning(f"[更新] - 等级: {self.CurrentLevel}/{self.MaxLevel}")
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
                "MaxHP": self.MaxHP,
                "CurrentHP": self.CurrentHP,
                "MaxEXP": self.MaxEXP,
                "CurrentEXP": self.CurrentEXP,
                "MaxLevel": self.MaxLevel,
                "CurrentLevel": self.CurrentLevel,
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
            ue.LogWarning(f"[更新] - 等级: {self.CurrentLevel}/{self.MaxLevel}")
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
                
                # 启动定时器线程
                threading.Thread(target=check_save_result).start()
            else:
                ue.LogError("[保存] 保存游戏数据请求发送失败")
                
            return success
        except Exception as e:
            ue.LogError(f"[保存] 触发保存游戏数据时出错: {str(e)}")
            import traceback
            ue.LogError(f"[保存] 错误详情: {traceback.format_exc()}")
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
                    max_attempts = 4
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
                
                # 启动定时器线程
                threading.Thread(target=check_load_result).start()
            else:
                ue.LogError("[加载] 加载游戏数据请求发送失败")
                
            return success
        except Exception as e:
            ue.LogError(f"[加载] 触发加载游戏数据时出错: {str(e)}")
            import traceback
            ue.LogError(f"[加载] 错误详情: {traceback.format_exc()}")
            return False
    
    def _initialize_mesh(self):
        """
        初始化角色网格体、动画蓝图和相关碰撞设置
        基于UE标准第三人称角色模板优化实现
        """
        try:
            ue.LogWarning("开始初始化角色网格体...")
            
            # 检查是否已有Mesh组件
            if not self.Mesh:
                ue.LogError("无法获取角色的Mesh组件，初始化失败")
                return False
                
            # 加载骨骼网格体资源 
            # 直接使用SetSkeletalMesh方法设置网格体，提高API兼容性
            skeletal_mesh = ue.LoadObject(ue.SkeletalMesh, "/Game/Mannequin/Character/Mesh/SK_Mannequin")
            if not skeletal_mesh:
                ue.LogError("无法加载骨骼网格体: SK_Mannequin")
                return False
            
            # 设置骨骼网格体
            if hasattr(self.Mesh, 'SetSkeletalMesh'):
                self.Mesh.SetSkeletalMesh(skeletal_mesh)
            else:
                self.Mesh.SkeletalMesh = skeletal_mesh
                
            # 设置网格体位置和旋转 - 基于标准模板的最佳实践值
            self.Mesh.SetRelativeLocation(ue.Vector(0.0, 0.0, -97.0))  # 调整为-97.0以更好地匹配胶囊体
            self.Mesh.SetRelativeRotation(ue.Rotator(0.0, 270.0, 0.0))  # 使用270度使角色朝向正确
            self.Mesh.bVisible = True
                
            # 设置动画蓝图 - 使用明确的动画模式设置
            self.Mesh.AnimationMode = ue.EAnimationMode.AnimationBlueprint
            
            # 加载动画蓝图类 - 确保路径后面有"_C"后缀
            anim_bp_path = "/Game/ThirdPersonCPP/Blueprints/AnimeBP/MyCharacterAnimBlueprint.MyCharacterAnimBlueprint_C"
            anim_class = ue.LoadClass(anim_bp_path)
            if not anim_class:
                # 尝试使用模板默认动画蓝图作为备选
                backup_anim_bp_path = "/Game/Mannequin/Animations/ThirdPerson_AnimBP.ThirdPerson_AnimBP_C"
                anim_class = ue.LoadClass(backup_anim_bp_path)
                if not anim_class:
                    ue.LogError("无法加载动画蓝图类")
                    return False
                else:
                    ue.LogWarning(f"使用备选动画蓝图: {backup_anim_bp_path}")
            
            # 设置动画类，优先使用SetAnimClass方法
            if hasattr(self.Mesh, 'SetAnimClass'):
                self.Mesh.SetAnimClass(anim_class)
            else:
                self.Mesh.AnimClass = anim_class
            
            # 设置网格体碰撞属性 - 简化碰撞设置，使用设置碰撞配置文件代替单独设置
            if hasattr(self.Mesh, 'SetCollisionProfileName'):
                # 使用预定义的角色网格体碰撞配置文件
                self.Mesh.SetCollisionProfileName("CharacterMesh")
            else:
                self.Mesh.CollisionProfileName = "CharacterMesh"
            
            # 确保网格体可见并正确渲染
            self.Mesh.bVisibleInRayTracing = True
            
            # 设置动画始终运行，不因可见性而暂停
            if hasattr(self.Mesh, 'VisibilityBasedAnimTickOption'):
                self.Mesh.VisibilityBasedAnimTickOption = ue.EVisibilityBasedAnimTickOption.AlwaysTickPose
            
            # 设置胶囊体和角色移动组件的属性，确保与网格体匹配
            # 调整胶囊体大小以匹配模型
            if hasattr(self, 'CapsuleComponent'):
                self.CapsuleComponent.CapsuleRadius = 42.0
                self.CapsuleComponent.CapsuleHalfHeight = 96.0
            
            # 配置角色移动组件
            if hasattr(self, 'CharacterMovement'):
                # 确保角色朝向移动方向
                self.CharacterMovement.bOrientRotationToMovement = True
                self.CharacterMovement.RotationRate = ue.Rotator(0.0, 540.0, 0.0)
            
            ue.LogWarning("角色网格体初始化完成!")
            return True
            
        except Exception as e:
            import traceback
            ue.LogError(f"初始化角色网格体时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            return False
            
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
        
        # 攻击状态初始化
        self.AttackState = False
        
        # 经验值初始化
        self.MaxEXP = 100
        self.CurrentEXP = 50
        
        # 等级初始化
        self.MaxLevel = 10
        self.CurrentLevel = 1

        # 弹药数初始化
        self.AllBulletNumber = 300
        self.WeaopnBulletNumber = 30
        
        # 击杀敌人数初始化
        self.KilledEnemies = 0
        
        # 角色状态初始
        self.Died = False
        self.OnHit = False
        self.LockOrientation = False
        
        # 初始化动画相关属性
        self.IsMoving = False
        self.MoveSpeed = 0.0
        self.IsIdle = True

        # 确保weapon属性初始化为None
        # self.weapon = None

        ue.LogWarning(f"玩家属性初始化完成:")
        ue.LogWarning(f"- 生命值: {self.CurrentHP}/{self.MaxHP}")
        ue.LogWarning(f"- 经验值: {self.CurrentEXP}/{self.MaxEXP}")
        ue.LogWarning(f"- 等级: {self.CurrentLevel}/{self.MaxLevel}")
        ue.LogWarning(f"- 总弹药: {self.AllBulletNumber}")
        ue.LogWarning(f"- 当前弹匣: {self.WeaopnBulletNumber}")
        ue.LogWarning(f"- 击杀敌人数: {self.KilledEnemies}")
    
    # 登录相关
    @ue.ufunction(BlueprintCallable=True, Category="Network")
    def _check_connection_status(self):
        """
        定期检查连接状态和认证状态
        检测是否在其他地方登录或被断开服务器连接
        如果发生这些情况，自动返回到登录地图
        """
        try:
            import ue_site
            
            # 获取网络状态单例
            network_status = ue_site.network_status
            
            # 之前的连接状态
            was_connected = hasattr(self, '_last_connected_status') and self._last_connected_status
            was_authenticated = hasattr(self, '_last_auth_status') and self._last_auth_status
            
            # 当前连接状态
            is_connected = network_status.is_connected if hasattr(network_status, 'is_connected') else False
            is_authenticated = network_status.auth_status["is_authenticated"] if hasattr(network_status, 'auth_status') else False
            
            # 保存当前状态用于下次比较
            self._last_connected_status = is_connected
            self._last_auth_status = is_authenticated
            
            # 检测连接断开
            if was_connected and not is_connected:
                ue.LogWarning("[网络监控] 检测到服务器连接断开")
                self._handle_connection_lost()
                return
                
            # 检测认证状态变化（其他地方登录）
            if was_authenticated and not is_authenticated:
                ue.LogWarning("[网络监控] 检测到认证状态变化，可能在其他设备登录")
                self._handle_auth_invalidated()
                return
                
            # 检测被服务器踢出的情况
            if network_status.client_entity and hasattr(network_status.client_entity, 'kicked'):
                if network_status.client_entity.kicked:
                    reason = network_status.client_entity.kick_reason if hasattr(network_status.client_entity, 'kick_reason') else "未知原因"
                    ue.LogWarning(f"[网络监控] 被服务器踢出: {reason}")
                    self._handle_kicked(reason)
                    return
                    
        except ImportError:
            ue.LogError("[网络监控] 导入ue_site模块失败")
        except Exception as e:
            import traceback
            ue.LogError(f"[网络监控] 检查连接状态时出错: {str(e)}")
            ue.LogError(traceback.format_exc())

    def _handle_connection_lost(self):
        """处理与服务器连接断开的情况"""
        ue.LogWarning("[网络监控] 处理连接断开事件")
        self._disconnect_from_server()  # 确保清理连接状态
        self._open_start_map()  # 返回登录地图

    def _handle_auth_invalidated(self):
        """处理认证失效的情况（可能是在其他设备登录）"""
        ue.LogWarning("[网络监控] 处理认证失效事件")
        self._disconnect_from_server()
        self._open_start_map()  # 返回登录地图

    def _handle_kicked(self, reason):
        """处理被服务器踢出的情况"""
        ue.LogWarning(f"[网络监控] 处理被踢事件: {reason}")
        self._disconnect_from_server()
        self._open_start_map()  # 返回登录地图

    def _setup_connection_monitor(self):
        """设置连接监控定时器"""
        import threading
        import time
        
        # 检查间隔（秒）
        check_interval = 5.0
        
        # 初始化状态
        self._last_connected_status = False
        self._last_auth_status = False
        
        # 设置标志，用于停止监控线程
        self._should_monitor_connection = True
        
        def monitor_loop():
            while hasattr(self, '_should_monitor_connection') and self._should_monitor_connection:
                self._check_connection_status()
                time.sleep(check_interval)
        
        # 创建并启动监控线程
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        ue.LogWarning("[网络监控] 已启动连接状态监控")
        
        # 保存线程引用
        self._monitor_thread = monitor_thread

    # 移动
    def _move_forward(self, value):
        if value != 0:
            self._apply_directional_movement(value, self._get_direction_vector("forward"))
    
    def _move_right(self, value):
        if value != 0:
            self._apply_directional_movement(value, self._get_direction_vector("right"))
    
    def _get_direction_vector(self, direction):
        """获取指定方向的向量（基于控制器旋转）"""
        # 获取控制器的旋转（相机方向）
        controller_rotation = self.Controller.GetControlRotation()
        # 只使用Yaw旋转创建新的旋转器（保持水平平面移动）
        yaw_rotation = ue.Rotator(0.0, controller_rotation.Yaw, 0.0)
        
        # 获取方向向量
        if hasattr(ue, "KismetMathLibrary"):
            if direction == "forward":
                return ue.KismetMathLibrary.GetForwardVector(yaw_rotation)
            else:
                return ue.KismetMathLibrary.GetRightVector(yaw_rotation)
        else:
            # 备选方案：直接从旋转获取向量
            if direction == "forward":
                return yaw_rotation.GetForwardVector()
            else:
                return yaw_rotation.GetRightVector()
    
    def _apply_directional_movement(self, value, direction_vector):
        """应用方向性移动"""
        self.AddMovementInput(direction_vector, value)
    
    # 鼠标转向
    def _turn_right(self, value):
        self.AddControllerYawInput(value * self.MouseSpeed * ue.GetDeltaTime())
    
    def _look_up(self, value):
        self.AddControllerPitchInput(value * self.MouseSpeed * ue.GetDeltaTime())
    
    # 移动功能
    def _run_start(self):
        """开始奔跑时设置较高的移动速度"""
        self._set_movement_speed(1200.0)
    
    def _run_stop(self):
        """停止奔跑时恢复正常移动速度"""
        self._set_movement_speed(600.0)
    
    def _set_movement_speed(self, speed):
            """设置角色移动速度"""
            if hasattr(self, 'CharacterMovement'):
                old_speed = self.CharacterMovement.MaxWalkSpeed
                self.CharacterMovement.MaxWalkSpeed = speed
                ue.LogWarning(f"移动速度从{old_speed}更改为{speed}")
            else:
                ue.LogError("无法找到CharacterMovement组件")
    
    def _jump(self):
        """
        处理跳跃逻辑，跳跃时临时关闭朝向运动的旋转，跳跃完成后恢复
        """
        # 保存当前朝向运动的状态
        self._previous_orient_to_movement = self.CharacterMovement.bOrientRotationToMovement
        
        # 跳跃时临时关闭朝向运动
        self.CharacterMovement.bOrientRotationToMovement = False
        ue.LogWarning("[跳跃] 开始跳跃，临时关闭朝向运动")
        
        # 调用基类跳跃方法
        self.Jump()
        
        self.CharacterMovement.bOrientRotationToMovement = True
    
    # 音乐音效相关
    def _play_sound(self, sound_path):
        """播放指定路径的音效
    
        Args:
            sound_path (str): 音效资源的路径
        """
        try:
            # 加载音效资源
            sound = ue.LoadObject(ue.SoundBase, sound_path)
            if not sound:
                ue.LogError(f"[音效] 无法加载音效: {sound_path}")
                return False
        
            # 打印音效详细信息
            try:
                sound_name = sound.GetName()
            except (AttributeError, TypeError):
                sound_name = "未知音效"
            
            sound_class = type(sound).__name__
        
            try:
                sound_path_full = sound.GetPathName()
            except (AttributeError, TypeError):
                sound_path_full = sound_path
        
            ue.LogWarning(f"[音效] 播放音效:")
            ue.LogWarning(f"[音效] - 名称: {sound_name}")
            ue.LogWarning(f"[音效] - 类型: {sound_class}")
            ue.LogWarning(f"[音效] - 路径: {sound_path_full}")
        
            # 使用PlaySound2D代替PlaySoundAtLocation来避免位置和旋转参数问题
            ue.GameplayStatics.PlaySound2D(
                self,       # WorldContextObject
                sound,      # 音效资源
                1.0,        # 音量倍数
                1.0,        # 音调倍数
                0.0,        # 起始时间
                None,       # 并发设置
                None        # 子标题
            )
        
            ue.LogWarning(f"[音效] 音效播放成功: {sound_name}")
            return True
        
        except Exception as e:
            import traceback
            ue.LogError(f"[音效] 播放音效时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            return False
    
    def _play_background_music(self):
        """播放循环背景音乐直到游戏结束"""
        try:
            import threading
            import time
        
            # 背景音乐路径
            music_path = "/Game/Sounds/Borislav_Slavov_-_Song_Of_Balduran"
        
            # 加载音乐资源
            music = ue.LoadObject(ue.SoundBase, music_path)
            if not music:
                ue.LogError(f"[音乐] 无法加载背景音乐: {music_path}")
                return False
        
            # 打印音乐详细信息
            try:
                music_name = music.GetName()
            except (AttributeError, TypeError):
                music_name = "未知音乐"
            
            music_class = type(music).__name__
        
            try:
                music_path_full = music.GetPathName()
            except (AttributeError, TypeError):
                music_path_full = music_path
        
            ue.LogWarning(f"[音乐] 播放背景音乐:")
            ue.LogWarning(f"[音乐] - 名称: {music_name}")
            ue.LogWarning(f"[音乐] - 类型: {music_class}")
            ue.LogWarning(f"[音乐] - 路径: {music_path_full}")
        
            # 初始化控制标志
            self.music_should_play = True
        
            # 播放背景音乐的函数
            def play_music_once():
                try:
                    # 播放2D音乐(不受位置影响)
                    ue.GameplayStatics.PlaySound2D(
                        self,          # WorldContextObject
                        music,         # 音乐资源
                        1.0,           # 音量倍数
                        1.0,           # 音调倍数
                        0.0,           # 起始时间
                        None,          # 并发设置
                        None           # 子标题
                    )
                    ue.LogWarning("[音乐] 背景音乐播放中")
                    return True
                except Exception as e:
                    ue.LogError(f"[音乐] 播放音乐时出错: {e}")
                    return False
        
            # 循环播放背景音乐的函数
            def music_loop():
                while hasattr(self, 'music_should_play') and self.music_should_play:
                    try:
                        # 播放音乐
                        play_music_once()
                    
                        # 等待一段时间后再次播放
                        # 这里的等待时间应该根据音乐长度来设置
                        # 稍微短一点以防止中断
                        sleep_time = 175  # 假设音乐长度约3分钟
                    
                        # 分段睡眠，每次检查是否应该停止
                        for _ in range(sleep_time):
                            if not (hasattr(self, 'music_should_play') and self.music_should_play):
                                break
                            time.sleep(1)
                    except Exception as e:
                        ue.LogError(f"[音乐] 循环线程中出错: {e}")
                        # 出错后短暂等待再尝试
                        time.sleep(5)
            
                ue.LogWarning("[音乐] 背景音乐循环已停止")
        
            # 首先立即播放一次
            play_music_once()
        
            # 创建循环播放的后台线程
            music_thread = threading.Thread(target=music_loop, daemon=True)
            music_thread.start()
        
            # 保存线程引用以便在需要时使用
            self.music_thread = music_thread
        
            ue.LogWarning(f"[音乐] 循环背景音乐开始播放: {music_name}")
            return True
        
        except Exception as e:
            import traceback
            ue.LogError(f"[音乐] 播放背景音乐时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            return False