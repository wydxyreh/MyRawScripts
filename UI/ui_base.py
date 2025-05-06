# -*- coding:utf-8 -*-

import ue


# UWidget的Python层封装基类
# UI类型有一个uobj成员变量，保存其对应的C++ UWidget对象
class UIBase(object):
	BIND_PANEL_WIDGET_UCLASS_DICT = {}  # 自动绑定的UUSerWidget

	def __init__(self, uobj):
		self.uobj = uobj
		self._parent = None
		self.init_finish = False

	def __getattr__(self, key):
		if not self.uobj:
			raise AttributeError("%s: widget object already destruct", key)

		if not hasattr(self.uobj, key):
			raise AttributeError("%s uobject without attr:%s" % ((str(self.__class__), key)))

		ret = getattr(self.uobj, key)
		setattr(self, key, ret)
		return ret

	def construct(self):
		"""UI被创建时调用的构造函数，在__init__之后调用"""
		pass

	def destruct(self):
		"""UI被销毁调用的析构函数"""
		# UMGPanelWidget的已经在子类调用过了
		self._parent = None
		self.uobj = None
		self.bound_uobj_events = None

	def init(self, *args, **kwargs):
		"""UI的初始化函数，在construct之后调用"""
		self.init_finish = True

	def get_parent_widget(self):
		return self._parent

	def set_parent_widget(self, parent):
		self._parent = parent

	@staticmethod
	def wbp_class_to_pyclass(uclass):
		return UIBase.BIND_PANEL_WIDGET_UCLASS_DICT.get(uclass.GetPathName())
