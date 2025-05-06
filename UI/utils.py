# -*- coding: utf-8 -*-

import ue


class UILibrary(object):
	UMG_FILE_UE_PATH = "/Game/UI"

	@staticmethod
	def get_wbp_class(py_class):
		from UI.user_widget import PyUserWidget
		if not issubclass(py_class, PyUserWidget):
			raise RuntimeError('UI class {} is not subclass of PyUserWidget!'.format(py_class))

		umg_class_path = UILibrary.get_umg_path(py_class)
		widget_class = ue.LoadClass(umg_class_path)
		if widget_class and widget_class.IsValid():
			return widget_class
		else:
			raise RuntimeError("Can't load wbp class of class {} at path {}, please check UMG_PATH.".format(
				py_class, umg_class_path))

	@staticmethod
	def get_wbp_class_path(py_class):
		uclass = UILibrary.get_wbp_class(py_class)
		return uclass.GetPathName() if uclass else None

	@staticmethod
	def absolute_to_local(geometry, abs_pos):
		return ue.SlateBlueprintLibrary.AbsoluteToLocal(geometry, abs_pos)

	@staticmethod
	def local_to_absolute(geometry, local_pos):
		return ue.SlateBlueprintLibrary.LocalToAbsolute(geometry, local_pos)

	@staticmethod
	def get_umg_path(py_class):
		widget_full_name = py_class.UMG_PATH
		path_list = widget_full_name.split(".")
		widget_path = UILibrary.UMG_FILE_UE_PATH if len(path_list) == 1 else \
			UILibrary.UMG_FILE_UE_PATH + "/" + "/".join(path_list[0:-1])
		widget_name = path_list[-1]
		umg_class_path = "{0}/{1}.{1}_C".format(widget_path, widget_name)
		return umg_class_path

	@staticmethod
	def create_panel(world, player_controller, py_class, *args, **kwargs):
		# 创建对应的C++ NePyUserWidget对象
		uclass = UILibrary.get_wbp_class(py_class)
		uwidget = ue.WidgetBlueprintLibrary.Create(world, uclass, player_controller)

		# 实例化python对象
		py_widget = py_class(uwidget, *args, **kwargs)
		return py_widget

	@staticmethod
	def create_sub_panel(world, player_controller, py_class, attach_panel, *args, **kwargs):
		py_widget = UILibrary.create_panel(world, player_controller, py_class, *args, **kwargs)
		attach_panel.AddChild(py_widget.uobj)
		user_widget = attach_panel.get_parent_widget()
		assert user_widget
		user_widget.bind_sub_umg_widget(py_widget)

		py_widget.init_widget(*args, **kwargs)
		return py_widget

	# 创建一个UI面板
	@staticmethod
	def create_ui(world, player_controller, parent_canvas, umg_class, *args, **kwargs):
		py_widget = UILibrary.create_panel(world, player_controller, umg_class)
		uwidget = py_widget.uobj

		# 绑定新的界面，下一行会调用 py_widget.construct()
		slot = parent_canvas.AddChildToCanvas(uwidget)
		py_widget.init_widget(*args, **kwargs)

		# UI根据root进行缩放
		anchor = ue.Anchors()  # Anchors只导出了默认构造函数，
		anchor.Maximum = ue.Vector2D(1, 1)  # 所以需要先构造后设置
		slot.SetAnchors(anchor)
		slot.SetOffsets(ue.Margin())
		slot.SetAlignment(ue.Vector2D())

		return py_widget

	# 销毁一个UI面板
	@staticmethod
	def destroy_ui(widget):
		if widget is None:
			return

		if widget.uobj and widget.uobj.IsValid():
			widget.uobj.RemoveFromParent()
