# -*- encoding: utf-8 -*-
import ue
@ue.uclass(BlueprintType=True)
class MyCharacter(ue.Character):
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
            self._reset_reload_state()

    def _play_reload_animation(self):
        """播放换弹动画（由_reload_weapon调用）"""
        montage_path = "/Game/Mannequin/Animations/My_Reload_Rifle_Hip_Montage.My_Reload_Rifle_Hip_Montage"
        if not self._play_animation_montage(montage_path, self._complete_reload, 1.0, "", "reload"):
            ue.LogError("[动画] 播放换弹动画失败")
            self._reset_reload_state()
    
    def _complete_reload(self, *args):
        """完成换弹操作，更新弹药数量
        
        参数:
            *args: 可变参数列表，用于接收由蒙太奇回调传递的额外参数
        """
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
            self._reset_reload_state()
        
        except Exception as e:
            import traceback
            ue.LogError(f"完成换弹操作时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            self._reset_reload_state()

    def _reset_reload_state(self):
        """重置换弹相关状态"""
        try:
            # 获取换弹状态前的值，用于日志
            prev_reload_state = getattr(self, '_is_reloading', False)
        
            # 安全地重置换弹状态
            self._is_reloading = False
            self.LockOrientation = False
        
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
                    
                    # 彻底清理所有回调
                    self._clean_all_montage_callbacks(anim_instance)
        
            ue.LogWarning(f"[状态] 重置换弹状态: 从 {prev_reload_state} 变为 {self._is_reloading}")
        except Exception as e:
            # 捕获所有可能的异常，确保不会崩溃
            import traceback
            ue.LogError(f"[动画] 重置换弹状态时发生错误: {str(e)}")
            ue.LogError(traceback.format_exc())
        
            # 尝试最基本的重置以防止卡住
            try:
                self._is_reloading = False
                self.LockOrientation = False
            except:
                pass
    
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
            
            # 直接使用动画实例播放蒙太奇
            # try:
            #     montage_play_method = getattr(anim_instance, 'Montage_Play', None)
            #     if montage_play_method:
            #         ue.LogWarning(f"[动画-{tag}] 尝试使用动画实例的Montage_Play方法...")
                    
            #         # 检查是否有其他蒙太奇正在播放
            #         try:
            #             montage_is_playing_method = getattr(anim_instance, 'Montage_IsPlaying', None)
            #             if montage_is_playing_method and anim_instance.Montage_IsPlaying(None):
            #                 try:
            #                     montage_stop_method = getattr(anim_instance, 'Montage_Stop', None)
            #                     if montage_stop_method:
            #                         anim_instance.Montage_Stop(0.25)  # 使用更平滑的混合时间
            #                         ue.LogWarning(f"[动画-{tag}] 停止其他正在播放的蒙太奇，混合时间: 0.25秒")
            #                 except (AttributeError, TypeError):
            #                     pass
            #         except (AttributeError, TypeError):
            #             pass
                    
            #         # 播放蒙太奇并获取持续时间
            #         montage_duration = anim_instance.Montage_Play(montage, play_rate)
                
            #         if montage_duration > 0:
            #             # 如果指定了起始节，跳转到该节
            #             if start_section_name:
            #                 try:
            #                     montage_jump_to_section_method = getattr(anim_instance, 'Montage_JumpToSection', None)
            #                     if montage_jump_to_section_method:
            #                         anim_instance.Montage_JumpToSection(start_section_name, montage)
            #                         ue.LogWarning(f"[动画-{tag}] 跳转到节: {start_section_name}")
            #                 except (AttributeError, TypeError):
            #                     pass
                        
            #             ue.LogWarning(f"[动画-{tag}] 动画蒙太奇播放成功，持续时间: {montage_duration}秒，播放速率: {play_rate}")
                    
            #             # 设置回调
            #             ue.LogWarning(f"[动画-{tag}] 设置动画完成回调...")
            #             self._setup_animation_callbacks(anim_instance, montage, completion_callback, tag)
            #             ue.LogWarning(f"[动画-{tag}] 播放成功，预计持续时间: {montage_duration / play_rate}秒")
            #             return True
            #         else:
            #             ue.LogError(f"[动画-{tag}] 动画蒙太奇播放失败，返回持续时间: {montage_duration}")
            #     else:
            #         ue.LogWarning(f"[动画-{tag}] 动画实例 {anim_instance_class} 不支持 Montage_Play 方法，尝试备用播放方式")
            # except (AttributeError, TypeError):
            #     ue.LogWarning(f"[动画-{tag}] 动画实例不支持Montage_Play方法，尝试备用播放方式")
            
            # 备选方案：尝试在动画实例中查找其他播放方法
            # if anim_instance:
            #     ue.LogWarning(f"[动画-{tag}] 尝试其他播放方法...")
            #     animation_functions = ['PlayAnimMontage', 'PlayAnimation', 'PlayMontage']
                
            #     # 遍历实例的所有方法并打印
            #     try:
            #         dict_attr = getattr(anim_instance, '__dict__', None)
            #         if dict_attr:
            #             methods = [m for m in dir(anim_instance) if m.startswith('Play') and callable(getattr(anim_instance, m))]
            #             ue.LogWarning(f"[动画-{tag}] 可用的播放方法: {methods}")
            #     except (AttributeError, TypeError):
            #         pass
                
            #     for func_name in animation_functions:
            #         try:
            #             func_attr = getattr(anim_instance, func_name, None)
            #             if func_attr:
            #                 try:
            #                     ue.LogWarning(f"[动画-{tag}] 尝试使用动画实例的 {func_name} 方法...")
            #                     result = getattr(anim_instance, func_name)(montage, play_rate)
            #                     ue.LogWarning(f"[动画-{tag}] 通过动画实例的 {func_name} 函数播放蒙太奇，结果: {result}")
                                
            #                     # 设置完成回调
            #                     if completion_callback:
            #                         import threading
            #                         try:
            #                             get_play_length_method = getattr(montage, 'GetPlayLength', None)
            #                             if get_play_length_method:
            #                                 animation_duration = montage.GetPlayLength()
            #                             else:
            #                                 animation_duration = 1.5
            #                         except (AttributeError, TypeError):
            #                             animation_duration = 1.5
                                        
            #                         timer = threading.Timer(animation_duration / play_rate, completion_callback)
            #                         timer.start()
            #                         ue.LogWarning(f"[动画-{tag}] 使用定时器回调，将在{animation_duration / play_rate}秒后调用")
                                    
            #                     ue.LogWarning(f"[动画-{tag}] 播放成功")
            #                     return True
            #                 except Exception as func_ex:
            #                     ue.LogWarning(f"[动画-{tag}] 调用动画实例的 {func_name} 函数失败: {func_ex}")
            #         except (AttributeError, TypeError):
            #             pass
            
            # 最后尝试使用网格体的PlayAnimation
            # try:
            #     play_animation_method = getattr(mesh_to_use, 'PlayAnimation', None)
            #     if play_animation_method:
            #         try:
            #             ue.LogWarning(f"[动画-{tag}] 尝试使用网格体的PlayAnimation方法...")
            #             mesh_to_use.PlayAnimation(montage, False)
            #             ue.LogWarning(f"[动画-{tag}] 使用网格体的PlayAnimation方法播放动画成功")
                        
            #             # 设置定时器回调
            #             if completion_callback:
            #                 import threading
            #                 try:
            #                     get_play_length_method = getattr(montage, 'GetPlayLength', None)
            #                     if get_play_length_method:
            #                         animation_duration = montage.GetPlayLength()
            #                     else:
            #                         animation_duration = 1.5
            #                 except (AttributeError, TypeError):
            #                     animation_duration = 1.5
                                
            #                 timer = threading.Timer(animation_duration / play_rate, completion_callback)
            #                 timer.start()
            #                 ue.LogWarning(f"[动画-{tag}] 使用定时器回调，将在{animation_duration / play_rate}秒后调用")
                        
            #             ue.LogWarning(f"[动画-{tag}] 播放成功")
            #             return True
            #         except Exception as anim_ex:
            #             ue.LogWarning(f"[动画-{tag}] 使用网格体PlayAnimation播放失败: {anim_ex}")
            # except (AttributeError, TypeError):
            #     pass
            
            # 如果所有方法都失败
            ue.LogError(f"[动画-{tag}] 所有播放方法均失败，无法播放蒙太奇")
            return False
                
        except Exception as e:
            import traceback
            ue.LogError(f"[动画-{tag}] 播放动画时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            return False
    
    @classmethod
    def _unreal_skeleton_class(cls):
        # 这里指定我们的Python类要使用的真实蓝图类型
        # 使用与动画蓝图尝试转换到的相同类型
        return '/Game/ThirdPersonCPP/Blueprints/MyCharacterBP.MyCharacterBP_C'
    
    # 添加EndPlay函数清理回调
    @ue.ufunction(override=True)
    def ReceiveEndPlay(self, EndPlayReason):
        try:
            # 获取动画实例
            if self.Mesh:
                anim_instance = self.Mesh.GetAnimInstance()
                if anim_instance:
                    # 使用新的清理函数移除所有回调
                    self._clean_all_montage_callbacks(anim_instance)
                        
            ue.LogWarning('角色退出游戏，已清理所有回调')
        except Exception as e:
            ue.LogError(f'清理角色回调时出错: {str(e)}')
    
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        ue.LogWarning('%s Character ReceiveBeginPlay!' % self)

        # 导入protobuf
        import sys
        sys.path.append("C:\\Users\\wydx\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages")
        
        # 创建战斗数据UI
        self._create_battle_ui()
        
        # 初始化玩家属性和控制器
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
            "LeftMouseButton": [(ue.EInputEvent.IE_Pressed, self._attack_started)]
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

    # 玩家状态
    Died = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    OnHit = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    LockOrientation = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    AttackState = ue.uproperty(bool, BlueprintReadWrite=True, Category="MyCharacter")
    
    # 额外添加几个动画蓝图可能需要的属性
    IsMoving = ue.uproperty(bool, BlueprintReadWrite=True, Category="Animation")
    MoveSpeed = ue.uproperty(float, BlueprintReadWrite=True, Category="Animation")
    IsIdle = ue.uproperty(bool, BlueprintReadWrite=True, Category="Animation")
    
    # 添加显式的getter函数供蓝图使用
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetAttackState(self):
        """获取攻击状态 - 提供一个显式的getter供蓝图使用"""
        return self.AttackState
        
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetDiedState(self):
        """获取死亡状态 - 提供一个显式的getter供蓝图使用"""
        return self.Died
        
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetOnHitState(self):
        """获取受击状态 - 提供一个显式的getter供蓝图使用"""
        return self.OnHit
        
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetIsMoving(self):
        """获取移动状态 - 提供一个显式的getter供蓝图使用"""
        velocity = self.GetVelocity()
        self.IsMoving = velocity.Size() > 10.0  # 如果速度大于10，认为在移动
        return self.IsMoving
        
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetMoveSpeed(self):
        """获取移动速度 - 提供一个显式的getter供蓝图使用"""
        velocity = self.GetVelocity()
        self.MoveSpeed = velocity.Size()
        return self.MoveSpeed
        
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetIsIdle(self):
        """获取待机状态 - 提供一个显式的getter供蓝图使用"""
        self.IsIdle = not self.IsMoving and not self.AttackState and not self.OnHit and not self.Died
        return self.IsIdle

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
    # 发射子弹
    FireBullet = ue.udelegate(BlueprintCallable=True, params=())

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
            
            # 获取玩家控制器和相机方向
            controller = self.GetWorld().GetPlayerController(0)  # 修复：使用GetPlayerController(0)替代GetFirstPlayerController
            if not controller:
                ue.LogError("无法获取玩家控制器")
                return False
                
            # 获取玩家视角方向
            player_view_point = controller.GetPlayerViewPoint()
            if not player_view_point or len(player_view_point) != 2:
                ue.LogError("无法获取玩家视角")
                return False
                
            # 解包视角信息
            camera_location = player_view_point[0]  # 相机位置
            camera_rotation = player_view_point[1]  # 相机旋转
            
            # 计算子弹生成位置 (枪口位置)
            # 尝试从角色网格体获取武器插槽位置
            socket_location = None
            if self.Mesh and hasattr(self.Mesh, "GetSocketLocation"):
                try:
                    socket_location = self.Mesh.GetSocketLocation("WeaponSocket")
                    if socket_location:
                        ue.LogWarning(f"从武器插槽获取发射位置: {socket_location}")
                except Exception as socket_error:
                    ue.LogWarning(f"获取插槽位置失败: {socket_error}，将使用角色位置")
            
            # 如果无法获取插槽位置，使用角色位置加上偏移
            if not socket_location:
                actor_location = self.GetActorLocation()
                forward_vector = ue.KismetMathLibrary.GetForwardVector(self.GetActorRotation())
                offset = ue.KismetMathLibrary.Multiply_VectorFloat(forward_vector, 100.0)  # 前方100单位
                offset.Z += 50.0  # 上方50单位
                spawn_location = ue.KismetMathLibrary.Add_VectorVector(actor_location, offset)
            else:
                spawn_location = socket_location
            
            # 加载子弹蓝图类
            bullet_class = ue.LoadClass("/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterSharpBullet.CharacterSharpBullet_C")
            if not bullet_class:
                ue.LogError("无法加载子弹蓝图类")
                return False
            
            # 计算子弹飞行方向
            target_direction = None
            
            # 首先尝试从鼠标点击位置获取方向
            hit_tuple = controller.GetHitResultUnderCursorByChannel(
                ue.ETraceTypeQuery.TraceTypeQuery1,  # 默认通道
                True  # 复杂碰撞检测
            )
            has_hit = hit_tuple[0]
            hit_result = hit_tuple[1]
            
            if has_hit:
                # 如果射线命中了物体，使用命中点方向
                target_location = hit_result.Location
                target_direction = ue.KismetMathLibrary.GetDirectionUnitVector(
                    spawn_location, 
                    target_location
                )
                ue.LogWarning(f"根据射线命中点设置子弹方向: {target_direction}")
            else:
                # 使用相机前方向作为子弹方向
                target_direction = ue.KismetMathLibrary.GetForwardVector(camera_rotation)
                ue.LogWarning(f"使用相机朝向作为子弹方向: {target_direction}")
            
            # 使用计算的方向设置子弹旋转
            bullet_rotation = ue.KismetMathLibrary.MakeRotFromX(target_direction)
            
            # 生成子弹Actor
            world = self.GetWorld()
            if world:
                try:
                    # 在UE Python绑定中，使用标准的SpawnActor方式
                    bullet = world.SpawnActor(bullet_class, spawn_location, bullet_rotation)
                    if bullet:
                        ue.LogWarning(f"成功生成子弹: {bullet}")
                        
                        # 如果子弹有ProjectileMovement组件，设置初始速度
                        if hasattr(bullet, "ProjectileMovement"):
                            if hasattr(bullet, "InitialSpeed"):
                                bullet.ProjectileMovement.InitialSpeed = bullet.InitialSpeed
                                bullet.ProjectileMovement.MaxSpeed = bullet.InitialSpeed
                                ue.LogWarning(f"设置子弹速度: {bullet.InitialSpeed}")
                            else:
                                # 设置默认速度
                                bullet.ProjectileMovement.InitialSpeed = 3000.0
                                bullet.ProjectileMovement.MaxSpeed = 3000.0
                                ue.LogWarning("设置子弹默认速度: 3000")
                        
                        return True
                    else:
                        ue.LogError("子弹生成失败")
                except Exception as spawn_error:
                    ue.LogError(f"生成子弹时出错: {spawn_error}")
                    return False
            else:
                ue.LogError("无法获取World实例")
                
            return False
        except Exception as e:
            import traceback
            ue.LogError(f"执行发射子弹逻辑时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            return False
    
    @ue.ufunction(BlueprintCallable=True, Category="Combat")
    def _attack_started(self):
        """处理攻击开始事件，对应蓝图中的MyAttack输入动作的Started事件"""
        # 检查是否已经在攻击中，避免重复触发
        if self.AttackState:
            ue.LogWarning("已经在攻击中，忽略新的攻击请求")
            return
        
        # 检查是否正在换弹，如果在换弹过程中则不允许攻击
        if hasattr(self, '_is_reloading') and self._is_reloading:
            ue.LogWarning("正在换弹中，无法攻击")
            return
            
        # 设置攻击状态
        self.AttackState = True
        # 锁定朝向，使角色不会随移动转向
        self.LockOrientation = True
        
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
                    mouse_x = mouse_position[0]
                    mouse_y = mouse_position[1]
                    
                    # 将鼠标屏幕坐标转换为世界空间方向
                    world_direction = controller.DeprojectScreenPositionToWorld(mouse_x, mouse_y)
                    if world_direction and len(world_direction) >= 2:
                        direction = world_direction[1]  # 第二个元素是方向向量
                        
                        # 沿着方向向量延伸一段距离（例如10000单位）作为目标点
                        # 使用向量计算：目标点 = 起点 + 方向 * 距离
                        target_location = ue.KismetMathLibrary.VectorAdd(
                            camera_location,
                            ue.KismetMathLibrary.Multiply_VectorFloat(direction, 10000.0)
                        )
                        ue.LogWarning(f"使用计算的远点作为目标：{target_location}")
                
                # 如果无法通过鼠标获取方向，使用相机前方
                if not target_location:
                    # 获取相机前方向量
                    forward_vector = ue.KismetMathLibrary.GetForwardVector(camera_rotation)
                    
                    # 计算相机前方远处的点
                    target_location = ue.KismetMathLibrary.VectorAdd(
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
            
            ue.LogWarning(f"计算方向向量: {direction_vector}, 目标旋转: {target_rotation}")
            
            # 设置角色朝向
            self.SetActorRotation(target_rotation, False)
            ue.LogWarning(f"设置角色旋转至：{target_rotation}")
            
            # 调用攻击动画播放函数
            self._play_attack_animation()
                
        except Exception as e:
            import traceback
            ue.LogError(f"执行攻击功能时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
            self._reset_attack_state()
    
    def _play_attack_animation(self):
        """播放攻击动画（该方法专门负责动画播放，由_attack_started调用）"""
        montage_path = "/Game/Mannequin/Animations/My_Fire_Rifle_Hip_Montage.My_Fire_Rifle_Hip_Montage"
        
        # 播放前触发发射子弹事件
        if self.WeaopnBulletNumber > 0:
            self.FireBullet.Broadcast()
            ue.LogWarning("[动画] 触发发射子弹事件")
        
        # 播放攻击动画
        if not self._play_animation_montage(montage_path, self._reset_attack_state, 1.0, "", "attack"):
            ue.LogError("[动画] 播放攻击动画失败")
            self._reset_attack_state()
        
    def _setup_animation_callbacks(self, anim_instance, montage, completion_callback, callback_prefix=""):
        """统一的动画回调设置函数，替代多个重复的回调设置函数
        
        Args:
            anim_instance: 动画实例对象
            montage: 播放的动画蒙太奇对象
            completion_callback: 动画完成时调用的回调函数
            callback_prefix: 回调函数和属性名的前缀，用于区分不同类型的动画
        """
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
            # 清理所有可能的回调类型
            callback_types = ["blend_out", "ended", "started"]
            
            # 清理与不同前缀相关的所有回调
            prefixes = ["attack", "reload", ""]  # 包含空字符串以处理没有前缀的情况
            
            # 直接移除所有委托，不依赖于属性检查
            if hasattr(anim_instance, 'OnMontageBlendingOut'):
                anim_instance.OnMontageBlendingOut.Clear()
                
            if hasattr(anim_instance, 'OnMontageEnded'):
                anim_instance.OnMontageEnded.Clear()
                
            if hasattr(anim_instance, 'OnMontageStarted'):
                anim_instance.OnMontageStarted.Clear()
            
            # 清除所有已保存的委托引用
            for prefix in prefixes:
                delegate_prefix = f"_{prefix}_" if prefix else "_"
                for callback_type in callback_types:
                    delegate_name = f"{delegate_prefix}{callback_type}_delegate"
                    if hasattr(self, delegate_name):
                        delattr(self, delegate_name)
            
            ue.LogWarning("[动画清理] 已清理所有蒙太奇回调")
                    
        except Exception as e:
            import traceback
            ue.LogError(f"[动画清理] 清理所有回调时出错: {str(e)}")
            ue.LogError(traceback.format_exc())
    
    def _reset_attack_state(self):
        """重置攻击状态，在攻击动画结束时调用"""
        try:
            # 获取攻击状态前的值，用于日志
            prev_attack_state = self.AttackState
        
            # 安全地重置攻击状态
            self.AttackState = False
            self.LockOrientation = False
        
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
                        
                    # 彻底清理所有回调
                    self._clean_all_montage_callbacks(anim_instance)
        
            ue.LogWarning(f"[状态] 重置攻击状态: 从 {prev_attack_state} 变为 {self.AttackState}")
        except Exception as e:
            # 捕获所有可能的异常，确保不会崩溃
            import traceback
            ue.LogError(f"[动画] 重置攻击状态时发生错误: {str(e)}")
            ue.LogError(traceback.format_exc())
        
            # 尝试最基本的重置以防止卡住
            try:
                self.AttackState = False
                self.LockOrientation = False
            except:
                pass
    
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
        
        # 弹药数初始化
        self.AllBulletNumber = 100
        self.WeaopnBulletNumber = 10
        
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
        ue.LogWarning(f"- 总弹药: {self.AllBulletNumber}")
        ue.LogWarning(f"- 当前弹匣: {self.WeaopnBulletNumber}")
        ue.LogWarning(f"- 击杀敌人数: {self.KilledEnemies}")

    # 移动 - 以相机方向为中心
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
        # self.AddControllerYawInput(value * 45 * ue.GetDeltaTime())
        self.AddControllerYawInput(value * self.MouseSpeed * ue.GetDeltaTime())

    def _look_up(self, value):
        # self.AddControllerPitchInput(value * 45 * ue.GetDeltaTime())
        self.AddControllerPitchInput(value * self.MouseSpeed * ue.GetDeltaTime())

    # 跳跃
    def _jump(self):
        self.Jump()

    @ue.ufunction(override=True)
    def ReceiveTick(self, DeltaSeconds):
        """接收Tick事件，相当于蓝图中的Event Tick节点"""
        # 检查角色是否移动 - 通过判断速度向量是否不为零
        velocity = self.GetVelocity()
        
        # 更新动画相关属性
        speed = velocity.Size()
        self.MoveSpeed = speed
        self.IsMoving = speed > 10.0  # 如果速度大于10，认为在移动
        self.IsIdle = not self.IsMoving and not self.AttackState and not self.OnHit and not self.Died
        
        # 如果速度不为零并且LockOrientation为false，则根据移动方向设置角色旋转
        if velocity != ue.Vector(0, 0, 0) and not self.LockOrientation:
            # 将速度向量转换为旋转值 - 相当于蓝图中的Conv_VectorToRotator节点
            new_rotation = ue.KismetMathLibrary.MakeRotFromX(velocity)
            
            # 设置角色朝向 - 相当于蓝图中的SetActorRotation节点
            self.SetActorRotation(new_rotation, False)

    # 拾取武器
    def pick_up_weapon(self, weapon):
        # type: (ue.Actor) -> None
        attachment_rule = ue.EAttachmentRule.SnapToTarget
        weapon.AttachToComponent(self.Mesh, 'WeaponSocket',
            attachment_rule, attachment_rule, attachment_rule, True)
        
        self.weapon = weapon
    
    # 奔跑功能
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
    
    def _reset_reload_state(self):
        """重置换弹相关状态 - 保持兼容性的包装函数"""
        self._reset_state("reload")
    
    def _reset_attack_state(self, *args):
        """重置攻击相关状态并确保角色回到待机状态 - 保持兼容性的包装函数
        
        参数:
            *args: 可变参数列表，用于接收由蒙太奇回调传递的额外参数
        """
        self._reset_state("attack")