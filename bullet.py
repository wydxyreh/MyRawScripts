# -*- encoding: utf-8 -*-
"""
子弹系统模块 - 定义了各种类型的子弹及其行为
"""
import ue
import traceback

@ue.uclass()
class Mybullet(ue.Actor):
    """子弹基类，定义基本行为和碰撞响应"""
    
    # 存储已伤害的目标，防止重复伤害
    _damaged_actors = None
    
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        """初始化子弹，设置组件和事件响应"""
        ue.LogWarning(f"[{self.__class__.__name__}] 初始化 ID:{self.GetUniqueID()}")
        
        try:
            # 初始化伤害追踪集合
            self._damaged_actors = set()
            
            collision_comp = self.SphereCollision  # type: ue.SphereComponent
            movement_comp = self.ProjectileMovement  # type: ue.ProjectileMovementComponent
            
            if not collision_comp or not movement_comp:
                ue.LogWarning(f"[{self.__class__.__name__}] 警告: 缺少必要组件")
                return
            
            # 设置移动组件的更新组件并禁用重力影响
            movement_comp.SetUpdatedComponent(collision_comp)
            movement_comp.ProjectileGravityScale = 0.0
            
            # 注册事件
            collision_comp.OnComponentHit.Add(self._on_hit)
            collision_comp.OnComponentBeginOverlap.Add(self._on_begin_overlap)
        except Exception as e:
            ue.LogWarning(f"[{self.__class__.__name__}] 初始化时出错: {e}")
            ue.LogWarning(traceback.format_exc())
    
    def _on_hit(self, hit_comp, other_actor, other_comp, normal_impulse, hit):
        # type: (ue.PrimitiveComponent, ue.Actor, ue.PrimitiveComponent, ue.Vector, ue.HitResult) -> None
        """处理子弹与物体的撞击事件"""
        try:
            # 检查组件是否支持物理模拟
            if other_comp and hasattr(other_comp, 'IsSimulatingPhysics') and other_comp.IsSimulatingPhysics():
                # 计算施加的冲量
                impulse_force = self.GetVelocity() * 100
                
                # 添加冲量
                other_comp.AddImpulseAtLocation(impulse_force, self.GetActorLocation())
                
                # 销毁子弹
                self.DestroyActor()
        except Exception as e:
            ue.LogWarning(f"[{self.__class__.__name__}] 处理撞击事件时出错: {e}")
    
    def _on_begin_overlap(self, overlapped_comp, other_actor, other_comp, body_index, from_sweep, sweep_result):
        # type: (ue.PrimitiveComponent, ue.Actor, ue.PrimitiveComponent, int, bool, ue.HitResult) -> None
        """
        当子弹开始与其他物体重叠时被调用
        这个基类方法可以被子类重写以实现不同的行为
        """
        pass
    
    def _destroy_self(self):
        """销毁子弹"""
        try:
            self.DestroyActor()
        except Exception as e:
            ue.LogWarning(f"[{self.__class__.__name__}] 销毁子弹时出错: {e}")
    
    def _apply_damage_and_effect(self, target_actor, damage_amount, sweep_result):
        """对目标应用伤害和特效的通用方法"""
        if not target_actor or target_actor in self._damaged_actors:
            return
        
        self._damaged_actors.add(target_actor)
        
        # 应用伤害
        ue.GameplayStatics.ApplyDamage(
            target_actor,      # 受伤害的Actor
            damage_amount,     # 伤害量
            None,              # 事件发起者
            self.Instigator,   # 伤害来源
            None               # 伤害类型
        )
        
        # 生成打击特效
        hit_location = sweep_result.Location if hasattr(sweep_result, 'Location') else self.GetActorLocation()
        hit_effect = ue.LoadObject(ue.ParticleSystem, '/Game/FXVarietyPack/Particles/P_ky_hit2')
        
        if hit_effect:
            ue.GameplayStatics.SpawnEmitterAtLocation(
                self,
                hit_effect,
                hit_location,
                ue.Rotator(0, 0, 0),
                ue.Vector(1, 1, 1),
                True
            )
        
        # 在播放完特效后立即销毁子弹，不再延迟
        self._destroy_self()

@ue.uclass()
class CharacterBullet(Mybullet):
    """
    角色射出的子弹，击中怪物时造成伤害并击退
    """
    def _on_begin_overlap(self, overlapped_comp, other_actor, other_comp, body_index, from_sweep, sweep_result):
        # type: (ue.PrimitiveComponent, ue.Actor, ue.PrimitiveComponent, int, bool, ue.HitResult) -> None
        """处理角色子弹与其他物体的重叠事件，主要是对怪物造成伤害"""
        try:
            # 尝试将碰撞的对象转换为Monster类型
            monster_class = ue.LoadClass('/Game/ThirdPersonCPP/Blueprints/MyMonsterBP.MyMonsterBP_C')
            
            # 检查other_actor是否是Monster类的实例并且未死亡
            if other_actor and monster_class and other_actor.IsA(monster_class):
                monster_died = getattr(other_actor, 'Died', False)
                
                if not monster_died:
                    monster = other_actor
                    
                    # 对Monster造成伤害和特效
                    self._apply_damage_and_effect(monster, 8.0, sweep_result)
                    
                    # 添加向前的冲击力
                    if hasattr(monster, 'CharacterMovement') and monster.CharacterMovement:
                        impulse_strength = 500
                        forward_vector = self.GetActorForwardVector()
                        monster.CharacterMovement.AddImpulse(forward_vector * impulse_strength)
        except Exception as e:
            ue.LogWarning(f"[CharacterBullet] 处理重叠事件时出错: {e}")
            ue.LogWarning(traceback.format_exc())

@ue.uclass()
class MonsterBullet(Mybullet):
    """
    怪物射出的尖锐子弹，击中角色时造成伤害
    """
    def _on_begin_overlap(self, overlapped_comp, other_actor, other_comp, body_index, from_sweep, sweep_result):
        # type: (ue.PrimitiveComponent, ue.Actor, ue.PrimitiveComponent, int, bool, ue.HitResult) -> None
        """处理怪物尖锐子弹与其他物体的重叠事件，主要是对玩家角色造成伤害"""
        try:
            # 尝试将碰撞的对象转换为角色类型
            character_class = ue.LoadClass('/Game/ThirdPersonCPP/Blueprints/MyCharacterBP.MyCharacterBP_C')
            
            # 检查other_actor是否是MyCharacterBP类的实例
            if other_actor and character_class and other_actor.IsA(character_class):
                character = other_actor
                
                # 使用基类方法对角色造成伤害和特效
                self._apply_damage_and_effect(character, 8.0, sweep_result)
                
                # 添加向后的击退效果，与CharacterBullet类似但方向相反
                if hasattr(character, 'CharacterMovement') and character.CharacterMovement:
                    impulse_strength = 300  # 较小的击退力
                    forward_vector = self.GetActorForwardVector()
                    character.CharacterMovement.AddImpulse(forward_vector * impulse_strength)
                
        except Exception as e:
            ue.LogWarning(f"[MonsterSharpBullet] 处理重叠事件时出错: {e}")
            ue.LogWarning(traceback.format_exc())