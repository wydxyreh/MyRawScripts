# -*- encoding: utf-8 -*-
import ue

@ue.uclass()
class MyRifle(ue.Actor):
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        pick_up = self.PickUp # type: ue.SphereComponent
        pick_up.OnComponentBeginOverlap.Add(self._on_pick_up)
        
        # 尝试加载子弹类
        self.bullet_class = ue.LoadClass('/Game/ThirdPersonCPP/Blueprints/Bullet/MonsterSharpBullet.MonsterSharpBullet_C')
        
        # 增加错误检查
        if self.bullet_class:
            if hasattr(self.bullet_class, 'OwnByPython'):
                self.bullet_class.OwnByPython()
            ue.LogWarning(f"{self}: 成功加载子弹类: {self.bullet_class}")
        else:
            ue.LogError(f"{self}: 无法加载任何子弹类，射击功能将不可用")

    def _on_pick_up(self, overlapped_comp, other_actor, other_comp, other_body_index, from_sweep, sweepresult):
        # type: (ue.PrimitiveComponent, ue.Actor, ue.PrimitiveComponent, int, bool, ue.HitResult) -> None
        from character import MyCharacter
        if other_actor.IsA(MyCharacter):
            my_character = other_actor # type: MyCharacter
            my_character.pick_up_weapon(self)
    
    def fire(self):
        try:
            mesh = self.RifleMesh # type: ue.SkeletalMeshComponent
            spawn_location = mesh.GetSocketLocation('Muzzle')
            spawn_rotation = mesh.GetSocketRotation('Muzzle')
            
            # 检查必要条件
            if not self.bullet_class:
                ue.LogError(f"{self}: 没有可用的子弹类，无法发射")
                return
                
            # 提前导入Mybullet类以防需要
            from bullet import Mybullet
            
            # 尝试生成子弹
            bullet = self.GetWorld().SpawnActor(self.bullet_class, spawn_location, spawn_rotation)
            if bullet:
                ue.LogWarning(f"成功发射子弹: {bullet}")
            else:
                ue.LogError(f"子弹发射失败")
        except Exception as e:
            ue.LogError(f"发射子弹时出错: {str(e)}")