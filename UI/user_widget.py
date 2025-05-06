# -*- coding:utf-8 -*-


import ue
import sys
from UI.ui_base import UIBase
from UI.utils import UILibrary


# 为wbp绑定一个默认python类型
class PanelMeta(type):
	def __init__(cls, name, bases, dct):
		if cls.UMG_PATH:
			uclass_path = UILibrary.get_wbp_class_path(cls)
			if uclass_path:  # 允许覆盖原有的配置
				UIBase.BIND_PANEL_WIDGET_UCLASS_DICT[uclass_path] = cls
		super(PanelMeta, cls).__init__(name, bases, dct)

	def __str__(cls):
		return "<class '%s.%s' - '%s'>" % (cls.__module__, cls.__name__, cls.UMG_PATH)

	def __repr__(cls):
		return "<class '%s.%s' - '%s'>" % (cls.__module__, cls.__name__, cls.UMG_PATH)


# UUserWidget的Python层基类
# 可以将UI蓝图中的控件封装成python类型
class PyUserWidget(UIBase):
	__metaclass__ = PanelMeta
	UMG_PATH = ""
	BIND_WIDGET = {}  # 绑定成员控件对应的python类型

	def __init__(self, uobj, *args, **kwargs):
		super(PyUserWidget, self).__init__(uobj)
		if not self.UMG_PATH and type(self) is not PyUserWidget:
			sys.stderr.write("PyUserWidget {} has no name".format(self.__class__))

		if not ue.KismetMathLibrary.ClassIsChildOf(uobj.GetClass(), ue.NePyUserWidget.Class()):
			raise RuntimeError("uobject {}<{}> is not a UNePyUserWidget".format(uobj.GetName(), uobj.GetClass()))

		uobj.SetPythonInstance(self)
		self._native_widget_map = {}
		self.root_widget = None
		self.widget_name = None
		self.bind_widget_map = {}
		self.unbind_widget_map = {}
		self.bind_event_list = {}
		self.anims = {}
		self.uobj.PythonTickForceDisabled = False

	# called from C++
	def destruct(self):
		if not self.init_finish:
			sys.stderr.write("{} [{}] without super init".format(self.__class__.__module__, self.__class__.__name__))

		self.unbind_widget_events()
		for bind_widget in self.bind_widget_map.values():
			# PyUserWidget's destruct will be call by c++
			if isinstance(bind_widget, PyUserWidget):
				continue
			bind_widget.destruct()

		for unbind_widget in self.unbind_widget_map.values():
			unbind_widget.destruct()

		self.bind_widget_map = None
		self.unbind_widget_map = None
		self.root_widget = None
		self._native_widget_map = None
		self.bind_event_list = None
		self.anims = None

		super(PyUserWidget, self).destruct()

	# called from C++
	def construct(self):
		super(PyUserWidget, self).construct()

		self.init_bind_map()
		self.root_widget = self.uobj.GetRootWidget()
		self.add_unbind_widget("root", self.root_widget)
		self._get_animations()

	def init(self, *args, **kwargs):
		super(PyUserWidget, self).init()
		for bind_widget in self.bind_widget_map.values():
			if not bind_widget:
				continue

			# 动态加入的sub_widget已经走过自己的init
			if bind_widget.init_finish:
				continue

			bind_widget.init(*args, **kwargs)

	# 每帧调用的tick函数
	def on_native_tick(self, geometry, delta_time):
		pass

	def __getattr__(self, key):
		widget = self._get_native_widget(key)
		if widget is not None:
			return widget

		return super(PyUserWidget, self).__getattr__(key)

	def init_widget(self, *args, **kwargs):
		self.init(*args, **kwargs)

	# 主动包装一个uwidget
	@classmethod
	def create_umg_py_widget(cls, py_class, uwidget):
		assert issubclass(py_class, PyUserWidget)
		py_widget = py_class(uwidget)
		uwidget.NativeConstruct()
		return py_widget

	def _get_animations(self):
		self.anims = {}
		mate_dict = self.uobj.GetAnimations()
		for key, value in mate_dict.items():
			self.anims[key.lower()] = value

	# 绑定一个UUserWidget对应的python类型
	def _bind_umg_widget(self, ui_name, py_class, uwidget):
		py_widget = self.create_umg_py_widget(py_class, uwidget)
		self.add_bind_widget(ui_name, py_widget)
		return py_widget

	# 动态加入UMG的子面板
	def bind_sub_umg_widget(self, py_widget):
		ui_name = py_widget.GetName().lower()
		self.add_bind_widget(ui_name, py_widget)

	# 进行UI绑定
	def init_bind_map(self):
		self._native_widget_map = {}
		self.uobj.BindWidget(self._native_widget_map)

		# 指定绑定
		for ui_name, py_class in self.__class__.BIND_WIDGET.items():
			ui_name = ui_name.lower()
			uwidget = self._native_widget_map.get(ui_name, None)
			if not uwidget:
				sys.stderr.write("{}:{} can't find child {}".format(
					str(self.__class__.__name__), str(UILibrary.get_umg_path(self.__class__)), ui_name))
				continue

			if issubclass(py_class, PyUserWidget):
				self._bind_umg_widget(ui_name, py_class, uwidget)

			del self._native_widget_map[ui_name]

		# 自动绑定UMG类型
		for ui_name, uwidget in self._native_widget_map.items():
			uclass = uwidget.GetClass()
			uclass_path = uclass.GetPathName()
			if uclass_path in UIBase.BIND_PANEL_WIDGET_UCLASS_DICT:
				py_class = UIBase.wbp_class_to_pyclass(uclass)
				self._bind_umg_widget(ui_name, py_class, uwidget)
			elif uclass.IsChildOf(ue.UserWidget.Class()):
				self._bind_umg_widget(ui_name, PyUserWidget, uwidget)

	def add_bind_widget(self, key, widget):
		widget.set_parent_widget(self)
		self.bind_widget_map[key] = widget
		setattr(self, key, widget)
		return widget

	def add_unbind_widget(self, key, uwidget):
		py_widget = UIBase(uwidget)
		py_widget.set_parent_widget(self)
		self.unbind_widget_map[key] = py_widget
		setattr(self, key, py_widget)
		return py_widget

	# 控件的延迟绑定获取
	def _get_native_widget(self, key):
		ui_name = key.lower()
		if ui_name in self.bind_widget_map:
			return self.bind_widget_map[ui_name]

		if ui_name in self.unbind_widget_map:
			return self.unbind_widget_map[ui_name]

		if self._native_widget_map and ui_name in self._native_widget_map:
			uwidget = self._native_widget_map[ui_name]
			uclass = uwidget.GetClass()
			return self.add_unbind_widget(ui_name, uwidget)

		return None

	# 绑定所有成员控件的事件回调
	def bind_widget_events(self, bind_event_list):
		self.bind_event_list.update(bind_event_list)

		for widget_name_and_event, callback_func in bind_event_list.items():
			widget_name, event_name = widget_name_and_event.split(":", 1)
			sub_widget = getattr(self, widget_name, None)

			if not sub_widget:
				sys.stderr.write("fail to get widget {} in {}".format(widget_name, self.__class__.__name__))
				continue

			if not hasattr(sub_widget, event_name):
				sys.stderr.write("{} has no event named {}".format(sub_widget, event_name))
				continue

			setattr(sub_widget, event_name, callback_func)

	def unbind_widget_events(self):
		for widget_name_and_event in self.bind_event_list.keys():
			widget_name, event_name = widget_name_and_event.split(":", 1)
			sub_widget = getattr(self, widget_name, None)
			if not sub_widget:
				continue

			if not hasattr(sub_widget, event_name):
				continue

			setattr(sub_widget, event_name, None)

		self.bind_event_list.clear()

	def play_animation(self, anim_name, start_at_time=0.0, number_of_loop=1, play_mode=ue.EUMGSequencePlayMode.Forward,
	                   play_back_speed=1.0, is_restore=False):
		if anim_name not in self.anims:
			return
		anim_widget = self.anims[anim_name]
		self.PlayAnimation(anim_widget, start_at_time, number_of_loop, play_mode, play_back_speed, is_restore)

	def is_animation_playing(self, anim_name):
		if anim_name not in self.anims:
			return False
		anim_widget = self.anims[anim_name]

		return self.IsAnimationPlaying(anim_widget)
