# MA-SerialDebugger
## 基于PyQt5开发的上位机

## 特点
- 简洁
- 简洁
- 简洁


## 食用方法 1
1. 安装python及相关依赖

```bash
pip install -r requirements.txt
```

2. 运行程序

```bash
python SerialDebugger.py
```

## 食用方法 2

下载release中压缩包，解压运行MA.exe(使用pyinstaller打包)即可

## 说明

MA文件夹内为MCU驱动文件，将MA添加到工程并填补MCU串口回调函数即可使用


若使用release中
1. 只支持发送整数且大小为int16, 即范围为-32768 ~ 32767，其余类型数据可自行缩放取整
2. 不支持更改数据包格式，若需更改可自行修改SerialDebugger.py




