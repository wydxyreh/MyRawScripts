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
[动画] 使用网格体播放换弹动画: {'PathName': '/Game/ThirdPersonCPP/Maps/UEDPIE_0_关卡1.关卡1:PersistentLevel.MyCharacterBP_C_0.CharacterMesh0', 'SkeletalMesh': 'SK_Mannequin', 'AnimClass': '/Game/ThirdPersonCPP/Blueprints/AnimeBP/MyCharacterAnimBlueprint.MyCharacterAnimBlueprint_C'}
播放蒙太奇的anim_instance:<MyCharacterAnimBlueprint_C 'MyCharacterAnimBlueprint_C_0' at 0x00000B420F250000>
[动画] 动画实例类型: MyCharacterAnimBlueprint_C
[动画] 开始播放换弹动画蒙太奇: My_Reload_Rifle_Hip_Montage
[动画] 换弹动画蒙太奇播放成功，持续时间: 2.1666667461395264秒，播放速率: 1.0
[动画] 换弹动画起始位置: 0.0，总长度: 2.1666667461395264
[动画清理] 已清理所有蒙太奇回调
[动画] 已注册reload蒙太奇混出回调
[动画] 已注册reload蒙太奇结束回调
[动画] 已注册reload蒙太奇开始回调
[动画回调] reload蒙太奇混出: My_Reload_Rifle_Hip_Montage, 中断状态: False
换弹完成! 当前武器弹药: 30/30, 剩余备用弹药: 92
[动画] 停止所有蒙太奇，混合时间: 0.25秒
[状态] 重置换弹状态: 从 True 变为 False
[动画回调] reload蒙太奇结束: My_Reload_Rifle_Hip_Montage, 中断状态: False
[动画清理] 已清理所有蒙太奇回调

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

正确的播放蒙太奇应该是下面的蓝图逻辑：

Begin Object Class=/Script/BlueprintGraph.K2Node_VariableGet Name="K2Node_VariableGet_7" ExportPath="/Script/BlueprintGraph.K2Node_VariableGet'/Game/ThirdPersonCPP/Blueprints/MyCharacterBP.MyCharacterBP:EventGraph.K2Node_VariableGet_7'"
   VariableReference=(MemberName="Mesh",bSelfContext=True)
   NodePosX=928
   NodePosY=1088
   NodeGuid=7738EE4747C7F7205D2AC6A5CC2114D3
   CustomProperties Pin (PinId=332E74C54D4D1C41FD4561B4B0EB1BC3,PinName="Mesh",PinFriendlyName=NSLOCTEXT("UObjectDisplayNames", "Character:Mesh", "Mesh"),Direction="EGPD_Output",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.SkeletalMeshComponent'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=True,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_PlayMontage_1 26E44B39462E4A95B0DD14967382B6FE,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=C1EE27E54CE1AD4E5A31ED95ADE95C1E,PinName="self",PinFriendlyName=NSLOCTEXT("K2Node", "Target", "Target"),PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.Character'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=True,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object
Begin Object Class=/Script/AnimGraph.K2Node_PlayMontage Name="K2Node_PlayMontage_1" ExportPath="/Script/AnimGraph.K2Node_PlayMontage'/Game/ThirdPersonCPP/Blueprints/MyCharacterBP.MyCharacterBP:EventGraph.K2Node_PlayMontage_1'"
   NodePosX=1168
   NodePosY=1008
   NodeGuid=23577FF845B8FD69463E39AAF3DD81F9
   CustomProperties Pin (PinId=8C9E4F654A2A5F4D4DAEA781CCBF9C9A,PinName="execute",PinToolTip="\n执行",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_IfThenElse_2 4790CD214FE5D10AD3B17F90B4E4B145,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=C0AB9CA64CE3F3F9C7BC83809F4FCE94,PinName="then",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=F5CA426B46CC8A21CFF3078471BB0343,PinName="OnCompleted",PinFriendlyName=NSLOCTEXT("UObjectDisplayNames", "PlayMontageCallbackProxy:OnCompleted", "On Completed"),PinToolTip="蒙太奇完成播放且未中断时调用",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=E03AF1D942E615991B50E880B922FF4C,PinName="OnBlendOut",PinFriendlyName=NSLOCTEXT("UObjectDisplayNames", "PlayMontageCallbackProxy:OnBlendOut", "On Blend Out"),PinToolTip="在蒙太奇开始混出且未中断时调用",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=0D5EFF0141A1450C0946B482AB47F9FD,PinName="OnInterrupted",PinFriendlyName=NSLOCTEXT("UObjectDisplayNames", "PlayMontageCallbackProxy:OnInterrupted", "On Interrupted"),PinToolTip="蒙太奇已中断时调用（或播放失败）",Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=C8807F9A48C8728F7676D7BDDD847ACE,PinName="OnNotifyBegin",PinFriendlyName=NSLOCTEXT("UObjectDisplayNames", "PlayMontageCallbackProxy:OnNotifyBegin", "On Notify Begin"),Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=EE29CC5C466A6605EEB83899DD07C4C3,PinName="OnNotifyEnd",PinFriendlyName=NSLOCTEXT("UObjectDisplayNames", "PlayMontageCallbackProxy:OnNotifyEnd", "On Notify End"),Direction="EGPD_Output",PinType.PinCategory="exec",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=939BEA8743E1C2E922616094A7A5B1E6,PinName="NotifyName",PinToolTip="Notify Name\n命名",Direction="EGPD_Output",PinType.PinCategory="name",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=26E44B39462E4A95B0DD14967382B6FE,PinName="InSkeletalMeshComponent",PinToolTip="In Skeletal Mesh Component\n骨骼网格体组件 对象引用",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.SkeletalMeshComponent'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,LinkedTo=(K2Node_VariableGet_7 332E74C54D4D1C41FD4561B4B0EB1BC3,),PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=F24D9FE74C96A825ED5D5D9564254879,PinName="MontageToPlay",PinToolTip="Montage to Play\n动画蒙太奇 对象引用",PinType.PinCategory="object",PinType.PinSubCategory="",PinType.PinSubCategoryObject="/Script/CoreUObject.Class'/Script/Engine.AnimMontage'",PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultObject="/Game/Mannequin/Animations/My_Hit_React_4_Montage.My_Hit_React_4_Montage",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=7F6699674A894D4C7B7AD8AE65E83F53,PinName="PlayRate",PinToolTip="Play Rate\n浮点（单精度）",PinType.PinCategory="real",PinType.PinSubCategory="float",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="1.000000",AutogeneratedDefaultValue="1.000000",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=2F297F5244EB56E387A069B7B8327E06,PinName="StartingPosition",PinToolTip="Starting Position\n浮点（单精度）",PinType.PinCategory="real",PinType.PinSubCategory="float",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="0.000000",AutogeneratedDefaultValue="0.000000",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
   CustomProperties Pin (PinId=B5D83E9141AAFCFED4C52D80B9EEDB0F,PinName="StartingSection",PinToolTip="Starting Section\n命名",PinType.PinCategory="name",PinType.PinSubCategory="",PinType.PinSubCategoryObject=None,PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,DefaultValue="None",AutogeneratedDefaultValue="None",PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,)
End Object

参考C:\Users\wydx\Documents\Unreal Projects\ThirdPersonWithPy\Plugins\NePythonBinding\Tools\pystubs\ue\__init__.pyi，修正现在的代码网格体动画蒙太奇播放，要将动画蒙太奇在正确的网格体上进行播放。