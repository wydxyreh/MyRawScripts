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