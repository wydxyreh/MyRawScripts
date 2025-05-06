# -*- encoding: utf-8 -*-
import ue

@ue.uclass()
class Mybullet(ue.Actor):
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        collision_comp = self.SphereCollision # type: ue.SphereComponent
        movement_comp = self.ProjectileMovement # type: ue.ProjectileMovementComponent
        movement_comp.SetUpdatedComponent(collision_comp)
        
        collision_comp.OnComponentHit.Add(self._on_hit)
    
    def _on_hit(self, hit_comp, other_actor, other_comp, normal_impulse, hit):
        # type: (ue.PrimitiveComponent, ue.Actor, ue.PrimitiveComponent, ue.Vector, ue.HitResult) -> None
        if other_comp.IsSimulatingPhysics():
            other_comp.AddImpulseAtLocation(self.GetVelocity() * 100, self.GetActorLocation())
            self.DestroyActor()