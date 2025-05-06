# -*- encoding: utf-8 -*-
import ue

@ue.uclass()
class MyRifle(ue.Actor):
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        pick_up = self.PickUp # type: ue.SphereComponent
        pick_up.OnComponentBeginOverlap.Add(self._on_pick_up)
        
        # self.bullet_class = ue.LoadClass('/Game/ThirdPersonCPP/Blueprints/Bullet/MyBulletBP.MyBulletBP_C')
        self.bullet_class = ue.LoadClass('/Game/ThirdPersonCPP/Blueprints/Bullet/SharpBullet.SharpBullet_C')
        self.bullet_class.OwnByPython()

    def _on_pick_up(self, overlapped_comp, other_actor, other_comp, other_body_index, from_sweep, sweepresult):
        # type: (ue.PrimitiveComponent, ue.Actor, ue.PrimitiveComponent, int, bool, ue.HitResult) -> None
        from character import MyCharacter
        if other_actor.IsA(MyCharacter):
            my_character = other_actor # type: MyCharacter
            my_character.pick_up_weapon(self)
    
    def fire(self):
        mesh = self.RifleMesh # type: ue.SkeletalMeshComponent
        spawn_location = mesh.GetSocketLocation('Muzzle')
        spawn_rotation = mesh.GetSocketRotation('Muzzle')
        self.GetWorld().SpawnActor(self.bullet_class, spawn_location, spawn_rotation)