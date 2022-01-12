# 台风集合预报(概率预报)路径系统后台
* 前台目前改为私有仓库不再公开
* 靠爱发电，只做展示示意 
* ps: 21-12-07 今年职称又没戏了，不过明年又是新的一年，加油 `(*^▽^*)`
* 2022年了，卧槽燃起来了
## 项目文档:

[部署README](./documents/项目部署.md)
## 项目架构及所用到的技术
![系统架构图](./documents/pic/sys.png)
## 项目预览
+ 21-10-15 目前上线测试的 v1.0 版本预览如下:
![这是图片](./documents/pic/pic001.png)
创建台风基础信息
![创建作业](./documents/pic/pic002.png)
历史创建case搜索栏
![条件搜索](./documents/pic/pic003.png)
选择创建的case加载台风集合(概率)预报路径
![加载台风](./documents/pic/pic004.png)
点击时间轴加载对应时刻的台风信息
![操作时间轴](./documents/pic/pic005.png)
可以切换色标
![切换色标](./documents/pic/pic006.png)
加载概率分布图层
![概率分布图层](./documents/pic/pic007.png)
加载对应时刻的台站，脉冲显示并显示对应的四色警戒
![脉冲4色](./documents/pic/pic008.png)
同时加载台站+增水场
![同时加载](./documents/pic/pic009.png)
显示粗略海洋站信息
![页面初始状态](./documents/pic/pic010.png)
显示详细海洋站信息及右侧对应的潮位预报form
![页面初始状态](./documents/pic/pic011.png)
+ 21-11-15 
+ 加入了箱式图显示百分位数
![页面初始状态](./documents/pic/pic012.png)
+ 对于数据显示可拖动放大调整尺寸
![页面初始状态](./documents/pic/pic013.png)

+ 21-12-22  
  本次基于21-12-10修改意见形成最新的版本  
  本项目于21年4月底开始立项至今也有8个月了，坚持加油 ヾ(◍°∇°◍)ﾉﾞ
+ 对于已经创建完成的作业默认收起task card
+ 统一海洋站icon为5色警戒颜色
+ 每次加载页面默认显示一种色标卡尺(可切换)
+ 对于未加载台风加入时间轴的遮罩
+ 左侧图层栏统一对 `checked` `class` 加入阴影效果
+ ![页面初始状态](./documents/pic/pic014.png)