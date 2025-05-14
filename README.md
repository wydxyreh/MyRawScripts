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

目前代码中存在大量重名函数、一部分被定义了却没被用到、旧的函数，移除这些函数和代码


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