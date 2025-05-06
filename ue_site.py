# -*- coding: utf-8 -*-

# ThirdPersonWithPy样例入口模块
# 包含了不关编辑器更新脚本逻辑的功能, 我们称之为hot reload(见release_post_game_modules和hold_pre_game_modules_name)


import sys
import ue

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
		pass

def on_shutdown():
	'''此函数会在NEPY插件初始化（ShutdownModule）时调用。可用于进行一些清理工作。'''


def on_post_engine_init():
	'''此函数是可选函数。如果定义了此函数，则会在引擎初始化完毕（OnPostEngineInit）时调用。回调时机晚于on_init'''
	# 为了启动编辑器的时候识别出在Python定义的类(subclassing), 需要在这里import
	# 这里import的类[不会]在每次play时重新加载
	# import Logic.some_subclassing

	import_preload_subclassing()


def on_tick(delta_secodes: float):
    '''此函数是可选函数。如果定义了此函数，则会在每帧Tick的时候调用。'''


def on_debug_input(cmd_str: str) -> bool:
	'''此函数是可选函数。如果定义了此函数，则当用户在PythonConsole中输入指令时，会首先回调到该函数。此函数可用于制作复杂的GM指令逻辑。返回值的含义是用户是否已自行处理了命令，若返回False，则PythonConsole会继续eval用户命令。'''
	import gmcmds
	return gmcmds.handle_debug_input(cmd_str)

# 为了启动编辑器的时候识别出在Python定义的类(subclassing), 需要在这里import
# 这里import的类[会]在每次play时被重新加载
def import_preload_subclassing():
	PyGameInstance.hold_pre_game_modules_name()

	import tp_game_mode

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
