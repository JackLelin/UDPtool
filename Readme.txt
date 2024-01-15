调试工具使用 Python 和 pyqt5库 编写，有两个功能：
1. 收发 UDP 通信 (功能，使用方法同小飞机）。在小飞机基础上添加了发送历史，双击历史条目可以快速发送已发送的命令
2. 为待发送的信息自动添加格式，信息前方加入 Head LenH LenL，后方加入校验信息 Check_H Check_L

源代码中包含的文件：
1. main_UDPtool.py 是主要的 python 源代码文件
2. UDPtoolMain.ui 由 pyqt5 的 designer 工具编辑
3. ui.py 由 UDPtoolMain.ui 编译生成
4. compile_ui.bat 包含编译 UDPtoolMain.ui 的命令。双击即可运行
5. pack_into_exe.bat 包含先编译 ui 再用 pyinstaller 将成 .exe 的命令。双击即可运行。打包好的文件在 dist 文件夹中，可以在没有安装 python 环境的电脑上独立运行

在用 UDPtoolMain.ui 生成 ui.py 之后 使用命令 python main_UDPtool.py 就可以直接运行 python 脚本
安装依赖包和工具：
pip install -U pyinstaller                 
----安装 pyinstaller 打包工具
pip install -U pyqt5 pyqt5-tools
----安装 pyqt5 gui 界面库 和 pyqt5 相关工具 （如 desinger）

designer 安装的位置：
C:\Users\linle\AppData\Roaming\Python\Python311\site-packages\qt5_applications\Qt\bin\designer.exe
Python311 表示 python3.11 版本，根据安装的 python 版本不同路径会不同