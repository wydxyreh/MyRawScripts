# -*- encoding: utf-8 -*-
import ue

@ue.uclass(BlueprintType=True)
class MyMonster(ue.Character):
    # 定义元类，帮助Unreal Engine在蓝图系统中正确识别此类
    @classmethod
    def _unreal_skeleton_class(cls):
        # 指定我们的Python类要使用的真实蓝图类型
        return '/Game/ThirdPersonCPP/Blueprints/MyMonsterBP.MyMonsterBP_C'
    
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        ue.LogWarning('%s Monster ReceiveBeginPlay!' % self)