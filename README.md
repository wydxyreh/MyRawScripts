C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\Network\sample_server.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\Network\sample_client.py
阅读并理解这两个文件中客户端与服务端的交互逻辑，服务端继续用sample_server，而客户端我要求改为在：
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\ue_site.py
的init中完成客户端基本的初始化和部署运行，以便后续我的ue项目可以在其他模块随时调用客户端函数与服务端进行通信，比如游戏运行时、游戏结束时等各种场景；
并且以具体代码为例，告诉我应该如何在：
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\ue_site.py
中调用login、logout、save_user_data、load_user_data等函数

分析并解决上述UE游戏运行日志中的错误

1.对于服务端的频率限制，我不希望为登录请求开设特例，我更倾向于在client端降低登录请求频率，比如每3秒内只发送一次，或者是相关处理不要放在tick里；
2.以及对于客户端token的存储，本身在设计时，C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\Network\sample_client.py中的ClientEntity就有相关变量专门用于存储token，结合C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\ue_site.py中定义的global进行处理，而不是本地持久化存储；

首先，C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\ue_site.py是环境中初始化的，并配置了一些全局变量，我希望结合：
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\Network\sample_server.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\Network\sample_client.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\ue_site.py
登录不是全自动登录，而是触发登录，比如我在UE中按下一个按键，然后调用一次登录函数即可，目前只需要给出登录的函数实现即可，登录的调用也只需要在游戏开始的时候自动登录一次即可，并且需要通过ue.Log将登录结果打印到命令行；

检查客户端和服务端有没有哪里存在问题，如果有，则将其修复


根据上述日志，可以看到，客户端在游戏关卡切换的时候，还在尝试登录。从代码里可以看出，用户的登录放在了C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py当中，其实这是不合理的，我更希望登录放在最开始的部分，就是游戏进去的时候，我后续会做一个界面，然后让用户输入账密，然后点击确认后才进行一次登录，并根据登录的结果返回来告诉用户是否通过，如果用户没有通过，则重新输入账密；而当用户退出游戏或者游戏结束，客户端会自动断开连接。
所以目前需要完成的：
1.在C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\ue_site.py的on_post_engine_init中完成客户端初始化，但这里仅仅只是配置客户端的各个参数和启动客户端，暂时不需要和服务端进行连接；而在游戏开始后，客户端才会和服务端进行连接，但也仅仅是尝试连接到服务端，而不是进行登录，同时客户端需要捕获到连接到服务端的结果并ue.log打印出来；登录要放在后续操作中，比如按键触发，同时客户端也要捕获到登录操作的结果并ue.log打印出来；最后登陆后才能进行save和load等操作。
2.C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py中只保留登录的操作，比如按键触发；


我期望的是，客户端配置和启动、客户端连接到服务端，客户端登录到服务端，这是三个不同的步骤，配置和启动在on_post_engine_init中完成，客户端连接到服务端，在游戏启动时完成，客户端登录到服务端则是按键触发，从客户端的运行日志可以看出，游戏开始时，客户端尝试连接到服务端，但是居然提示“[网络] 网络客户端尚未初始化完成，稍后可通过按L键手动登录”，而是在按下L之后，客户端才开始连接然后同时登录，我要求客户端与服务端的连接放在游戏开始时，按下L仅进行登录，如果连接此时已断开，才会重新进行与服务端的连接；
可以考虑将客户端进行登录操作时，将接下来的行为阻塞，然后等到服务端返回的结果，当结果返回时，客户端再继续往后，并且客户端登录的结果也可以在相关函数中通ue.log展示出来。


C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\Network\sample_server.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\Network\sample_client.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\ue_site.py
通过按键实现登录后的save和load，进入游戏、登录成功后，可以按下U和I分别进行save和load操作，并打印出相关信息，包括操作的执行情况和结果，以及操作的数据对象的具体值，比如save操作后，可以打印出保存的数据对象的具体值；
保存的数据为MyCharacter中的变量值，比如AllBulletNumber、WeaopnBulletNumber

结合 C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Plugins\NePythonBinding\Tools\pystubs\ue\__init__.pyi 分析并修复上述问题

C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py
对于换弹，在换弹过程中，播放换弹动画蒙太奇的时候，不允许进行攻击（可扩展）。
同理，对于攻击，播放攻击动画蒙太奇的时候，不允许运行换弹操作（可扩展）；

要求在按住shift加速跑的时候，不允许攻击，但是可以换弹

蓝图资源放在了C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Content\ThirdPersonCPP\Blueprints
动画蓝图资源放在了C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Content\Mannequin\Animations
参考C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Plugins\NePythonBinding\Tools\pystubs\ue\__init__.pyi
要求把现在的播放动画序列改为播放动画蒙太奇：
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Content\Mannequin\Animations\My_Fire_Rifle_Hip_Montage.uasset
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Content\Mannequin\Animations\My_Reload_Rifle_Hip_Montage.uasset
将动画蒙太奇播放的骨骼对象选择为：
Begin Object Class=/Script/Engine.SkeletalMeshComponent Name="CharacterMesh0" ExportPath="/Script/Engine.SkeletalMeshComponent'/Engine/Transient.CharacterMesh0'"
   AnimClass="/Script/Engine.AnimBlueprintGeneratedClass'/Game/ThirdPersonCPP/Blueprints/AnimeBP/MyCharacterAnimBlueprint.MyCharacterAnimBlueprint_C'"
   SkeletalMesh="/Script/Engine.SkeletalMesh'/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin'"
   SkinnedAsset="/Script/Engine.SkeletalMesh'/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin'"
   VisibilityBasedAnimTickOption=AlwaysTickPose
   BodyInstance=(ObjectType=ECC_Pawn,CollisionEnabled=QueryOnly,CollisionProfileName="CharacterMesh",CollisionResponses=(ResponseArray=((Channel="Pawn",Response=ECR_Ignore),(Channel="Visibility",Response=ECR_Ignore),(Channel="Vehicle",Response=ECR_Ignore))))
   RelativeLocation=(X=0.000000,Y=0.000000,Z=-88.000000)
   RelativeRotation=(Pitch=0.000000,Yaw=-90.000000,Roll=0.000000)
End Object

目前C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py代码中存在大量重名函数、一部分被定义了却没被用到、旧的函数，移除这些函数和代码

UE客户端日志：
射线命中目标点：<Vector_NetQuantize {X=710.579 Y=-1074.510 Z=130.239}>
计算方向向量: <Vector {X=0.983 Y=-0.184 Z=0.000}>, 目标旋转: <Rotator {P=0.000000 Y=-10.589309 R=0.000000}>
设置角色旋转至：<Rotator {P=0.000000 Y=-10.589309 R=0.000000}>
发射子弹，剩余弹药: 14
从武器插槽获取发射位置: <Vector {X=-909.893 Y=-744.866 Z=239.414}>
根据射线命中点设置子弹方向: <Vector {X=0.978 Y=-0.199 Z=-0.066}>
成功生成子弹: <CharacterSharpBullet_C 'CharacterSharpBullet_C_15' at 0x0000044943E73200>
设置子弹默认速度: 3000
[动画] 触发发射子弹事件
[动画-attack] 使用网格体播放动画: {'PathName': '/Game/ThirdPersonCPP/Maps/UEDPIE_0_关卡1.关卡1:PersistentLevel.MyCharacterBP_C_0.CharacterMesh0', 'SkeletalMesh': 'SK_Mannequin', 'AnimClass': '/Game/ThirdPersonCPP/Blueprints/AnimeBP/MyCharacterAnimBlueprint.MyCharacterAnimBlueprint_C'}
[动画-attack] 找到动画函数库类: PlayMontageCallbackProxy
[动画-attack] 找到静态方法: CreateProxyObjectForPlayMontage
[动画-attack] 通过静态方法成功播放蒙太奇
已经在攻击中，忽略新的攻击请求
[动画] 停止所有蒙太奇，混合时间: 0.25秒
[状态] 重置攻击状态: 从 True 变为 False
[动画-reload] 使用网格体播放动画: {'PathName': '/Game/ThirdPersonCPP/Maps/UEDPIE_0_关卡1.关卡1:PersistentLevel.MyCharacterBP_C_0.CharacterMesh0', 'SkeletalMesh': 'SK_Mannequin', 'AnimClass': '/Game/ThirdPersonCPP/Blueprints/AnimeBP/MyCharacterAnimBlueprint.MyCharacterAnimBlueprint_C'}
[动画-reload] 找到动画函数库类: PlayMontageCallbackProxy
[动画-reload] 找到静态方法: CreateProxyObjectForPlayMontage
[动画-reload] 通过静态方法成功播放蒙太奇
换弹完成! 当前武器弹药: 30/30, 剩余备用弹药: 84
[动画] 停止所有蒙太奇，混合时间: 0.25秒
[状态] 重置换弹状态: 从 True 变为 False


上述我尝试播放动画蒙太奇，但是我的网格体并没有做出对应动画，我认为是网格体配置有问题，我在蓝图中的网格体为：
Begin Object Class=/Script/Engine.SkeletalMeshComponent Name="CharacterMesh0" ExportPath="/Script/Engine.SkeletalMeshComponent'/Engine/Transient.CharacterMesh0'"
   AnimClass="/Script/Engine.AnimBlueprintGeneratedClass'/Game/ThirdPersonCPP/Blueprints/AnimeBP/MyCharacterAnimBlueprint.MyCharacterAnimBlueprint_C'"
   SkeletalMesh="/Script/Engine.SkeletalMesh'/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin'"
   SkinnedAsset="/Script/Engine.SkeletalMesh'/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin'"
   VisibilityBasedAnimTickOption=AlwaysTickPose
   BodyInstance=(ObjectType=ECC_Pawn,CollisionEnabled=QueryOnly,CollisionProfileName="CharacterMesh",CollisionResponses=(ResponseArray=((Channel="Pawn",Response=ECR_Ignore),(Channel="Visibility",Response=ECR_Ignore),(Channel="Vehicle",Response=ECR_Ignore))))
   RelativeLocation=(X=0.000000,Y=0.000000,Z=-88.000000)
   RelativeRotation=(Pitch=0.000000,Yaw=-90.000000,Roll=0.000000)
End Object

拖拽出来得到：
Begin Object Class=/Script/BlueprintGraph.K2Node_VariableGet Name="K2Node_VariableGet_0" ExportPath="/Script/BlueprintGraph.K2Node_VariableGet'/Game/ThirdPersonCPP/Blueprints/MyCharacterBP.MyCharacterBP:EventGraph.K2Node_VariableGet_0'"
   VariableReference=(MemberName="Mesh",bSelfContext=True)
   NodePosX=288
   NodePosY=1216
   NodeGuid=ED587A7A40FA8B3E778CFB82665AE26C
   CustomProperties Pin (PinId=D00D6A174860DAFE4E999D8B6A6DCF96,PinName="Mesh",PinFriendlyName=NSLOCTEXT("UObjectDisplayNames", "Character:Mesh", "Mesh"),Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.SkeletalMeshComponent'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=True,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=17DDC70943D77A9D7CFB4B97E763C20F,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Character'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object

参考C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Plugins\NePythonBinding\Tools\pystubs\ue\__init__.pyi，修正现在的代码网格体动画蒙太奇播放，从动画蒙太奇播放，直接改为用动画序列播放：
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Content\Mannequin\Animations\My_Fire_Rifle_Hip_Montage.uasset
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Content\Mannequin\Animations\My_Reload_Rifle_Hip_Montage.uasset


结合C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Plugins\NePythonBinding\Tools\pystubs\ue\init.pyi，修正该错误

C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py中的_play_animation_montage中，这部分代码是否有更好的定时器回调处理方式，比如不用threading？


修改C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py中的_play_animation_montage函数，使其使用Character类的PlayAnimMontage方法来播放动画蒙太奇，且要求动画播放的对象为：
蓝图中的网格体为：
Begin Object Class=/Script/Engine.SkeletalMeshComponent Name="CharacterMesh0" ExportPath="/Script/Engine.SkeletalMeshComponent'/Engine/Transient.CharacterMesh0'"
   AnimClass="/Script/Engine.AnimBlueprintGeneratedClass'/Game/ThirdPersonCPP/Blueprints/AnimeBP/MyCharacterAnimBlueprint.MyCharacterAnimBlueprint_C'"
   SkeletalMesh="/Script/Engine.SkeletalMesh'/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin'"
   SkinnedAsset="/Script/Engine.SkeletalMesh'/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin'"
   VisibilityBasedAnimTickOption=AlwaysTickPose
   BodyInstance=(ObjectType=ECC_Pawn,CollisionEnabled=QueryOnly,CollisionProfileName="CharacterMesh",CollisionResponses=(ResponseArray=((Channel="Pawn",Response=ECR_Ignore),(Channel="Visibility",Response=ECR_Ignore),(Channel="Vehicle",Response=ECR_Ignore))))
   RelativeLocation=(X=0.000000,Y=0.000000,Z=-88.000000)
   RelativeRotation=(Pitch=0.000000,Yaw=-90.000000,Roll=0.000000)
End Object

拖拽出来得到：
Begin Object Class=/Script/BlueprintGraph.K2Node_VariableGet Name="K2Node_VariableGet_0" ExportPath="/Script/BlueprintGraph.K2Node_VariableGet'/Game/ThirdPersonCPP/Blueprints/MyCharacterBP.MyCharacterBP:EventGraph.K2Node_VariableGet_0'"
   VariableReference=(MemberName="Mesh",bSelfContext=True)
   NodePosX=288
   NodePosY=1216
   NodeGuid=ED587A7A40FA8B3E778CFB82665AE26C
   CustomProperties Pin (PinId=D00D6A174860DAFE4E999D8B6A6DCF96,PinName="Mesh",PinFriendlyName=NSLOCTEXT("UObjectDisplayNames", "Character:Mesh", "Mesh"),Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.SkeletalMeshComponent'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=True,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=17DDC70943D77A9D7CFB4B97E763C20F,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Character'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
使用的语法严格参考C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Plugins\NePythonBinding\Tools\pystubs\ue\init.pyi，版本为UE5

使用：
OnComponentBeginOverlap: DynamicMulticastDelegateWrapper[typing.Callable[[PrimitiveComponent, Actor, PrimitiveComponent, int, bool, HitResult], None]]
	""" Event called when something starts to overlaps this component, for example a player walking into a trigger.
	For events when objects have a blocking collision, for example a player hitting a wall, see 'Hit' events.

在C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\bullet.py的CharacterBullet中

Begin Object Class=/Script/BlueprintGraph.K2Node_ComponentBoundEvent Name="K2Node_ComponentBoundEvent_0" ExportPath="/Script/BlueprintGraph.K2Node_ComponentBoundEvent'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_ComponentBoundEvent_0'"
   DelegatePropertyName="OnComponentBeginOverlap"
   DelegateOwnerClass="/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'"
   ComponentPropertyName="SphereCollision"
   EventReference=(MemberParent="/Script/CoreUObject.Package'/Script/Engine'",MemberName="ComponentBeginOverlapSignature__DelegateSignature")
   bInternalEvent=True
   CustomFunctionName="BndEvt__SharpBullet_SphereCollision_K2Node_ComponentBoundEvent_0_ComponentBeginOverlapSignature__DelegateSignature"
   NodePosX=-160
   NodePosY=656
   NodeGuid=60491AC94D529A7C3BC540AF8BC2D501
   CustomProperties Pin (PinId=1925C78E485D39330B2F7DA117262082,PinName="OutputDelegate",Direction="EGPD_Output",PinType.PinCategory="delegate",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(MemberParent="/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet_C'",MemberName="BndEvt__SharpBullet_SphereCollision_K2Node_ComponentBoundEvent_0_ComponentBeginOverlapSignature__DelegateSignature"),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=96C564184C2C12905AE07BB147AB6752,PinName="then",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=0A6512BF4B088867CE1317809592290B,PinName="OverlappedComponent",PinToolTip="Overlapped Component\n基元组件 对象引用",Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=78B651704AE1C78E245CC09FB266101A,PinName="OtherActor",PinToolTip="Other Actor\nActor 对象引用",Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Actor'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_DynamicCast_0 7B2C4B7849469966FF5800AC7EDE813B,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=E94D4E2C434B6FFFCBB05C909A4D919A,PinName="OtherComp",PinToolTip="Other Comp\n基元组件 对象引用",Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.PrimitiveComponent'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=324DB6EB4411C757B02C0FA69902CDBB,PinName="OtherBodyIndex",PinToolTip="Other Body Index\n整数",Direction="EGPD_Output",PinType.PinCategory="int",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0",AutogeneratedDefaultValue="0",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=58CEEDA7498E68CB8430BB9E86C5B9C7,PinName="bFromSweep",PinToolTip="From Sweep\n布尔",Direction="EGPD_Output",PinType.PinCategory="bool",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="false",AutogeneratedDefaultValue="false",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=90674F3F4C49F9EDCD43B9975B64AC71,PinName="SweepResult",PinToolTip="Sweep Result\n命中结果 结构（按引用）",Direction="EGPD_Output",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/Engine.HitResult'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=True,PinType.bIsConst=True,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_DynamicCast Name="K2Node_DynamicCast_0" ExportPath="/Script/BlueprintGraph.K2Node_DynamicCast'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_DynamicCast_0'"
   TargetType="/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPersonCPP/Blueprints/MyMonsterBP.MyMonsterBP_C'"
   NodePosX=368
   NodePosY=656
   NodeGuid=A19364874BE8D894BB71F9A6DD52422D
   CustomProperties Pin (PinId=2A63B3384E34DD4602E80395656BA717,PinName="execute",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=44C2F4804FFA3FAE212F1D8A954B32E2,PinName="then",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_MacroInstance_0 4F18329A42934093770DFFA5B5D9C04F,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=3AB23E8C4EEB8CDF20C0B3ADE0AC61E8,PinName="CastFailed",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=7B2C4B7849469966FF5800AC7EDE813B,PinName="Object",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/CoreUObject.Object'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_ComponentBoundEvent_0 78B651704AE1C78E245CC09FB266101A,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=82E1BA774982EAF10F3E47AFB3F7D560,PinName="AsMy Monster BP",Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPersonCPP/Blueprints/MyMonsterBP.MyMonsterBP_C'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_3 05F107CC451BBEE242B1B28DB701D501,K2Node_VariableGet_2 231093D8470C4FA65B9D178750518B3C,K2Node_VariableGet_5 0D73AFFC49D625840CA0D5BBE114626E,K2Node_CallFunction_10 0445435F465F82F5E2719684149C37DB,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=2F890A5D46AB0D2DF619849FFF3599DE,PinName="bSuccess",Direction="EGPD_Output",PinType.PinCategory="bool",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name="K2Node_CallFunction_3" ExportPath="/Script/BlueprintGraph.K2Node_CallFunction'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_CallFunction_3'"
   FunctionReference=(MemberParent="/Script/CoreUObject.Class'/Script/Engine.GameplayStatics'",MemberName="ApplyDamage")
   NodePosX=1040
   NodePosY=656
   NodeGuid=AAEC9BEA4E0DA5EE08348084129EF0AD
   CustomProperties Pin (PinId=280D9ACC4A7827BBEBF88B867EBB4297,PinName="execute",PinToolTip="\n执行",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_MacroInstance_0 9C21032446017C3DD26CA58DE1881857,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=E3135B0041FA02C38B21E2A4C67B6B96,PinName="then",PinToolTip="\n执行",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_4 2CC4F7EF41805DD455C5A6939682951E,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=790B10004291EDC7997BCE99C53F72DD,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinToolTip="目标\nGameplay静态 对象引用",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.GameplayStatics'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultObject="/Script/Engine.Default__GameplayStatics",PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=05F107CC451BBEE242B1B28DB701D501,PinName="DamagedActor",PinToolTip="Damaged Actor\nActor 对象引用\n\n将受到伤害的Actor。",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Actor'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_DynamicCast_0 82E1BA774982EAF10F3E47AFB3F7D560,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=65715EBE4CFC835B40A4BDB4D1C35A3E,PinName="BaseDamage",PinToolTip="Base Damage\n浮点（单精度）\n\n要应用的基础伤害。",PinType.PinCategory="real",PinType.PinSubCategory="float",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="8.000000",AutogeneratedDefaultValue="0.0",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=0C4CA5E749FC0A1BFBD725B6CF46FEFF,PinName="EventInstigator",PinToolTip="Event Instigator\n控制器 对象引用\n\n负责输出此伤害的控制器（例如发射武器的玩家）",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Controller'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=A02BB2D248DB56C4355808A058F5EF51,PinName="DamageCauser",PinToolTip="Damage Causer\nActor 对象引用\n\n实际输出伤害的Actor（例如爆炸的手雷）",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Actor'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_VariableGet_1 2EE249A34F25B425A73E9095BD106E43,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=C298C06E41489B3AB0ADA19BBA5F717F,PinName="DamageTypeClass",PinToolTip="Damage Type Class\n伤害类型 类引用\n\n描述已完成伤害的类。",PinType.PinCategory="class",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.DamageType'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=True,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=27A7AFA04B77B421AD99959B7E670F7C,PinName="ReturnValue",PinToolTip="Return Value\n浮点（单精度）\n\n最终应用到actor的实际伤害。",Direction="EGPD_Output",PinType.PinCategory="real",PinType.PinSubCategory="float",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0.0",AutogeneratedDefaultValue="0.0",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_MacroInstance Name="K2Node_MacroInstance_0" ExportPath="/Script/BlueprintGraph.K2Node_MacroInstance'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_MacroInstance_0'"
   MacroGraphReference=(MacroGraph="/Script/Engine.EdGraph'/Engine/EditorBlueprintResources/StandardMacros.StandardMacros:DoOnce'",GraphBlueprint="/Script/Engine.Blueprint'/Engine/EditorBlueprintResources/StandardMacros.StandardMacros'",GraphGuid=1281F54248A2ECB5B8B2C5B24AE6FDF4)
   NodePosX=768
   NodePosY=576
   NodeGuid=583C41D446DC96B4670491B4FB13846A
   CustomProperties Pin (PinId=4F18329A42934093770DFFA5B5D9C04F,PinName="execute",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_DynamicCast_0 44C2F4804FFA3FAE212F1D8A954B32E2,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=EE47373F4387265AED5716A246A2CDA6,PinName="Reset",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=D988179A4D064A6C3358DAB0D21C0AFE,PinName="Start Closed",PinType.PinCategory="bool",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_VariableGet_2 82260F8D480AED23513220B49EECAF16,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=9C21032446017C3DD26CA58DE1881857,PinName="Completed",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_3 280D9ACC4A7827BBEBF88B867EBB4297,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name="K2Node_CallFunction_4" ExportPath="/Script/BlueprintGraph.K2Node_CallFunction'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_CallFunction_4'"
   FunctionReference=(MemberParent="/Script/CoreUObject.Class'/Script/Engine.GameplayStatics'",MemberName="SpawnEmitterAtLocation")
   NodePosX=1504
   NodePosY=656
   NodeGuid=7D5AFC2F40C8A4CCC84496A699CBA4FC
   CustomProperties Pin (PinId=2CC4F7EF41805DD455C5A6939682951E,PinName="execute",PinToolTip="\n执行",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_3 E3135B0041FA02C38B21E2A4C67B6B96,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=1FA53DF14CE5C549A1BF90B38CFBF5C0,PinName="then",PinToolTip="\n执行",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_ExecutionSequence_0 53B870234A61A9B87D8F1E8583241EBF,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=064D0CCC4EF0D6F5B3EF4E90B975020B,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinToolTip="目标\nGameplay静态 对象引用",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.GameplayStatics'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultObject="/Script/Engine.Default__GameplayStatics",PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=2E98EFE244A7C73CF69CAE95CA29A846,PinName="WorldContextObject",PinToolTip="World Context Object\n对象引用\n\n可获取场景情境的源对象",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/CoreUObject.Object'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=True,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=70E5B4C9464B5FE27C341F84E916A2B3,PinName="EmitterTemplate",PinToolTip="Emitter Template\n粒子系统 对象引用\n\n要创建的粒子系统",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.ParticleSystem'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultObject="/Game/FXVarietyPack/Particles/P_ky_hit2.P_ky_hit2",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=82D2C3F84E4CB36E6D51C1B302ED9B0F,PinName="Location",PinToolTip="Location\n向量\n\n在场景空间中放置效果的位置",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0, 0, 0",AutogeneratedDefaultValue="0, 0, 0",LinkedTo=(K2Node_CallFunction_0 5BFC091748C6F11C681564AD04ACB4FE,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=A561E4274726A70F61B113A896B35942,PinName="Rotation",PinToolTip="Rotation\n旋转体\n\n在场景空间中放置效果的旋转",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0, 0, 0",AutogeneratedDefaultValue="0, 0, 0",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=5258FCAA4412B79338696593E377CC58,PinName="Scale",PinToolTip="Scale\n向量\n\n创建效果的范围",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="1.000000,1.000000,1.000000",AutogeneratedDefaultValue="1.000000,1.000000,1.000000",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=7ADDD41948B5903523AFF08D34420070,PinName="bAutoDestroy",PinToolTip="Auto Destroy\n布尔\n\n粒子系统播放完毕后，组件将自动被销毁，还是可被重新启用",PinType.PinCategory="bool",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="true",AutogeneratedDefaultValue="true",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=B324E9B14F146BED7CC46BA9D25FB975,PinName="PoolingMethod",PinToolTip="Pooling Method\nEPSCPoolMethod枚举值\n\n用于对此组件建池的方法。默认为空。",PinType.PinCategory="byte",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Enum'/Script/Engine.EPSCPoolMethod'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="None",AutogeneratedDefaultValue="None",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=B89B79464A8C2FA22D8DBCB8D4F19740,PinName="bAutoActivateSystem",PinToolTip="Auto Activate System\n布尔",PinType.PinCategory="bool",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="true",AutogeneratedDefaultValue="true",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=ACF25C1848523EECF874248197E90F58,PinName="ReturnValue",PinToolTip="Return Value\nCascade粒子系统组件 对象引用",Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.ParticleSystemComponent'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name="K2Node_CallFunction_6" ExportPath="/Script/BlueprintGraph.K2Node_CallFunction'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_CallFunction_6'"
   FunctionReference=(MemberParent="/Script/CoreUObject.Class'/Script/Engine.KismetSystemLibrary'",MemberName="Delay")
   NodePosX=2592
   NodePosY=672
   NodeGuid=942BDB904A7455469A3D2DB0624C9EF0
   CustomProperties Pin (PinId=A19549B64FCC1BFDB11EB7AC77517B99,PinName="execute",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_ExecutionSequence_0 AA3C945546F65989FEAFA3B7BD3CBFCE,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=DDC13A81462A9700DC96B0A9F52ABF0C,PinName="then",PinFriendlyName="Completed",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_7 683280C243C2D1DCF1AB33B7A26EA7C8,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=55C6E1954AD7B4408929CB86CEE09EFE,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.KismetSystemLibrary'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultObject="/Script/Engine.Default__KismetSystemLibrary",PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=62283C8B423723AA2A906B8957F7F34D,PinName="WorldContextObject",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/CoreUObject.Object'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=True,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=C1C8255A430F809996AE1B80438BE175,PinName="Duration",PinType.PinCategory="real",PinType.PinSubCategory="float",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0.2",AutogeneratedDefaultValue="0.2",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=2A423B7442FAA994C82D8F94EEC4EA48,PinName="LatentInfo",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/Engine.LatentActionInfo'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="(Linkage=-1,UUID=-1,ExecutionFunction=\"\",CallbackTarget=None)",AutogeneratedDefaultValue="LatentInfo",PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name="K2Node_CallFunction_7" ExportPath="/Script/BlueprintGraph.K2Node_CallFunction'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_CallFunction_7'"
   FunctionReference=(MemberName="K2_DestroyActor",bSelfContext=True)
   NodePosX=2864
   NodePosY=656
   NodeGuid=C2FCF4E94BE328FAFB19608203C6FC51
   CustomProperties Pin (PinId=683280C243C2D1DCF1AB33B7A26EA7C8,PinName="execute",PinToolTip="\n执行",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_6 DDC13A81462A9700DC96B0A9F52ABF0C,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=3ECE5DD64893CFFD7D1E92A3F8DEC33A,PinName="then",PinToolTip="\n执行",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=D854C5594F5F6501ADE107A6F5A0053B,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinToolTip="目标\nActor 对象引用",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Actor'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_VariableGet Name="K2Node_VariableGet_2" ExportPath="/Script/BlueprintGraph.K2Node_VariableGet'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_VariableGet_2'"
   VariableReference=(MemberParent="/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPersonCPP/Blueprints/MyMonsterBP.MyMonsterBP_C'",MemberName="Died",MemberGuid=1C242E0B4FABC3D4F19DC790810515A1)
   SelfContextInfo=NotSelfContext
   NodePosX=608
   NodePosY=880
   NodeGuid=D40254FE4E3438433AFCF4B9AEEEA938
   CustomProperties Pin (PinId=82260F8D480AED23513220B49EECAF16,PinName="Died",Direction="EGPD_Output",PinType.PinCategory="bool",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="false",AutogeneratedDefaultValue="false",LinkedTo=(K2Node_MacroInstance_0 D988179A4D064A6C3358DAB0D21C0AFE,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=231093D8470C4FA65B9D178750518B3C,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/Engine.BlueprintGeneratedClass'/Game/ThirdPersonCPP/Blueprints/MyMonsterBP.MyMonsterBP_C'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_DynamicCast_0 82E1BA774982EAF10F3E47AFB3F7D560,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name="K2Node_CallFunction_8" ExportPath="/Script/BlueprintGraph.K2Node_CallFunction'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_CallFunction_8'"
   FunctionReference=(MemberParent="/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'",MemberName="AddImpulse")
   NodePosX=2592
   NodePosY=880
   NodeGuid=D9124E1543DCF2B3D392ECBDA82B1DDF
   CustomProperties Pin (PinId=669E7CEA4DAB10A1B8E6FA836250523B,PinName="execute",PinToolTip="\n执行",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_IfThenElse_0 DB5211384CF2CF34175F1DA32B5DE643,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=060788B14BD0BE853256F9A9225C2836,PinName="then",PinToolTip="\n执行",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=947E9848488F00A51EC80189F5EB87B7,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinToolTip="目标\n角色移动组件 对象引用",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_VariableGet_5 0A6381914979ACDF3FA330989E5F6E7C,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=0738D9AF48982D318C4CB998DA2419A0,PinName="Impulse",PinToolTip="Impulse\n向量\n\n要应用的推动力。",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0, 0, 0",AutogeneratedDefaultValue="0, 0, 0",LinkedTo=(K2Node_PromotableOperator_2 A66A87034594F4B5925109B7E5D21D6F,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=D4EE2AD24A620CD06B02EB9C7954E0FE,PinName="bVelocityChange",PinToolTip="Velocity Change\n布尔\n\n推动力是否相对于质量。",PinType.PinCategory="bool",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="false",AutogeneratedDefaultValue="false",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_VariableGet Name="K2Node_VariableGet_5" ExportPath="/Script/BlueprintGraph.K2Node_VariableGet'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_VariableGet_5'"
   VariableReference=(MemberParent="/Script/CoreUObject.Class'/Script/Engine.Character'",MemberName="CharacterMovement")
   SelfContextInfo=NotSelfContext
   NodePosX=1712
   NodePosY=1280
   NodeGuid=AF228CCC4F90F6870F9EF8BCF01428D8
   CustomProperties Pin (PinId=0A6381914979ACDF3FA330989E5F6E7C,PinName="CharacterMovement",PinFriendlyName=NSLOCTEXT("UObjectDisplayNames", "Character:CharacterMovement", "Character Movement"),Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.CharacterMovementComponent'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=True,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_8 947E9848488F00A51EC80189F5EB87B7,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=0D73AFFC49D625840CA0D5BBE114626E,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Character'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_DynamicCast_0 82E1BA774982EAF10F3E47AFB3F7D560,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_PromotableOperator Name="K2Node_PromotableOperator_2" ExportPath="/Script/BlueprintGraph.K2Node_PromotableOperator'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_PromotableOperator_2'"
   OperationName="Multiply"
   bIsPureFunc=True
   FunctionReference=(MemberParent="/Script/CoreUObject.Class'/Script/Engine.KismetMathLibrary'",MemberName="Multiply_VectorVector")
   NodePosX=2336
   NodePosY=1232
   NodeGuid=E06A6C32429C8D0D9D88D6AE53E732E9
   CustomProperties Pin (PinId=D60C2D934A843D037932E99C446D319E,PinName="A",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_1 B0F88ED441361712ECB0D1B0D0A0BD20,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=3B4C222E4BE050229669C4AD09240842,PinName="B",PinType.PinCategory="int",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="500",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=A66A87034594F4B5925109B7E5D21D6F,PinName="ReturnValue",Direction="EGPD_Output",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_8 0738D9AF48982D318C4CB998DA2419A0,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name="K2Node_CallFunction_10" ExportPath="/Script/BlueprintGraph.K2Node_CallFunction'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_CallFunction_10'"
   bIsPureFunc=True
   FunctionReference=(MemberParent="/Script/CoreUObject.Class'/Script/Engine.KismetSystemLibrary'",MemberName="IsValid")
   NodePosX=1584
   NodePosY=1136
   NodeGuid=6E6A62434D2E731705A6E4BC3143B0C6
   CustomProperties Pin (PinId=7D4A69D64A673F3790260DACCEB49753,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinToolTip="目标\nKismet系统库 对象引用",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.KismetSystemLibrary'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultObject="/Script/Engine.Default__KismetSystemLibrary",PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=0445435F465F82F5E2719684149C37DB,PinName="Object",PinToolTip="Object\n对象引用",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/CoreUObject.Object'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=True,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_DynamicCast_0 82E1BA774982EAF10F3E47AFB3F7D560,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=45CE730C40AA278BF437A2BD75BFC40F,PinName="ReturnValue",PinToolTip="Return Value\n布尔\n\n如对象可用，则返回true：非空，且非待销毁",Direction="EGPD_Output",PinType.PinCategory="bool",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="false",AutogeneratedDefaultValue="false",LinkedTo=(K2Node_IfThenElse_0 04B57FB04A9F72E4787BD3B8CADC576D,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_IfThenElse Name="K2Node_IfThenElse_0" ExportPath="/Script/BlueprintGraph.K2Node_IfThenElse'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_IfThenElse_0'"
   NodePosX=2272
   NodePosY=864
   NodeGuid=4BCB31A040E01012C665DF95F35BA5A2
   CustomProperties Pin (PinId=70B630B94CEAEBE3BACF2A9E89EBCC33,PinName="execute",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_ExecutionSequence_0 15DEE4AB439C3A4E72D0A9A8A9070721,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=04B57FB04A9F72E4787BD3B8CADC576D,PinName="Condition",PinType.PinCategory="bool",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="true",AutogeneratedDefaultValue="true",LinkedTo=(K2Node_CallFunction_10 45CE730C40AA278BF437A2BD75BFC40F,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=DB5211384CF2CF34175F1DA32B5DE643,PinName="then",PinFriendlyName=NSLOCTEXT("K2Node", "true", "true"),Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_8 669E7CEA4DAB10A1B8E6FA836250523B,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=956D959A4F871D5B040035B6A1BAA378,PinName="else",PinFriendlyName=NSLOCTEXT("K2Node", "false", "false"),Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_ExecutionSequence Name="K2Node_ExecutionSequence_0" ExportPath="/Script/BlueprintGraph.K2Node_ExecutionSequence'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_ExecutionSequence_0'"
   NodePosX=1936
   NodePosY=656
   NodeGuid=158702CD4678D8921CDEA69C3668F499
   CustomProperties Pin (PinId=53B870234A61A9B87D8F1E8583241EBF,PinName="execute",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_4 1FA53DF14CE5C549A1BF90B38CFBF5C0,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=AA3C945546F65989FEAFA3B7BD3CBFCE,PinName="then_0",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_6 A19549B64FCC1BFDB11EB7AC77517B99,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=15DEE4AB439C3A4E72D0A9A8A9070721,PinName="then_1",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_IfThenElse_0 70B630B94CEAEBE3BACF2A9E89EBCC33,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_Self Name="K2Node_Self_0" ExportPath="/Script/BlueprintGraph.K2Node_Self'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_Self_0'"
   NodePosX=512
   NodePosY=1232
   NodeGuid=ECAAA92D434477007A20298A2E332737
   CustomProperties Pin (PinId=DC9F7453461690A35FAFA8BA795F9028,PinName="self",Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="self",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_1 BF376D0E492E68246B07EF955C4D5C74,K2Node_CallFunction_0 DC94DB314B58877AD16FC88E1ED72820,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name="K2Node_CallFunction_0" ExportPath="/Script/BlueprintGraph.K2Node_CallFunction'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_CallFunction_0'"
   bIsPureFunc=True
   bIsConstFunc=True
   FunctionReference=(MemberName="K2_GetActorLocation",bSelfContext=True)
   NodePosX=928
   NodePosY=1104
   NodeGuid=F1E9238B48D92C317709FB957BE3A31A
   CustomProperties Pin (PinId=DC94DB314B58877AD16FC88E1ED72820,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinToolTip="目标\nActor 对象引用",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Actor'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_Self_0 DC9F7453461690A35FAFA8BA795F9028,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=5BFC091748C6F11C681564AD04ACB4FE,PinName="ReturnValue",PinToolTip="Return Value\n向量\n\n返回此Actor的RootComponent的位置",Direction="EGPD_Output",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0, 0, 0",AutogeneratedDefaultValue="0, 0, 0",LinkedTo=(K2Node_CallFunction_4 82D2C3F84E4CB36E6D51C1B302ED9B0F,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_VariableGet Name="K2Node_VariableGet_1" ExportPath="/Script/BlueprintGraph.K2Node_VariableGet'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_VariableGet_1'"
   VariableReference=(MemberName="Instigator",bSelfContext=True)
   NodePosX=720
   NodePosY=992
   NodeGuid=355D7BC54E5A2A2C785420ABA6230C89
   CustomProperties Pin (PinId=2EE249A34F25B425A73E9095BD106E43,PinName="Instigator",PinFriendlyName="Instigator",Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Pawn'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=True,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_CallFunction_3 A02BB2D248DB56C4355808A058F5EF51,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=C0CA737F422FB4189F3DD0B428B1814C,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Actor'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/BlueprintGraph.K2Node_CallFunction Name="K2Node_CallFunction_1" ExportPath="/Script/BlueprintGraph.K2Node_CallFunction'/Game/ThirdPersonCPP/Blueprints/Bullet/CharacterBullet.CharacterBullet:EventGraph.K2Node_CallFunction_1'"
   bIsPureFunc=True
   bIsConstFunc=True
   FunctionReference=(MemberName="GetActorForwardVector",bSelfContext=True)
   NodePosX=1728
   NodePosY=1392
   NodeGuid=28B909054DB0ED0E428966A1B671DBE9
   CustomProperties Pin (PinId=BF376D0E492E68246B07EF955C4D5C74,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Actor'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_Self_0 DC9F7453461690A35FAFA8BA795F9028,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=B0F88ED441361712ECB0D1B0D0A0BD20,PinName="ReturnValue",Direction="EGPD_Output",PinType.PinCategory="struct",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0, 0, 0",AutogeneratedDefaultValue="0, 0, 0",LinkedTo=(K2Node_PromotableOperator_2 D60C2D934A843D037932E99C446D319E,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object


对于MyCharacter中的网格体的动画设置，结合C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Plugins\NePythonBinding\Tools\pystubs\ue\__init__.pyi，可以看到:
class SkeletalMeshComponent(SkinnedMeshComponent):
	""" SkeletalMeshComponent is used to create an instance of an animated SkeletalMesh asset.

	See: https://docs.unrealengine.com/latest/INT/Engine/Content/Types/SkeletalMeshes/
	See: USkeletalMesh
	"""  # noqa

	@property
	def AnimBlueprintGeneratedClass(self) -> Class:
		""" Anim Blueprint Generated Class """  # noqa
		pass

	@property
	def AnimClass(self) -> Class:
		""" The AnimBlueprint class to use. Use 'SetAnimInstanceClass' to change at runtime. """  # noqa
		pass
在C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py初始化的时候，配置动画蓝图为：C:/Users/wydx/Documents/Unreal Projects/ThirdPersonWithPy/Content/ThirdPersonCPP/Blueprints/AnimeBP/MyCharacterAnimBlueprint.uasset




class UserWidget(Widget):
	""" The user widget is extensible by users through the WidgetBlueprint. """  # noqa

	@property
	def ColorAndOpacity(self) -> LinearColor:
		""" The color and opacity of this widget.  Tints all child widgets. """  # noqa
		pass

	ColorAndOpacityDelegate: DynamicDelegateWrapper[typing.Callable[[], LinearColor]]
	""" Color and Opacity Delegate """  # noqa

	@property
	def ForegroundColor(self) -> SlateColor:
		""" The foreground color of the widget, this is inherited by sub widgets.  Any color property
		that is marked as inherit will use this color.
		"""  # noqa
		pass

	ForegroundColorDelegate: DynamicDelegateWrapper[typing.Callable[[], SlateColor]]
	""" Foreground Color Delegate """  # noqa

	OnVisibilityChanged: DynamicMulticastDelegateWrapper[typing.Callable[[int], None]]
	""" Called when the visibility has changed """  # noqa

	@property
	def Padding(self) -> Margin:
		""" The padding area around the content. """  # noqa
		pass

	ActiveSequencePlayers: ArrayWrapper[UMGSequencePlayer]
	""" All the sequence players currently playing """  # noqa

	AnimationTickManager: UMGSequenceTickManager
	""" Animation Tick Manager """  # noqa

	StoppedSequencePlayers: ArrayWrapper[UMGSequencePlayer]
	""" List of sequence players to cache and clean up when safe """  # noqa

	NamedSlotBindings: ArrayWrapper[NamedSlotBinding]
	""" Stores the widgets being assigned to named slots """  # noqa

	WidgetTree: WidgetTree
	""" The widget tree contained inside this user widget initialized by the blueprint """  # noqa

	DesignTimeSize: Vector2D
	""" Stores the design time desired size of the user widget """  # noqa

	DesignSizeMode: int
	""" Design Size Mode """  # noqa

	PaletteCategory: str
	""" The category this widget appears in the palette. """  # noqa

	PreviewBackground: Texture2D
	""" A preview background that you can use when designing the UI to get a sense of scale on the screen.  Use
	a texture with a screenshot of your game in it, for example if you were designing a HUD.
	"""  # noqa

	@property
	def Priority(self) -> int:
		""" Priority """  # noqa
		pass

	bIsFocusable: bool
	""" Setting this flag to true, allows this widget to accept focus when clicked, or when navigated to. """  # noqa

	bStopAction: bool
	""" Stop Action """  # noqa

	bHasScriptImplementedTick: bool
	""" If a widget has an implemented tick blueprint function """  # noqa

	bHasScriptImplementedPaint: bool
	""" If a widget has an implemented paint blueprint function """  # noqa

	@property
	def TickFrequency(self) -> int:
		""" This widget is allowed to tick. If this is unchecked tick will never be called, animations will not play correctly, and latent actions will not execute.
		Uncheck this for performance reasons only
		"""  # noqa
		pass

	InputComponent: InputComponent
	""" Input Component """  # noqa

	AnimationCallbacks: ArrayWrapper[AnimationEventBinding]
	""" Animation Callbacks """  # noqa

	def SetInputActionBlocking(self, bShouldBlock: bool):
		""" Set Input Action Blocking """  # noqa
		pass

	def SetInputActionPriority(self, NewPriority: int):
		""" Set Input Action Priority """  # noqa
		pass

	def IsListeningForInputAction(self, ActionName: str) -> bool:
		""" Checks if the action has a registered callback with the input component. """  # noqa
		pass

	def UnregisterInputComponent(self):
		""" StopListeningForAllInputActions will automatically Register an Input Component with the player input system.
		If you however, want to Pause and Resume, listening for a set of actions, the best way is to use
		UnregisterInputComponent to pause, and RegisterInputComponent to resume listening.
		"""  # noqa
		pass

	def RegisterInputComponent(self):
		""" ListenForInputAction will automatically Register an Input Component with the player input system.
		If you however, want to Pause and Resume, listening for a set of actions, the best way is to use
		UnregisterInputComponent to pause, and RegisterInputComponent to resume listening.
		"""  # noqa
		pass

	def StopListeningForAllInputActions(self):
		""" Stops listening to all input actions, and unregisters the input component with the player controller. """  # noqa
		pass

	def StopListeningForInputAction(self, ActionName: str, EventType: int):
		""" Removes the binding for a particular action's callback. """  # noqa
		pass

	def ListenForInputAction(self, ActionName: str, EventType: int, bConsume: bool, Callback: typing.Callable[[], None]):
		""" Listens for a particular Player Input Action by name.  This requires that those actions are being executed, and
		that we're not currently in UI-Only Input Mode.
		"""  # noqa
		pass

	def IsPlayingAnimation(self) -> bool:
		""" Are we currently playing any animations? """  # noqa
		pass

	def FlushAnimations(self):
		""" Flushes all animations on all widgets to guarantee that any queued updates are processed before this call returns """  # noqa
		pass

	def IsAnimationPlayingForward(self, InAnimation: WidgetAnimation) -> bool:
		""" returns true if the animation is currently playing forward, false otherwise.

		@param InAnimation The playing animation that we want to know about
		"""  # noqa
		pass

	def ReverseAnimation(self, InAnimation: WidgetAnimation):
		""" If an animation is playing, this function will reverse the playback.

		@param InAnimation The playing animation that we want to reverse
		"""  # noqa
		pass

	def SetPlaybackSpeed(self, InAnimation: WidgetAnimation, PlaybackSpeed: float = ...):
		""" Changes the playback rate of a playing animation

		@param InAnimation The animation that is already playing
		@param PlaybackRate Playback rate multiplier (1 is default)
		"""  # noqa
		pass

	def SetNumLoopsToPlay(self, InAnimation: WidgetAnimation, NumLoopsToPlay: int):
		""" Changes the number of loops to play given a playing animation

		@param InAnimation The animation that is already playing
		@param NumLoopsToPlay The number of loops to play. (0 to loop indefinitely)
		"""  # noqa
		pass

	def IsAnyAnimationPlaying(self) -> bool:
		""" @return True if any animation is currently playing """  # noqa
		pass

	def IsAnimationPlaying(self, InAnimation: WidgetAnimation) -> bool:
		""" Gets whether an animation is currently playing on this widget.

		@param InAnimation The animation to check the playback status of
		@return True if the animation is currently playing
		"""  # noqa
		pass

	def SetAnimationCurrentTime(self, InAnimation: WidgetAnimation, InTime: float):
		""" Sets the current time of the animation in this widget. Does not change state.

		@param The name of the animation to get the current time for
		@param The current time of the animation.
		"""  # noqa
		pass

	def GetAnimationCurrentTime(self, InAnimation: WidgetAnimation) -> float:
		""" Gets the current time of the animation in this widget

		@param The name of the animation to get the current time for
		@return the current time of the animation.
		"""  # noqa
		pass

	def PauseAnimation(self, InAnimation: WidgetAnimation) -> float:
		""" Pauses an already running animation in this widget

		@param The name of the animation to pause
		@return the time point the animation was at when it was paused, relative to its start position.  Use this as the StartAtTime when you trigger PlayAnimation.
		"""  # noqa
		pass

	def StopAllAnimations(self):
		""" Stop All actively running animations.

		@param The name of the animation to stop
		"""  # noqa
		pass

	def StopAnimation(self, InAnimation: WidgetAnimation):
		""" Stops an already running animation in this widget

		@param The name of the animation to stop
		"""  # noqa
		pass

	def PlayAnimationReverse(self, InAnimation: WidgetAnimation, PlaybackSpeed: float = ..., bRestoreState: bool = ...) -> UMGSequencePlayer:
		""" Plays an animation on this widget relative to it's current state in reverse.  You should use this version in situations where
		say a user can click a button and that causes a panel to slide out, and you want to reverse that same animation to begin sliding
		in the opposite direction.

		@param InAnimation The animation to play
		@param PlayMode Specifies the playback mode
		@param PlaybackSpeed The speed at which the animation should play
		@param bRestoreState Restores widgets to their pre-animated state when the animation stops
		"""  # noqa
		pass

	def PlayAnimationForward(self, InAnimation: WidgetAnimation, PlaybackSpeed: float = ..., bRestoreState: bool = ...) -> UMGSequencePlayer:
		""" Plays an animation on this widget relative to it's current state forward.  You should use this version in situations where
		say a user can click a button and that causes a panel to slide out, and you want to reverse that same animation to begin sliding
		in the opposite direction.

		@param InAnimation The animation to play
		@param PlayMode Specifies the playback mode
		@param PlaybackSpeed The speed at which the animation should play
		@param bRestoreState Restores widgets to their pre-animated state when the animation stops
		"""  # noqa
		pass

	def PlayAnimationTimeRange(self, InAnimation: WidgetAnimation, StartAtTime: float = ..., EndAtTime: float = ..., NumLoopsToPlay: int = ..., PlayMode: int = ..., PlaybackSpeed: float = ..., bRestoreState: bool = ...) -> UMGSequencePlayer:
		""" Plays an animation in this widget a specified number of times stopping at a specified time

		@param InAnimation The animation to play
		@param StartAtTime The time in the animation from which to start playing, relative to the start position. For looped animations, this will only affect the first playback of the animation.
		@param EndAtTime The absolute time in the animation where to stop, this is only considered in the last loop.
		@param NumLoopsToPlay The number of times to loop this animation (0 to loop indefinitely)
		@param PlayMode Specifies the playback mode
		@param PlaybackSpeed The speed at which the animation should play
		@param bRestoreState Restores widgets to their pre-animated state when the animation stops
		"""  # noqa
		pass

	def PlayAnimation(self, InAnimation: WidgetAnimation, StartAtTime: float = ..., NumLoopsToPlay: int = ..., PlayMode: int = ..., PlaybackSpeed: float = ..., bRestoreState: bool = ...) -> UMGSequencePlayer:
		""" Plays an animation in this widget a specified number of times

		@param InAnimation The animation to play
		@param StartAtTime The time in the animation from which to start playing, relative to the start position. For looped animations, this will only affect the first playback of the animation.
		@param NumLoopsToPlay The number of times to loop this animation (0 to loop indefinitely)
		@param PlaybackSpeed The speed at which the animation should play
		@param PlayMode Specifies the playback mode
		@param bRestoreState Restores widgets to their pre-animated state when the animation stops
		"""  # noqa
		pass

	def SetPadding(self, InPadding: Margin):
		""" Sets the padding for the user widget, putting a larger gap between the widget border and it's root widget. """  # noqa
		pass

	def SetForegroundColor(self, InForegroundColor: SlateColor):
		""" Sets the foreground color of the widget, this is inherited by sub widgets.  Any color property
		that is marked as inherit will use this color.

		@param InForegroundColor     The foreground color.
		"""  # noqa
		pass

	def SetColorAndOpacity(self, InColorAndOpacity: LinearColor):
		""" Sets the tint of the widget, this affects all child widgets.

		@param InColorAndOpacity     The tint to apply to all child widgets.
		"""  # noqa
		pass

	def OnAnimationFinished(self, Animation: WidgetAnimation):
		""" Called when an animation has either played all the way through or is stopped

		@param Animation The animation that has finished playing
		"""  # noqa
		pass

	def OnAnimationStarted(self, Animation: WidgetAnimation):
		""" Called when an animation is started.

		@param Animation the animation that started
		"""  # noqa
		pass

	def BindToAnimationEvent(self, Animation: WidgetAnimation, Delegate: typing.Callable[[], None], AnimationEvent: int, UserTag: str = ...):
		""" Allows binding to a specific animation's event.
		@param Animation the animation to listen for starting or finishing.
		@param Delegate the delegate to call when the animation's state changes
		@param AnimationEvent the event to watch for.
		@param UserTag Scopes the delegate to only be called when the animation completes with a specific tag set on it when it was played.
		"""  # noqa
		pass

	def UnbindAllFromAnimationFinished(self, Animation: WidgetAnimation):
		""" Unbind All from Animation Finished """  # noqa
		pass

	def UnbindFromAnimationFinished(self, Animation: WidgetAnimation, Delegate: typing.Callable[[], None]):
		""" Unbind an animation finished delegate.
		@param Animation the animation to listen for starting or finishing.
		@param Delegate the delegate to call when the animation's state changes
		"""  # noqa
		pass

	def BindToAnimationFinished(self, Animation: WidgetAnimation, Delegate: typing.Callable[[], None]):
		""" Bind an animation finished delegate.
		@param Animation the animation to listen for starting or finishing.
		@param Delegate the delegate to call when the animation's state changes
		"""  # noqa
		pass

	def UnbindAllFromAnimationStarted(self, Animation: WidgetAnimation):
		""" Unbind All from Animation Started """  # noqa
		pass

	def UnbindFromAnimationStarted(self, Animation: WidgetAnimation, Delegate: typing.Callable[[], None]):
		""" Unbind an animation started delegate.
		@param Animation the animation to listen for starting or finishing.
		@param Delegate the delegate to call when the animation's state changes
		"""  # noqa
		pass

	def BindToAnimationStarted(self, Animation: WidgetAnimation, Delegate: typing.Callable[[], None]):
		""" Bind an animation started delegate.
		@param Animation the animation to listen for starting or finishing.
		@param Delegate the delegate to call when the animation's state changes
		"""  # noqa
		pass

	def StopAnimationsAndLatentActions(self):
		""" Cancels any pending Delays or timer callbacks for this widget, and stops all active animations on the widget. """  # noqa
		pass

	def CancelLatentActions(self):
		""" Cancels any pending Delays or timer callbacks for this widget. """  # noqa
		pass

	def GetOwningPlayerCameraManager(self) -> PlayerCameraManager:
		""" Gets the player camera manager associated with this UI.
		@return Gets the owning player camera manager that's owned by the player controller assigned to this widget.
		"""  # noqa
		pass

	def GetOwningPlayerPawn(self) -> Pawn:
		""" Gets the player pawn associated with this UI.
		@return Gets the owning player pawn that's owned by the player controller assigned to this widget.
		"""  # noqa
		pass

	def SetOwningPlayer(self, LocalPlayerController: PlayerController):
		""" Sets the local player associated with this UI via PlayerController reference.
		@param LocalPlayerController The PlayerController of the local player you want to be the conceptual owner of this UI.
		"""  # noqa
		pass

	def IsInViewport(self) -> bool:
		""" @return true if the widget was added to the viewport using AddToViewport. """  # noqa
		pass

	def GetAlignmentInViewport(self) -> Vector2D:
		""" Get Alignment in Viewport """  # noqa
		pass

	def GetAnchorsInViewport(self) -> Anchors:
		""" Get Anchors in Viewport """  # noqa
		pass

	def SetAlignmentInViewport(self, Alignment: Vector2D):
		""" Set Alignment in Viewport """  # noqa
		pass

	def SetAnchorsInViewport(self, Anchors: Anchors):
		""" Set Anchors in Viewport """  # noqa
		pass

	def SetDesiredSizeInViewport(self, Size: Vector2D):
		""" Set Desired Size in Viewport """  # noqa
		pass

	def SetPositionInViewport(self, Position: Vector2D, bRemoveDPIScale: bool = ...):
		""" Sets the widgets position in the viewport.
		@param Position The 2D position to set the widget to in the viewport.
		@param bRemoveDPIScale If you've already calculated inverse DPI, set this to false.
		Otherwise inverse DPI is applied to the position so that when the location is scaled
		by DPI, it ends up in the expected position.
		"""  # noqa
		pass

	def AddToPlayerScreen(self, ZOrder: int = ...) -> bool:
		""" Adds the widget to the game's viewport in a section dedicated to the player.  This is valuable in a split screen
		game where you need to only show a widget over a player's portion of the viewport.

		@param ZOrder The higher the number, the more on top this widget will be.
		"""  # noqa
		pass

	def AddToViewport(self, ZOrder: int = ...):
		""" Adds it to the game's viewport and fills the entire screen, unless SetDesiredSizeInViewport is called
		to explicitly set the size.

		@param ZOrder The higher the number, the more on top this widget will be.
		"""  # noqa
		pass

	def SetPythonInstance(self, PythonInstance: object) -> None:
		pass

	def NativeConstruct(self) -> None:
		pass

	def GetWidgetFromName(self, WidgetName: str) -> Widget:
		pass

	def GetAllWidget(self) -> typing.Tuple[Widget]:
		pass

	def GetRootWidget(self) -> Widget:
		pass

	pass

class NePyUserWidget(UserWidget):
	""" Ne Py User Widget """  # noqa

	PythonTickForceDisabled: bool
	""" Python Tick Force Disabled """  # noqa

	PythonPaintForceDisabled: bool
	""" Python Paint Force Disabled """  # noqa

	NativeWidgetHost: NativeWidgetHost
	""" Native Widget Host """  # noqa

	def CallPythonUserWidgetMethod(self, InMethodName: str, InArgs: str):
		""" Call Python User Widget Method """  # noqa
		pass

	def GetPyProxy(self) -> object:
		pass

	def BindWidget(self, WidgetMap: dict) -> None:
		pass

	def GetAnimations(self) -> dict:
		pass

	pass

C:/Users/wydx/Documents/Unreal Projects/ThirdPersonWithPy/Content/Sounds/S_WEP_Fire_08.uasset

C:/Users/wydx/Documents/Unreal Projects/ThirdPersonWithPy/Content/Sounds/S_WEP_Rifle_Reload.uasset

C:/Users/wydx/Documents/Unreal Projects/ThirdPersonWithPy/Content/Sounds/Borislav_Slavov_-_Song_Of_Balduran.uasset

对于C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py，在玩家LeftMouseButton按下时，做成两种模式，默认时点射，即每点一下鼠标左键，发射一次子弹，按下T键切换为连射，即按下鼠标左键，就连续发射30发子弹，一直发射直到弹匣打空或左键松开。连射模式下，连续发射时，只重复音效和子弹生成，动画蒙太奇的播放，只在发射结束时才会播放一次，基于tick实现，MyCharacterTick函数中的内容即为tick事件执行的内容

在C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py中，攻击时，无论是点射还是连射，攻击时，角色转向和攻击方向都要立刻转向鼠标的方位

移动、跑步时，不允许攻击，但是可以换弹

对C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py中，_load_game_data函数调用时，不是_save_game_data

检查核实：
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\ue_site.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\Network\sample_server.py
C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\Network\sample_client.py
在游戏json数据save、load时，函数调用和数据传递关系，修复其中存在的问题，以及去除其中的冗杂处理

在C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py中，提供一个函数，对于来自服务端的broadcast_achievement函数-客户端的achievement_broadcast函数进行对接，能够获取到
ClientEntity.achievement_broadcast_received = False  # 标志位：是否接收到成就广播
ClientEntity.last_achievement_broadcast = None  # 最近接收到的成就广播内容
这两个参数（合理利用get_recent_achievement_broadcast函数），能够使得用户可以在接收到来自服务端的广播后，在游戏中将广播内容显示到游戏UI界面中，并持续3S


参考下述代码，优化C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\RawScripts\character.py中对角色网格体的初始化函数

class PyTPCharacter(ue.FindClass("Character")):

	def __init__(self):
		# 设置胶囊体组件的尺寸（胶囊体用于碰撞）
		capsule_comp = self.CapsuleComponent
		capsule_comp.CapsuleRadius = 42.0
		capsule_comp.CapsuleHalfHeight = 96.0

		# 此类自己拥有的属性为小写+下划线
		self.base_turn_rate = 45.0
		self.base_lookup_rate = 45.0

		# 不使用Controller的旋转
		self.bUseControllerRotationPitch = False
		self.bUseControllerRotationYaw = False
		self.bUseControllerRotationRoll = False

		# 设置移动组件的属性
		char_move_comp = self.CharacterMovement
		# 始终朝向自己移动的方向
		char_move_comp.bOrientRotationToMovement = True
		char_move_comp.RotationRate = ue.Rotator(0.0, 540.0, 0.0)
		char_move_comp.JumpZVelocity = 600.0
		char_move_comp.AirControl = 0.2

		# 注意！！
		# AddActorComponent 里自带ReigsterComponent等需要操作
		# 它的调用时机是在ReceiveBeginPlay里，若放到__init__会有异常
		# 如果增加Component想放到__init__里，应该使用 CreateDefaultSubobject
		self.camera_boom = self.CreateDefaultSubobject(ue.SpringArmComponent.Class(), "CameraBoom")
		self.camera_boom.SetupAttachment(self.RootComponent)
		self.camera_boom.TargetArmLength = 300.0
		self.camera_boom.bUsePawnControlRotation = True

		self.follow_camera = self.CreateDefaultSubobject(ue.CameraComponent.Class(), "FollowCamera")
		self.follow_camera.SetupAttachment(self.camera_boom, 'SpringEndpoint')
		self.follow_camera.bUsePawnControlRotation = False

		# 设置Mesh资源
		self.Mesh.SetSkeletalMesh(ue.LoadObject(ue.SkeletalMesh.Class(), '/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin'))

		# 资源匹配胶囊体大小，适配朝向
		self.Mesh.SetRelativeLocation(ue.Vector(0.0, 0.0, -97.0))
		self.Mesh.SetRelativeRotation(ue.Rotator(0.0, 270, 0.0))

		self.Mesh.AnimationMode = ue.EAnimationMode.AnimationBlueprint  # 使用动画蓝图
		# 注意LoadClass参数的Path需要加上"_C"
		anim_bp_class = ue.LoadClass('/Game/Mannequin/Animations/ThirdPerson_AnimBP.ThirdPerson_AnimBP_C')
		# 设置Mesh使用的蓝图蓝图类具体是哪个
		self.Mesh.SetAnimClass(anim_bp_class)