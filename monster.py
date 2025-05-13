# -*- encoding: utf-8 -*-
import ue

@ue.uclass(BlueprintType=True)
class MyMonster(ue.Character):
    # 定义元类，帮助Unreal Engine在蓝图系统中正确识别此类
    @classmethod
    def _unreal_skeleton_class(cls):
        # 指定我们的Python类要使用的真实蓝图类型
        return '/Game/ThirdPersonCPP/Blueprints/MyMonsterBP.MyMonsterBP_C'
    
    # 添加所有可能在动画蓝图中使用的属性
    # 常见的动画属性
    IsAttacking = ue.uproperty(bool, BlueprintReadWrite=True, Category="Animation")
    IsMoving = ue.uproperty(bool, BlueprintReadWrite=True, Category="Animation")
    MoveSpeed = ue.uproperty(float, BlueprintReadWrite=True, Category="Animation")
    IsDead = ue.uproperty(bool, BlueprintReadWrite=True, Category="Animation")
    IsIdle = ue.uproperty(bool, BlueprintReadWrite=True, Category="Animation")
    IsHit = ue.uproperty(bool, BlueprintReadWrite=True, Category="Animation")
    
    # 添加几个动画蒙太奇属性以防万一
    AttackMontage = ue.uproperty(ue.AnimMontage, BlueprintReadWrite=True, Category="Animation")
    HitReactionMontage = ue.uproperty(ue.AnimMontage, BlueprintReadWrite=True, Category="Animation")
    DeathMontage = ue.uproperty(ue.AnimMontage, BlueprintReadWrite=True, Category="Animation")
    
    @ue.ufunction(override=True)
    def ReceiveBeginPlay(self):
        # 初始化动画属性
        self.IsAttacking = False
        self.IsMoving = False
        self.MoveSpeed = 0.0
        self.IsDead = False
        self.IsIdle = True
        self.IsHit = False
        
        # 输出日志
        ue.LogWarning('%s Monster ReceiveBeginPlay!' % self)
        
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetIsAttacking(self):
        """获取攻击状态 - 提供一个显式的getter供蓝图使用"""
        return self.IsAttacking
    
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetIsMoving(self):
        """获取移动状态 - 提供一个显式的getter供蓝图使用"""
        return self.IsMoving
    
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetMoveSpeed(self):
        """获取移动速度 - 提供一个显式的getter供蓝图使用"""
        return self.MoveSpeed
    
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetIsDead(self):
        """获取死亡状态 - 提供一个显式的getter供蓝图使用"""
        return self.IsDead
    
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetIsIdle(self):
        """获取待机状态 - 提供一个显式的getter供蓝图使用"""
        return self.IsIdle
    
    @ue.ufunction(BlueprintCallable=True, Category="Animation")
    def GetIsHit(self):
        """获取受击状态 - 提供一个显式的getter供蓝图使用"""
        return self.IsHit