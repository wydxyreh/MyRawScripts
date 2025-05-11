# -*- coding: utf-8 -*-

# ThirdPersonWithPy样例入口模块
# 包含了不关编辑器更新脚本逻辑的功能, 我们称之为hot reload(见release_post_game_modules和hold_pre_game_modules_name)


import sys
import ue
import threading
import os
import json
import time

# 导入网络客户端模块所需的依赖
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Network"))

import sys

# 全局网络状态单例（确保只有一个状态源）
class NetworkStatus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NetworkStatus, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化网络状态"""
        self.network_client = None
        self.client_entity = None
        self.is_network_initialized = False
        self.is_connected = False
        self.auth_status = {
            "is_authenticated": False,
            "username": "",
            "last_login_attempt": 0,
            "login_in_progress": False,
            "login_result": "",
            "error_message": ""
        }

    def get_status_dict(self):
        """返回状态字典，用于调试"""
        return {
            "is_network_initialized": self.is_network_initialized,
            "is_connected": self.is_connected,
            "has_network_client": self.network_client is not None,
            "has_client_entity": self.client_entity is not None,
            "is_authenticated": self.auth_status["is_authenticated"]
        }

# 创建全局单例实例
network_status = NetworkStatus()

def on_init():
	'''此函数会在NEPY插件初始化（StartupModule）时调用，可用于进行一些初始化工作。为最早回调的python接口'''
	print('on_nepy_init')
	import character # noqa
	import monster # noqa
	import rifle # noqa
	import bullet # noqa

	if ue.GIsEditor:
		# 当前是编辑器环境
		import gmcmds
		gmcmds.debug()

		import reloader
		reloader.init_last_reload_time()

		import reload_monitor
		reload_monitor.start()

		pass
	elif ue.IsRunningCommandlet():
		# 当前是命令行模式
		pass
	else:
		# 当前是纯游戏环境
		# 将网络客户端的初始化延迟到on_post_engine_init，确保只在一个地方初始化
		ue.LogWarning("[Network] 游戏环境检测，网络初始化将在on_post_engine_init中进行")

def on_shutdown():
	'''此函数会在NEPY插件初始化（ShutdownModule）时调用。可用于进行一些清理工作。'''


def on_post_engine_init():
	'''此函数是可选函数。如果定义了此函数，则会在引擎初始化完毕（OnPostEngineInit）时调用。回调时机晚于on_init'''
	# 为了启动编辑器的时候识别出在Python定义的类(subclassing), 需要在这里import
	# 这里import的类[不会]在每次play时重新加载
	# import Logic.some_subclassing

	import_preload_subclassing()

	# 初始化网络客户端 - 只在这个时机进行初始化，确保引擎完全初始化后再连接网络
	ue.LogWarning("[网络] 在on_post_engine_init中初始化网络客户端")
	initialize_network_client()
	
	# 在初始化客户端后立即尝试连接服务器，确保游戏开始时已经连接
	# if is_network_initialized:
	# 	ue.LogWarning("[网络] 尝试连接到服务器...")
	# 	if try_connect_server():
	# 		ue.LogWarning("[网络] 已在引擎初始化时成功连接到服务器")
	# 	else:
	# 		ue.LogWarning("[网络] 引擎初始化时连接服务器失败，游戏中可通过按L键重试")


def on_tick(delta_secodes: float):
	'''此函数是可选函数。如果定义了此函数，则会在每帧Tick的时候调用。'''
	# 处理网络事件
	process_network_events()


def on_debug_input(cmd_str: str) -> bool:
	'''此函数是可选函数。如果定义了此函数，则当用户在PythonConsole中输入指令时，会首先回调到该函数。此函数可用于制作复杂的GM指令逻辑。返回值的含义是用户是否已自行处理了命令，若返回False，则PythonConsole会继续eval用户命令。'''
	import gmcmds
	return gmcmds.handle_debug_input(cmd_str)

# 为了启动编辑器的时候识别出在Python定义的类(subclassing), 需要在这里import
# 这里import的类[会]在每次play时被重新加载
def import_preload_subclassing():
	PyGameInstance.hold_pre_game_modules_name()

	import tp_game_mode

def initialize_network_client():
    """初始化网络客户端"""
    global network_status
    import sys
    
    # 在初始化前先记录单例状态
    ue.LogWarning(f"[网络] 初始化前状态: {network_status.get_status_dict()}")
    
    if network_status.is_network_initialized:
        ue.LogWarning("[网络] 网络客户端已经初始化(检查单例)")
        return
    
    try:
        # 确保我们可以导入所需的模块
        import os
        
        # 确保Network路径被正确添加到Python路径
        network_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Network")
        if network_path not in sys.path:
            sys.path.append(network_path)
            ue.LogWarning(f"[网络] 添加网络模块路径: {network_path}")
        
        # 尝试导入必要的模块
        try:
            from Network.server.common.timer import TimerManager
            from Network.sample_client import ClientNetworkManager, ClientEntity
        except ImportError as e:
            ue.LogError(f"[网络] 导入网络模块失败: {str(e)}")
            ue.LogError(f"[网络] 当前Python路径: {sys.path}")
            return
        
        # 创建网络管理器
        tmp_network_client = ClientNetworkManager(host='127.0.0.1', port=2000)
        
        # 创建客户端实体
        tmp_client_entity = ClientEntity(tmp_network_client)
        
        # 设置定时器处理网络事件
        TimerManager.addRepeatTimer(0.001, TimerManager.scheduler)
        TimerManager.addRepeatTimer(0.01, _process_network_internal)
        TimerManager.addRepeatTimer(0.1, _process_messages_internal)
        
        # 更新单例状态
        network_status.network_client = tmp_network_client
        network_status.client_entity = tmp_client_entity
        network_status.is_network_initialized = True
        
        ue.LogWarning("[网络] 网络客户端初始化完成")
        ue.LogWarning(f"[网络] 初始化后状态: {network_status.get_status_dict()}")
        
    except ImportError as e:
        ue.LogError(f"[网络] 初始化网络客户端失败: {str(e)}")
        ue.LogError("[网络] 请确保 Network 目录及依赖项目已正确安装")
    except Exception as e:
        ue.LogError(f"[网络] 初始化网络客户端失败: {str(e)}")

def _background_connect_attempts():
	"""在后台定期尝试连接服务器的函数"""
	global network_status
	
	max_attempts = 10  # 最大尝试次数
	attempt_count = 0
	
	while not network_status.is_network_initialized and attempt_count < max_attempts:
		attempt_count += 1
		ue.LogWarning(f"[Network] 后台尝试连接服务器 (尝试 {attempt_count}/{max_attempts})...")
		
		if try_connect_server():
			ue.LogWarning("[Network] 后台连接成功，网络功能现已可用")
			return
		
		# 每次尝试之间等待3秒
		time.sleep(3)
	
	if not network_status.is_network_initialized:
		ue.LogError("[Network] 达到最大尝试次数，无法连接到服务器，网络功能将不可用")

def try_connect_server():
	"""尝试连接服务器
	
	Returns:
		bool: 是否成功连接
	"""
	global network_status
	
	if not network_status.network_client or not network_status.client_entity:
		ue.LogError("[网络] 网络客户端未初始化，无法连接服务器")
		return False
	
	# 如果已经连接，则不需要再次连接
	if network_status.is_connected and network_status.network_client.connected:
		ue.LogWarning("[网络] 已经连接到服务器")
		return True
	
	try:
		ue.LogWarning("[网络] 正在尝试连接服务器...")
		connected = network_status.network_client.connect()
		
		if connected:
			network_status.is_connected = True
			ue.LogWarning("[网络] 成功连接到服务器")
			return True
		else:
			network_status.is_connected = False
			ue.LogWarning("[网络] 连接服务器失败，游戏中可能无法使用网络功能")
			return False
			
	except Exception as e:
		network_status.is_connected = False
		ue.LogError(f"[网络] 连接服务器时发生错误: {str(e)}")
		return False

def _process_network_internal():
	"""内部处理网络事件的函数，由定时器调用"""
	global network_status
	
	if not network_status.network_client or not network_status.client_entity:
		return
		
	try:
		# 处理网络并获取数据
		data_list = network_status.network_client.process()
		
		# 处理接收到的数据
		if data_list:
			network_status.client_entity.pending_messages.extend(data_list)
	except Exception as e:
		ue.LogError(f"[Network] 处理网络事件时出错: {str(e)}")

def _process_messages_internal():
	"""内部处理消息队列的函数，由定时器调用"""
	global network_status
    
	if not network_status.client_entity or not network_status.client_entity.pending_messages:
		return
        
	try:
		# 批量处理消息
		messages_to_process = network_status.client_entity.pending_messages.copy()
		network_status.client_entity.pending_messages = []
        
		for data in messages_to_process:
			ue.LogWarning(f"[网络] 处理接收到的消息：长度={len(data)}")
			network_status.client_entity.caller.parse_rpc(data)
            
		# 如果处理了登录响应，确保与auth_status同步
		if network_status.client_entity.authenticated:
			network_status.auth_status["is_authenticated"] = True
			network_status.auth_status["login_in_progress"] = False
			network_status.auth_status["login_result"] = "成功"
        
	except Exception as e:
		ue.LogError(f"[Network] 处理消息队列时出错: {str(e)}")
		# 记录详细错误
		import traceback
		ue.LogError(f"[Network] 错误详情: {traceback.format_exc()}")

def process_network_events():
	"""在游戏每帧处理网络事件，此函数在on_tick中被调用"""
	global network_status
	
	# 如果网络未初始化，则不做任何处理
	if not network_status.is_network_initialized:
		return
		
	# 使用定时器机制处理，这里可以添加额外的处理逻辑
	try:
		if network_status.network_client and network_status.client_entity:
			# 手动调用一次网络处理函数
			_process_network_internal()
			_process_messages_internal()
	except Exception as e:
		ue.LogError(f"[网络] 处理网络事件时出错: {str(e)}")

def login(username, password):
	"""登录服务器
	
	Args:
		username (str): 用户名
		password (str): 密码
		
	Returns:
		bool: 是否成功发送登录请求
	"""
	global network_status
    
	if not network_status.is_network_initialized or not network_status.client_entity:
		error_msg = "[网络] 网络客户端未初始化，无法登录"
		ue.LogError(error_msg)
		network_status.auth_status["error_message"] = error_msg
		return False
    
	# 如果用户已经登录，就不再尝试登录
	if network_status.auth_status["is_authenticated"]:
		ue.LogWarning(f"[网络] 用户 {network_status.auth_status['username']} 已登录，无需重复登录")
		return True
        
	# 避免频繁重复登录的逻辑，记录上次登录尝试时间
	current_time = time.time()
    
	# 如果登录操作正在进行中且未超过10秒，不再尝试登录
	if network_status.auth_status["login_in_progress"]:
		# 如果上一次登录请求已经超过10秒，则重置状态
		if current_time - network_status.auth_status["last_login_attempt"] > 10.0:
			ue.LogWarning("[网络] 上一次登录请求已超时，重置登录状态")
			network_status.auth_status["login_in_progress"] = False
		else:
			ue.LogWarning("[网络] 登录操作正在进行中，请等待")
			return False
    
	# 更新最后登录尝试时间和状态
	network_status.auth_status["last_login_attempt"] = current_time
	network_status.auth_status["login_in_progress"] = True
	network_status.auth_status["username"] = username
	network_status.auth_status["login_result"] = "等待服务器响应"
	network_status.auth_status["error_message"] = ""
    
	# 检查网络	# 检查网络连接
	if not network_status.is_connected or not network_status.network_client.connected:
		ue.LogWarning("[网络] 未连接到服务器，尝试重新连接")
		connected = try_connect_server()
		if not connected:
			error_msg = "[网络] 无法连接到服务器，登录失败"
			ue.LogError(error_msg)
			network_status.auth_status["login_in_progress"] = False
			network_status.auth_status["error_message"] = error_msg
			network_status.auth_status["login_result"] = "失败"
			return False
    
	try:
		# 设置登录凭据
		network_status.client_entity.username = username
		network_status.client_entity.password = password
        
		# 执行登录
		ue.LogWarning(f"[网络] 正在向服务器发送登录请求: 用户名={username}")
		login_result = network_status.client_entity.login()
        
		if login_result:
			ue.LogWarning("[网络] 登录请求已发送，等待服务器响应...")
			# 注意：此时登录过程尚未完成，需要等待服务器回调
			return True
		else:
			network_status.auth_status["login_in_progress"] = False
			network_status.auth_status["login_result"] = "请求发送失败"
			ue.LogError("[网络] 登录请求发送失败")
			return False
	except Exception as e:
		error_msg = f"[网络] 登录时出错: {str(e)}"
		ue.LogError(error_msg)
		network_status.auth_status["login_in_progress"] = False
		network_status.auth_status["error_message"] = error_msg
		network_status.auth_status["login_result"] = "失败"
		import traceback
		ue.LogError(f"[网络] 错误详情: {traceback.format_exc()}")
		return False

def logout():
	"""登出服务器
	
	Returns:
		bool: 是否成功发送登出请求
	"""
	global network_status
	
	if not network_status.is_network_initialized or not network_status.client_entity:
		ue.LogError("[Network] 网络客户端未初始化，无法登出")
		return False
	
	try:
		return network_status.client_entity.logout()
	except Exception as e:
		ue.LogError(f"[Network] 登出时出错: {str(e)}")
		return False

def save_user_data(data):
	"""保存用户数据
	
	Args:
		data (dict): 要保存的用户数据
		
	Returns:
		bool: 是否成功发送保存请求
	"""
	global network_status
	
	if not network_status.is_network_initialized or not network_status.client_entity:
		ue.LogError("[Network] 网络客户端未初始化，无法保存数据")
		return False
	
	try:
		# 将数据转换为JSON
		data_json = json.dumps(data)
		return network_status.client_entity.save_user_data(data_json)
	except Exception as e:
		ue.LogError(f"[Network] 保存用户数据时出错: {str(e)}")
		return False

def load_user_data():
	"""从服务器加载用户数据
	
	Returns:
		bool: 是否成功发送加载请求
	"""
	global network_status
	
	if not network_status.is_network_initialized or not network_status.client_entity:
		ue.LogError("[Network] 网络客户端未初始化，无法加载数据")
		return False
	
	try:
		return network_status.client_entity.load_user_data()
	except Exception as e:
		ue.LogError(f"[Network] 加载用户数据时出错: {str(e)}")
		return False

def get_user_data():
	"""获取当前客户端的用户数据
	
	Returns:
		dict: 用户数据
	"""
	global network_status
	
	if not network_status.is_network_initialized or not network_status.client_entity:
		ue.LogError("[Network] 网络客户端未初始化，无法获取数据")
		return {}
	
	return network_status.client_entity.user_data if hasattr(network_status.client_entity, 'user_data') else {}

def is_authenticated():
	"""检查用户是否已认证
	
	Returns:
		bool: 是否已认证
	"""
	global network_status
	
	if not network_status.is_network_initialized or not network_status.client_entity:
		return False
		
	# 同步 client_entity 的认证状态到我们的全局状态
	if hasattr(network_status.client_entity, 'authenticated'):
		network_status.auth_status["is_authenticated"] = network_status.client_entity.authenticated
		
	return network_status.auth_status["is_authenticated"]
	
def get_auth_status():
	"""获取当前认证状态详情
	
	Returns:
		dict: 认证状态详情
	"""
	global network_status
	
	# 如果可能，同步 client_entity 的状态
	if network_status.client_entity and hasattr(network_status.client_entity, 'authenticated'):
		network_status.auth_status["is_authenticated"] = network_status.client_entity.authenticated
		
	# 返回完整认证状态信息
	return network_status.auth_status
	
# 回调函数: 在登录成功时被调用
def on_login_success(token):
	"""登录成功的回调函数，由ClientEntity调用
    
	Args:
		token (str): 登录成功后获取的会话令牌
	"""
	global network_status
    
	network_status.auth_status["is_authenticated"] = True
	network_status.auth_status["login_in_progress"] = False
	network_status.auth_status["login_result"] = "成功"
	network_status.auth_status["error_message"] = ""
    
	# 确保client_entity知道登录已成功
	if network_status.client_entity:
		network_status.client_entity.authenticated = True
		network_status.client_entity.token = token
    
	# 更详细的登录成功信息
	ue.LogWarning(f"[网络] 用户 {network_status.auth_status['username']} 登录成功!")
	ue.LogWarning(f"[网络] 认证状态: 已认证，会话已建立")
	ue.LogWarning(f"[网络] 登录完成，现在可以安全地保存和加载用户数据")

# 回调函数: 在登录失败时被调用
def on_login_failure(error_message):
	"""登录失败的回调函数，由ClientEntity调用

	Args:
		error_message (str): 登录失败的错误信息
	"""
	global network_status

	network_status.auth_status["is_authenticated"] = False
	network_status.auth_status["login_in_progress"] = False
	network_status.auth_status["login_result"] = "失败"
	network_status.auth_status["error_message"] = error_message

	# 更详细的登录失败信息
	ue.LogError(f"[网络] 用户 {network_status.auth_status['username']} 登录失败: {error_message}")
	ue.LogError(f"[网络] 认证状态: 未认证，登录请求被拒绝")
	ue.LogError(f"[网络] 请检查用户名和密码是否正确，或者服务器状态")

# 下面的接口调用时机比on_post_engine_init要晚
# 将ProjectSettings里的GameInstanceClass设置为NePyGameInstance，下面的接口才会被回调。
class PyGameInstance(object):
	def init(self):
		'''如有定义，则在UGameInstance::Init()时调用。'''
		import_preload_subclassing()

	def on_start(self):
		'''如有定义，则在UGameInstance::OnStart()时调用，时机比init稍晚。'''
		print('GameInstance start')

	def shutdown(self):
		'''如有定义，则在UGameInstance::Shutdown()时调用。'''
		# 断开网络连接
		global network_status
		if network_status and network_status.client_entity:
			try:
				network_status.client_entity.disconnect()
				ue.LogWarning("[网络] 游戏关闭时断开网络连接")
			except Exception as e:
				ue.LogError(f"[网络] 关闭连接时出错: {str(e)}")
		self.release_post_game_modules()   # 释放游戏启动后加载了哪些模块， 这样第二次启动会重新load(达到不关编辑器更新脚本的效果，复杂情况可能出现未释放干净的bug)

	# def on_pre_world_tick(self, delta_seconds: float):
    #     '''如有定义，则在World开始时Tick'''
    #     pass

    # def on_pre_actor_tick(self, delta_seconds: float):
    #     '''如有定义，则在所有Actor之前Tick'''
    #     pass

    # def on_post_actor_tick(self, delta_seconds: float):
    #     '''如有定义，则在所有Actor之后Tick'''
    #     pass

	def on_tick(self, delta_secodes):
		'''如有定义，则每帧调用。'''
		# print('GameInstance on_tick')
		pass
	
	# 记录游戏启动前加载了哪些模块, 配合release_post_game_modules使用
	@staticmethod
	def hold_pre_game_modules_name():
		# use sys to only record the first time preload_modules.
		pre_game_modules = getattr(sys, 'pre_game_modules', None)
		if not pre_game_modules:  # just record the first time
			pre_game_modules = set(sys.modules.keys())
			setattr(sys, 'pre_game_modules', pre_game_modules)

	def release_post_game_modules(self):
		pre_game_modules = getattr(sys, 'pre_game_modules', None)
		for mname in list(sys.modules.keys()):
			if mname not in pre_game_modules or sys.modules[mname] is None:
				del sys.modules[mname]
