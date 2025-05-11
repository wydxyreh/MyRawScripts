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

# 全局客户端实例
network_client = None
client_entity = None
is_network_initialized = False

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
	ue.LogWarning("[Network] 在on_post_engine_init中初始化网络客户端")
	initialize_network_client()


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

# 网络客户端功能实现
def initialize_network_client():
	"""初始化网络客户端"""
	global network_client, client_entity, is_network_initialized
	
	if is_network_initialized:
		ue.LogWarning("[Network] 网络客户端已经初始化")
		return
	
	try:
		# 确保我们可以导入所需的模块
		import sys
		import os
		
		# 确保Network路径被正确添加到Python路径
		network_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Network")
		if network_path not in sys.path:
			sys.path.append(network_path)
			ue.LogWarning(f"[Network] 添加网络模块路径: {network_path}")
		
		# 尝试导入必要的模块
		try:
			from Network.server.common.timer import TimerManager
			from Network.sample_client import ClientNetworkManager, ClientEntity
		except ImportError as e:
			ue.LogError(f"[Network] 导入网络模块失败: {str(e)}")
			ue.LogError(f"[Network] 当前Python路径: {sys.path}")
			return
		
		# 创建网络管理器
		network_client = ClientNetworkManager(host='127.0.0.1', port=2000)
		
		# 创建客户端实体
		client_entity = ClientEntity(network_client)
		
		# 设置定时器处理网络事件
		TimerManager.addRepeatTimer(0.001, TimerManager.scheduler)
		TimerManager.addRepeatTimer(0.01, _process_network_internal)
		TimerManager.addRepeatTimer(0.1, _process_messages_internal)
		
		ue.LogWarning("[Network] 网络客户端初始化完成")
		
		# 尝试连接服务器 - 使用同步方式连接确保初始化完成
		# 如果连接成功，再设置初始化标志
		if try_connect_server(set_initialized=False):
			is_network_initialized = True
			ue.LogWarning("[Network] 网络功能初始化标志已设置")
		else:
			ue.LogWarning("[Network] 服务器连接失败，将在后台继续尝试连接")
			# 启动一个后台线程定期尝试连接
			threading.Thread(target=_background_connect_attempts, daemon=True).start()
		
	except ImportError as e:
		ue.LogError(f"[Network] 初始化网络客户端失败: {str(e)}")
		ue.LogError("[Network] 请确保 Network 目录及依赖项目已正确安装")
	except Exception as e:
		ue.LogError(f"[Network] 初始化网络客户端失败: {str(e)}")

def _background_connect_attempts():
	"""在后台定期尝试连接服务器的函数"""
	global is_network_initialized
	
	max_attempts = 10  # 最大尝试次数
	attempt_count = 0
	
	while not is_network_initialized and attempt_count < max_attempts:
		attempt_count += 1
		ue.LogWarning(f"[Network] 后台尝试连接服务器 (尝试 {attempt_count}/{max_attempts})...")
		
		if try_connect_server(set_initialized=True):
			ue.LogWarning("[Network] 后台连接成功，网络功能现已可用")
			return
		
		# 每次尝试之间等待3秒
		time.sleep(3)
	
	if not is_network_initialized:
		ue.LogError("[Network] 达到最大尝试次数，无法连接到服务器，网络功能将不可用")

def try_connect_server(set_initialized=False):
	"""尝试连接服务器
	
	Args:
		set_initialized (bool): 是否在连接成功后设置initialized标志
		
	Returns:
		bool: 是否成功连接
	"""
	global network_client, client_entity, is_network_initialized
	
	if not network_client or not client_entity:
		ue.LogError("[Network] 网络客户端未初始化，无法连接服务器")
		return False
	
	try:
		ue.LogWarning("[Network] 正在尝试连接服务器...")
		connected = network_client.connect()
		
		if connected:
			ue.LogWarning("[Network] 成功连接到服务器")
			# 在连接成功后设置初始化标志
			if set_initialized:
				is_network_initialized = True
				ue.LogWarning("[Network] 网络功能初始化标志已设置")
			return True
		else:
			ue.LogWarning("[Network] 连接服务器失败，游戏中可能无法使用网络功能")
			return False
			
	except Exception as e:
		ue.LogError(f"[Network] 连接服务器时发生错误: {str(e)}")
		return False

def _process_network_internal():
	"""内部处理网络事件的函数，由定时器调用"""
	global network_client, client_entity
	
	if not network_client or not client_entity:
		return
		
	try:
		# 处理网络并获取数据
		data_list = network_client.process()
		
		# 处理接收到的数据
		if data_list:
			client_entity.pending_messages.extend(data_list)
	except Exception as e:
		ue.LogError(f"[Network] 处理网络事件时出错: {str(e)}")

def _process_messages_internal():
	"""内部处理消息队列的函数，由定时器调用"""
	global client_entity
	
	if not client_entity or not client_entity.pending_messages:
		return
		
	try:
		# 批量处理消息
		for data in client_entity.pending_messages:
			client_entity.caller.parse_rpc(data)
			
		# 清空消息队列
		client_entity.pending_messages = []
	except Exception as e:
		ue.LogError(f"[Network] 处理消息队列时出错: {str(e)}")

def process_network_events():
	"""在游戏每帧处理网络事件，此函数在on_tick中被调用"""
	# 使用定时器机制处理，这里无需额外操作
	pass

def login(username, password):
    """登录服务器
	
    Args:
        username (str): 用户名
        password (str): 密码
		
    Returns:
        bool: 是否成功发送登录请求
    """
    global client_entity, network_client, is_network_initialized
    
    if not is_network_initialized or not client_entity:
        ue.LogError("[Network] 网络客户端未初始化，无法登录")
        return False
    
    # 如果用户已经登录，就不再尝试登录
    if client_entity.authenticated:
        ue.LogWarning("[Network] 用户已登录，无需重复登录")
        return True
        
    # 避免频繁重复登录的逻辑，记录上次登录尝试时间
    current_time = time.time()
    last_login_time = getattr(client_entity, '_last_login_time', 0)
    
    # 如果登录操作正在进行中且未超过10秒，不再尝试登录
    if hasattr(client_entity, 'login_in_progress') and client_entity.login_in_progress:
        # 如果上一次登录请求已经超过10秒，则重置状态
        if current_time - last_login_time > 10.0:
            ue.LogWarning("[Network] 上一次登录请求已超时，重置状态")
            client_entity.login_in_progress = False
        else:
            ue.LogWarning("[Network] 登录操作正在进行中，请等待")
            return False
    
    # 更新最后登录尝试时间
    client_entity._last_login_time = current_time
    
    # 如果强制登录标记存在，清除它
    if hasattr(client_entity, '_force_login'):
        delattr(client_entity, '_force_login')
    
    # 检查网络连接
    if not network_client.connected:
        ue.LogWarning("[Network] 未连接到服务器，尝试重新连接")
        network_client.connect()
        if not network_client.connected:
            ue.LogError("[Network] 无法连接到服务器，登录失败")
            return False
    
    try:
        # 设置登录凭据
        client_entity.username = username
        client_entity.password = password
        
        # 执行登录
        return client_entity.login()
    except Exception as e:
        ue.LogError(f"[Network] 登录时出错: {str(e)}")
        client_entity.login_in_progress = False  # 重置登录状态
        return False

def logout():
	"""登出服务器
	
	Returns:
		bool: 是否成功发送登出请求
	"""
	global client_entity
	
	if not is_network_initialized or not client_entity:
		ue.LogError("[Network] 网络客户端未初始化，无法登出")
		return False
	
	try:
		return client_entity.logout()
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
	global client_entity
	
	if not is_network_initialized or not client_entity:
		ue.LogError("[Network] 网络客户端未初始化，无法保存数据")
		return False
	
	try:
		# 将数据转换为JSON
		data_json = json.dumps(data)
		return client_entity.save_user_data(data_json)
	except Exception as e:
		ue.LogError(f"[Network] 保存用户数据时出错: {str(e)}")
		return False

def load_user_data():
	"""从服务器加载用户数据
	
	Returns:
		bool: 是否成功发送加载请求
	"""
	global client_entity
	
	if not is_network_initialized or not client_entity:
		ue.LogError("[Network] 网络客户端未初始化，无法加载数据")
		return False
	
	try:
		return client_entity.load_user_data()
	except Exception as e:
		ue.LogError(f"[Network] 加载用户数据时出错: {str(e)}")
		return False

def get_user_data():
	"""获取当前客户端的用户数据
	
	Returns:
		dict: 用户数据
	"""
	global client_entity
	
	if not is_network_initialized or not client_entity:
		ue.LogError("[Network] 网络客户端未初始化，无法获取数据")
		return {}
	
	return client_entity.user_data if hasattr(client_entity, 'user_data') else {}

def is_authenticated():
	"""检查用户是否已认证
	
	Returns:
		bool: 是否已认证
	"""
	global client_entity
	
	if not is_network_initialized or not client_entity:
		return False
	
	return client_entity.authenticated if hasattr(client_entity, 'authenticated') else False

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
		global client_entity
		if client_entity:
			client_entity.disconnect()
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
