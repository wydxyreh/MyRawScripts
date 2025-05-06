# -*- encoding: utf-8 -*-
import ue

@ue.uclass()
class MyMonster(ue.Character):
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        ue.LogWarning('%s Monster ReceiveBeginPlay!' % self)