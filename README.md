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
通过按键实现登录后的save和load，进入游戏、登录成功后，可以按下F5和F8分别进行save和load操作，并打印出相关信息，包括操作的执行情况和结果，以及操作的数据对象的具体值，比如save操作后，可以打印出保存的数据对象的具体值；
保存的数据为MyCharacter中的变量值，比如MyAllBulletNumber、MyWeaopnBulletNumber。