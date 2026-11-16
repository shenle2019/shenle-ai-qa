---
title: "阶段十. 鸿蒙自动化测试之UI测试"
doc_id: 256210649
slug: medqxe7h3cx795mo
book_id: 73651885
words: 8364
updated_at: 2026-02-06T06:51:13.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/medqxe7h3cx795mo
---
# UI 测试框架

官网 Api 文档：<https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/js-apis-uitest-V5#on9>

|  |  |  |
| --- | --- | --- |
| No. | 特性 | 功能说明 |
| 1 | Driver | Ui测试的入口，提供查找控件，检查控件存在性以及注入按键能力。 |
| 2 | On | 用于描述目标控件特征(文本、id、类型等)，`Driver`根据`On`描述的控件特征信息来查找控件。 |
| 3 | Component | Driver查找返回的控件对象，提供查询控件属性，滑动查找等触控和检视能力。 |
| 4 | UiWindow | Driver查找返回的窗口对象，提供获取窗口属性、操作窗口的能力。 |

> 1. `On`类提供的接口全部是**同步**接口，使用者可以使用**链式调用**其接口构造控件筛选条件。
> 2. `Driver`和`Component`类提供的接口全部是异步接口(`Promise`形式)，**需使用**`await`**语法**。
> 3. Ui测试用例均需使用**异步**语法编写用例，需遵循单元测试框架异步用例编写规范。

## 基础示例

UI 自动化测试只支持 **OHTest**

## Driver

`Driver`类作为UiTest测试框架的总入口，提供查找控件，注入按键，单击坐标，滑动控件，手势操作，截图等能力。

|  |  |  |
| --- | --- | --- |
| No. | API | 功能描述 |
| 1 | create():Promise | 静态方法，构造Driver。 |
| 2 | findComponent(on:On):Promise | 查找匹配控件。 |
| 3 | pressBack():Promise | 单击BACK键。 |
| 4 | click(x:number, y:number):Promise | 基于坐标点的单击。 |
| 5 | swipe(x1:number, y1:number, x2:number, y2:number):Promise | 基于坐标点的滑动。 |
| 6 | assertComponentExist(on:On):Promise | 断言匹配的控件存在。 |
| 7 | delayMs(t:number):Promise | 延时。 |
| 8 | screenCap(s:path):Promise | 截屏。 |
| 9 | findWindow(filter: WindowFilter): Promise | 查找匹配窗口。 |

## On

Ui测试框架通过`On`类提供了丰富的控件特征描述API，用来匹配查找要操作或检视的目标控件。`On`提供的API能力具有以下特点：

- 支持匹配单属性和匹配多属性组合，例如同时指定目标控件text和id。
- 控件属性支持多种匹配模式(等于，包含，`STARTS_WITH`，`ENDS_WITH`)。
- 支持相对定位控件，可通过`isBefore`和`isAfter`等API限定邻近控件特征进行辅助定位。

|  |  |  |
| --- | --- | --- |
| No. | API | 功能描述 |
| 1 | id(i:string):On | 指定控件id。 |
| 2 | text(t:string, p?:MatchPattern):On | 指定控件文本，可指定匹配模式。 |
| 3 | type(t:string):On | 指定控件类型。 |
| 4 | enabled(e:bool):On | 指定控件使能状态。 |
| 5 | clickable(c:bool):On | 指定控件可单击状态。 |
| 6 | longClickable(l:bool):On | 指定控件可长按状态。 |
| 7 | focused(f:bool):On | 指定控件获焦状态。 |
| 8 | scrollable(s:bool):On | 指定控件可滑动状态。 |
| 9 | selected(s:bool):On | 指定控件选中状态。 |
| 10 | checked(c:bool):On | 指定控件选择状态。 |
| 11 | checkable(c:bool):On | 指定控件可选择状态。 |
| 12 | isBefore(b:On):On | **相对定位**，限定目标控件位于指定特征控件之前。 |
| 13 | isAfter(b:On):On | **相对定位**，限定目标控件位于指定特征控件之后。 |

其中，`text`属性支持{`MatchPattern.EQUALS`，`MatchPattern.CONTAINS`，`MatchPattern.STARTS_WITH`，`MatchPattern.ENDS_WITH`}四种匹配模式，缺省使用`MatchPattern.EQUALS`模式。

### 控件定位

**示例代码1**：查找id是`Id_button`的控件。

**示例代码2**：查找id是`Id_button`并且状态是`enabled`的控件，适用于无法通过单一属性定位的场景。

通过`On.id(x).enabled(y)`来指定目标控件的多个属性。

**示例代码3**：查找文本中包含`hello`的控件，适用于不能完全确定控件属性取值的场景。

通过向`On.text()`方法传入第二个参数`MatchPattern.CONTAINS`来指定文本匹配规则；默认规则是`MatchPattern.EQUALS`，即目标控件text属性必须严格等于给定值。

### 控件相对定位

**示例代码1**：查找位于文本控件`Item3_3`后面的，id是`Id_switch`的Switch控件。

通过`On.isAfter`方法，指定位于目标控件前面的特征控件属性，通过该特征控件进行相对定位。一般地，特征控件是某个具有全局唯一特征的控件(例如具有唯一的id或者唯一的text)。

类似的，可以使用`On.isBefore`控件指定位于目标控件后面的特征控件属性，实现相对定位。

## Component

`Component`类代表了Ui界面上的一个控件，一般是通过`Driver.findComponent(on)`方法查找到的。通过该类的实例，用户可以获取控件属性，单击控件，滑动查找，注入文本等操作。

`Component`包含的常用API：

|  |  |  |
| --- | --- | --- |
| No. | API | 功能描述 |
| 1 | click():Promise | 单击该控件。 |
| 2 | inputText(t:string):Promise | 向控件中输入文本(适用于文本框控件)。 |
| 3 | scrollSearch(s:On):Promise | 在该控件上滑动查找目标控件(适用于List等控件)。 |
| 4 | scrollToTop(s:number):Promise | 滑动到该控件顶部(适用于List等控件)。 |
| 5 | scrollTobottom(s:number):Promise | 滑动到该控件底部(适用于List等控件)。 |
| 6 | getText():Promise | 获取控件text。 |
| 7 | getId():Promise | 获取控件id。 |
| 8 | getType():Promise | 获取控件类型。 |
| 9 | isEnabled():Promise | 获取控件使能状态。 |

`Component`完整的API列表请参考[API文档](https://gitee.com/openharmony/interface_sdk-js/blob/master/api/@ohos.UiTest.d.ts)及[示例文档说明](https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/reference/apis-test-kit/js-apis-uitest.md#component9)。

**示例代码1**：单击控件。

**示例代码2**：通过get接口获取控件属性后，可以使用单元测试框架提供的assert\*接口做断言检查。

**示例代码3**：在List控件中滑动查找text是`Item3_3`的子控件。

**示例代码4**：向输入框控件中输入文本。

## UiWindow

`UiWindow`类代表了Ui界面上的一个窗口，一般是通过`Driver.findWindow(WindowFilter)`方法查找到的。通过该类的实例，用户可以获取窗口属性，并进行窗口拖动、调整窗口大小等操作。

`UiWindow`包含的常用API：

|  |  |  |
| --- | --- | --- |
| No. | API | 功能描述 |
| 1 | getBundleName(): Promise | 获取窗口所属应用包名。 |
| 2 | getTitle(): Promise | 获取窗口标题信息。 |
| 3 | focus(): Promise | 使得当前窗口获取焦点。 |
| 4 | moveTo(x: number, y: number): Promise | 将当前窗口移动到指定位置（适用于支持移动的窗口）。 |
| 5 | resize(wide: number, height: number, direction: ResizeDirection): Promise | 调整窗口大小（适用于支持调整大小的窗口）。 |
| 6 | split(): Promise | 将窗口模式切换为分屏模式(适用于支持分屏的窗口)。 |
| 7 | close(): Promise | 关闭当前窗口。 |

`UiWindow`完整的API列表请参考[API文档](https://gitee.com/openharmony/interface_sdk-js/blob/master/api/@ohos.UiTest.d.ts)及[示例文档说明](https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/reference/apis-test-kit/js-apis-uitest.md#uiwindow9)。

**示例代码1**：获取窗口属性。

**示例代码2**：移动窗口。

**示例代码3**：关闭窗口。

## 常见错误

### 异步代码的错误

### 添加网络权限

不会提示，当发现对应服务端接口测试时，如果服务端看到不对应的数据，应该就是网络权限设置的问题

### 组件没有正确的获取到

- ON 的描述写的不对
- 组件被摭挡了，比如弹出来的键盘或者模态弹出框等

### 调用异步代码没有调用 done 函数报错如下

# 项目实战

## 注册功能测试

看下面的代码

## 登录功能测试

# shell uitest 命令

## 命令列表

|  |  |  |
| --- | --- | --- |
| 命令 | 配置参数 | 描述 |
| help | help | 显示uitest工具能够支持的命令信息。 |
| screenCap | [-p] | 截屏。 **-p**：非必填, 指定存储路径和文件名, 只支持存放在/data/local/tmp/下。 默认存储路径：/data/local/tmp，文件名：时间戳 + .png 。 |
| dumpLayout | [-p] <-i | -a> | 支持在daemon运行时执行获取控件树。 **-p** ：指定存储路径和文件名, 只支持存放在/data/local/tmp/下。默认存储路径：/data/local/tmp，文件名：时间戳 + .json。 **-i** ：不过滤不可见控件,也不做窗口合并。 **-a** ：保存 BackgroundColor、 Content、FontColor、FontSize、extraAttrs 属性数据。 **默认** ：不保存上述属性数据。 **-a和-i** 不可同时使用。 |
| uiRecord | uiRecord <record | read> | 录制Ui操作。  **record** ：开始录制，将当前界面操作记录到/data/local/tmp/record.csv，结束录制操作使用Ctrl+C结束录制。  **read** ：读取并且打印录制数据。 |
| uiInput | <help | click | doubleClick | longClick | fling | swipe | drag | dircFling | inputText | keyEvent> | 注入UI模拟操作。 |
| --version | --version | 获取当前工具版本信息。 |
| start-daemon | start-daemon | 拉起uitest测试进程。 |

## 获取版本信息

## 截图使用示例

> 这个路径指的是模拟器的路径
>
> 可以通过右键->Save As 将文件保存到电脑磁盘上

## 获取控件树使用示例

## 用户录制操作

**说明**

录制过程中，需等待当前操作的识别结果在命令行输出后，再进行下一步操作。

以下举例为：record数据中包含的字段及字段含义，仅供参考

## 注入UI模拟操作

使用纯终端命令来实现自动测试操作

|  |  |  |
| --- | --- | --- |
| 命令 | 必填 | 描述 |
| help | 是 | uiInput命令相关帮助信息。 |
| click | 是 | 模拟单击操作。 |
| doubleClick | 是 | 模拟双击操作。 |
| longClick | 是 | 模拟长按操作。 |
| fling | 是 | 模拟快滑操作。 |
| swipe | 是 | 模拟慢滑操作。 |
| drag | 是 | 模拟拖拽操作。 |
| dircFling | 是 | 模拟指定方向滑动操作。 |
| inputText | 是 | 指定坐标点，模拟输入框输入文本操作。 |
| text | 是 | 无需指定坐标点，在当前获焦处，模拟输入框输入文本操作。 |
| keyEvent | 是 | 模拟实体按键事件(如：键盘,电源键,返回上一级,返回桌面等)，以及组合按键操作。 |

### uiInput click/doubleClick/longClick使用示例

获取坐标

|  |  |  |
| --- | --- | --- |
| 配置参数 | 必填 | 描述 |
| point\_x | 是 | 点击x坐标点。 |
| point\_y | 是 | 点击y坐标点。 |

#### uiInput fling使用示例

|  |  |  |
| --- | --- | --- |
| 配置参数 | 必填 | 描述 |
| from\_x | 是 | 滑动起点x坐标。 |
| from\_y | 是 | 滑动起点y坐标。 |
| to\_x | 是 | 滑动终点x坐标。 |
| to\_y | 是 | 滑动终点y坐标。 |
| swipeVelocityPps\_ | 否 | 滑动速度，单位: (px/s)，取值范围：200-40000。 默认值: 600。 |
| stepLength\_ | 否 | 滑动步长。默认值: 滑动距离/50。 **为实现更好的模拟效果，推荐参数缺省/使用默认值。** |

#### uiInput swipe/drag使用示例

|  |  |  |
| --- | --- | --- |
| 配置参数 | 必填 | 描述 |
| from\_x | 是 | 滑动起点x坐标。 |
| from\_y | 是 | 滑动起点y坐标。 |
| to\_x | 是 | 滑动终点x坐标。 |
| to\_y | 是 | 滑动终点y坐标。 |
| swipeVelocityPps\_ | 否 | 滑动速度，单位: (px/s)，取值范围：200-40000。 默认值: 600。 |

#### uiInput dircFling使用示例

|  |  |  |
| --- | --- | --- |
| 配置参数 | 必填 | 描述 |
| direction | 否 | 滑动方向，取值范围：[0,1,2,3]，默认值为0。 0代表向左滑动，1代表向右滑动，2代表向上滑动，3代表向下滑动。 |
| swipeVelocityPps\_ | 否 | 滑动速度，单位: (px/s)，取值范围：200-40000。 默认值: 600。 |
| stepLength | 否 | 滑动步长。 默认值: 滑动距离/50。为更好的模拟效果，推荐参数缺省/使用默认值。 |

#### uiInput inputText使用示例

|  |  |  |
| --- | --- | --- |
| 配置参数 | 必填 | 描述 |
| point\_x | 是 | 输入框x坐标点。 |
| point\_y | 是 | 输入框y坐标点。 |
| text | 是 | 输入文本内容。 |

#### uiInput keyEvent使用示例

|  |  |  |
| --- | --- | --- |
| 配置参数 | 必填 | 描述 |
| keyID1 | 是 | 实体按键对应ID，取值范围：KeyCode/Back/Home/Power。 当取Back/Home/Power时，不支持输入组合键。 |
| keyID2 | 否 | 实体按键对应ID。 |
| keyID3 | 否 | 实体按键对应ID。 |

**说明**

最多支持传入是三个键值

#### 键码值。

|  |  |  |
| --- | --- | --- |
| 名称 | 值 | 说明 |
| KEYCODE\_FN | 0 | 功能（Fn）键 |
| KEYCODE\_UNKNOWN | -1 | 未知按键 |
| KEYCODE\_HOME | 1 | 功能（Home）键 |
| KEYCODE\_BACK | 2 | 返回键 |
| KEYCODE\_SEARCH13+ | 9 | 搜索键 |
| KEYCODE\_MEDIA\_PLAY\_PAUSE | 10 | 多媒体键：播放/暂停 **原子化服务API：** 从API version 12开始，该接口支持在原子化服务中使用。 |
| KEYCODE\_MEDIA\_STOP | 11 | 多媒体键：停止 **原子化服务API：** 从API version 12开始，该接口支持在原子化服务中使用。 |
| KEYCODE\_MEDIA\_NEXT | 12 | 多媒体键：下一首 **原子化服务API：** 从API version 12开始，该接口支持在原子化服务中使用。 |
| KEYCODE\_MEDIA\_PREVIOUS | 13 | 多媒体键：上一首 **原子化服务API：** 从API version 12开始，该接口支持在原子化服务中使用。 |
| KEYCODE\_MEDIA\_REWIND | 14 | 多媒体键：快退 **原子化服务API：** 从API version 12开始，该接口支持在原子化服务中使用。 |
| KEYCODE\_MEDIA\_FAST\_FORWARD | 15 | 多媒体键：快进 **原子化服务API：** 从API version 12开始，该接口支持在原子化服务中使用。 |
| KEYCODE\_VOLUME\_UP | 16 | 音量增加键 |
| KEYCODE\_VOLUME\_DOWN | 17 | 音量减小键 |
| KEYCODE\_POWER | 18 | 电源键 |
| KEYCODE\_CAMERA | 19 | 拍照键 |
| KEYCODE\_VOLUME\_MUTE | 22 | 扬声器静音键 |
| KEYCODE\_MUTE | 23 | 话筒静音键 |
| KEYCODE\_BRIGHTNESS\_UP | 40 | 亮度调节按键：调亮 |
| KEYCODE\_BRIGHTNESS\_DOWN | 41 | 亮度调节按键：调暗 |
| KEYCODE\_0 | 2000 | 按键'0' |
| KEYCODE\_1 | 2001 | 按键'1' |
| KEYCODE\_2 | 2002 | 按键'2' |
| KEYCODE\_3 | 2003 | 按键'3' |
| KEYCODE\_4 | 2004 | 按键'4' |
| KEYCODE\_5 | 2005 | 按键'5' |
| KEYCODE\_6 | 2006 | 按键'6' |
| KEYCODE\_7 | 2007 | 按键'7' |
| KEYCODE\_8 | 2008 | 按键'8' |
| KEYCODE\_9 | 2009 | 按键'9' |
| KEYCODE\_STAR | 2010 | 按键'\*' |
| KEYCODE\_POUND | 2011 | 按键'#' |
| KEYCODE\_DPAD\_UP | 2012 | 导航键：向上 |
| KEYCODE\_DPAD\_DOWN | 2013 | 导航键：向下 |
| KEYCODE\_DPAD\_LEFT | 2014 | 导航键：向左 |
| KEYCODE\_DPAD\_RIGHT | 2015 | 导航键：向右 |
| KEYCODE\_DPAD\_CENTER | 2016 | 导航键：确定键 |
| KEYCODE\_A | 2017 | 按键'A' |
| KEYCODE\_B | 2018 | 按键'B' |
| KEYCODE\_C | 2019 | 按键'C' |
| KEYCODE\_D | 2020 | 按键'D' |
| KEYCODE\_E | 2021 | 按键'E' |
| KEYCODE\_F | 2022 | 按键'F' |
| KEYCODE\_G | 2023 | 按键'G' |
| KEYCODE\_H | 2024 | 按键'H' |
| KEYCODE\_I | 2025 | 按键'I' |
| KEYCODE\_J | 2026 | 按键'J' |
| KEYCODE\_K | 2027 | 按键'K' |
| KEYCODE\_L | 2028 | 按键'L' |
| KEYCODE\_M | 2029 | 按键'M' |
| KEYCODE\_N | 2030 | 按键'N' |
| KEYCODE\_O | 2031 | 按键'O' |
| KEYCODE\_P | 2032 | 按键'P' |
| KEYCODE\_Q | 2033 | 按键'Q' |
| KEYCODE\_R | 2034 | 按键'R' |
| KEYCODE\_S | 2035 | 按键'S' |
| KEYCODE\_T | 2036 | 按键'T' |
| KEYCODE\_U | 2037 | 按键'U' |
| KEYCODE\_V | 2038 | 按键'V' |
| KEYCODE\_W | 2039 | 按键'W' |
| KEYCODE\_X | 2040 | 按键'X' |
| KEYCODE\_Y | 2041 | 按键'Y' |
| KEYCODE\_Z | 2042 | 按键'Z' |
| KEYCODE\_COMMA | 2043 | 按键',' |
| KEYCODE\_PERIOD | 2044 | 按键'.' |
| KEYCODE\_ALT\_LEFT | 2045 | 左Alt键 |
| KEYCODE\_ALT\_RIGHT | 2046 | 右Alt键 |
| KEYCODE\_SHIFT\_LEFT | 2047 | 左Shift键 |
| KEYCODE\_SHIFT\_RIGHT | 2048 | 右Shift键 |
| KEYCODE\_TAB | 2049 | Tab键 |
| KEYCODE\_SPACE | 2050 | 空格键 |
| KEYCODE\_SYM | 2051 | 符号修改器按键 |
| KEYCODE\_EXPLORER | 2052 | 浏览器功能键，此键用于启动浏览器应用程序 |
| KEYCODE\_ENVELOPE | 2053 | 电子邮件功能键，此键用于启动电子邮件应用程序 |
| KEYCODE\_ENTER | 2054 | 回车键 |
| KEYCODE\_DEL | 2055 | 退格键 |
| KEYCODE\_GRAVE | 2056 | 按键'`' |
| KEYCODE\_MINUS | 2057 | 按键'-' |
| KEYCODE\_EQUALS | 2058 | 按键'=' |
| KEYCODE\_LEFT\_BRACKET | 2059 | 按键'[' |
| KEYCODE\_RIGHT\_BRACKET | 2060 | 按键']' |
| KEYCODE\_BACKSLASH | 2061 | 按键'\' |
| KEYCODE\_SEMICOLON | 2062 | 按键';' |
| KEYCODE\_APOSTROPHE | 2063 | 按键''' (单引号) |
| KEYCODE\_SLASH | 2064 | 按键'/' |
| KEYCODE\_AT | 2065 | 按键'@' |
| KEYCODE\_PLUS | 2066 | 按键'+' |
| KEYCODE\_MENU | 2067 | 菜单键 |
| KEYCODE\_PAGE\_UP | 2068 | 向上翻页键 |
| KEYCODE\_PAGE\_DOWN | 2069 | 向下翻页键 |
| KEYCODE\_ESCAPE | 2070 | ESC键 |
| KEYCODE\_FORWARD\_DEL | 2071 | 删除键 |
| KEYCODE\_CTRL\_LEFT | 2072 | 左Ctrl键 |
| KEYCODE\_CTRL\_RIGHT | 2073 | 右Ctrl键 |
| KEYCODE\_CAPS\_LOCK | 2074 | 大写锁定键 |
| KEYCODE\_SCROLL\_LOCK | 2075 | 滚动锁定键 |
| KEYCODE\_META\_LEFT | 2076 | 左元修改器键 |
| KEYCODE\_META\_RIGHT | 2077 | 右元修改器键 |
| KEYCODE\_FUNCTION | 2078 | 功能键 |
| KEYCODE\_SYSRQ | 2079 | 系统请求/打印屏幕键 |
| KEYCODE\_BREAK | 2080 | Break/Pause键 |
| KEYCODE\_MOVE\_HOME | 2081 | 光标移动到开始键 |
| KEYCODE\_MOVE\_END | 2082 | 光标移动到末尾键 |
| KEYCODE\_INSERT | 2083 | 插入键 |
| KEYCODE\_FORWARD | 2084 | 前进键 |
| KEYCODE\_MEDIA\_PLAY | 2085 | 多媒体键：播放 **原子化服务API：** 从API version 12开始，该接口支持在原子化服务中使用。 |
| KEYCODE\_MEDIA\_PAUSE | 2086 | 多媒体键：暂停 **原子化服务API：** 从API version 12开始，该接口支持在原子化服务中使用。 |
| KEYCODE\_MEDIA\_CLOSE | 2087 | 多媒体键：关闭 |
| KEYCODE\_MEDIA\_EJECT | 2088 | 多媒体键：弹出 |
| KEYCODE\_MEDIA\_RECORD | 2089 | 多媒体键：录音 |
| KEYCODE\_F1 | 2090 | 按键'F1' |
| KEYCODE\_F2 | 2091 | 按键'F2' |
| KEYCODE\_F3 | 2092 | 按键'F3' |
| KEYCODE\_F4 | 2093 | 按键'F4' |
| KEYCODE\_F5 | 2094 | 按键'F5' |
| KEYCODE\_F6 | 2095 | 按键'F6' |
| KEYCODE\_F7 | 2096 | 按键'F7' |
| KEYCODE\_F8 | 2097 | 按键'F8' |
| KEYCODE\_F9 | 2098 | 按键'F9' |
| KEYCODE\_F10 | 2099 | 按键'F10' |
| KEYCODE\_F11 | 2100 | 按键'F11' |
| KEYCODE\_F12 | 2101 | 按键'F12' |
| KEYCODE\_NUM\_LOCK | 2102 | 小键盘锁 |
| KEYCODE\_NUMPAD\_0 | 2103 | 小键盘按键'0' |
| KEYCODE\_NUMPAD\_1 | 2104 | 小键盘按键'1' |
| KEYCODE\_NUMPAD\_2 | 2105 | 小键盘按键'2' |
| KEYCODE\_NUMPAD\_3 | 2106 | 小键盘按键'3' |
| KEYCODE\_NUMPAD\_4 | 2107 | 小键盘按键'4' |
| KEYCODE\_NUMPAD\_5 | 2108 | 小键盘按键'5' |
| KEYCODE\_NUMPAD\_6 | 2109 | 小键盘按键'6' |
| KEYCODE\_NUMPAD\_7 | 2110 | 小键盘按键'7' |
| KEYCODE\_NUMPAD\_8 | 2111 | 小键盘按键'8' |
| KEYCODE\_NUMPAD\_9 | 2112 | 小键盘按键'9' |
| KEYCODE\_NUMPAD\_DIVIDE | 2113 | 小键盘按键'/' |
| KEYCODE\_NUMPAD\_MULTIPLY | 2114 | 小键盘按键'\*' |
| KEYCODE\_NUMPAD\_SUBTRACT | 2115 | 小键盘按键'-' |
| KEYCODE\_NUMPAD\_ADD | 2116 | 小键盘按键'+' |
| KEYCODE\_NUMPAD\_DOT | 2117 | 小键盘按键'.' |
| KEYCODE\_NUMPAD\_COMMA | 2118 | 小键盘按键',' |
| KEYCODE\_NUMPAD\_ENTER | 2119 | 小键盘按键回车 |
| KEYCODE\_NUMPAD\_EQUALS | 2120 | 小键盘按键'=' |
| KEYCODE\_NUMPAD\_LEFT\_PAREN | 2121 | 小键盘按键'(' |
| KEYCODE\_NUMPAD\_RIGHT\_PAREN | 2122 | 小键盘按键')' |
| KEYCODE\_VIRTUAL\_MULTITASK | 2210 | 虚拟多任务键 |
| KEYCODE\_SLEEP | 2600 | 睡眠键 |
| KEYCODE\_ZENKAKU\_HANKAKU | 2601 | 日文全宽/半宽键 |
| KEYCODE\_102ND | 2602 | 102nd按键 |
| KEYCODE\_RO | 2603 | 日文Ro键 |
| KEYCODE\_KATAKANA | 2604 | 日文片假名键 |
| KEYCODE\_HIRAGANA | 2605 | 日文平假名键 |
| KEYCODE\_HENKAN | 2606 | 日文转换键 |
| KEYCODE\_KATAKANA\_HIRAGANA | 2607 | 日语片假名/平假名键 |
| KEYCODE\_MUHENKAN | 2608 | 日文非转换键 |
| KEYCODE\_LINEFEED | 2609 | 换行键 |
| KEYCODE\_MACRO | 2610 | 宏键 |
| KEYCODE\_NUMPAD\_PLUSMINUS | 2611 | 数字键盘上的加号/减号键 |
| KEYCODE\_SCALE | 2612 | 扩展键 |
| KEYCODE\_HANGUEL | 2613 | 日文韩语键 |
| KEYCODE\_HANJA | 2614 | 日文汉语键 |
| KEYCODE\_YEN | 2615 | 日元键 |
| KEYCODE\_STOP | 2616 | 停止键 |
| KEYCODE\_AGAIN | 2617 | 重复键 |
| KEYCODE\_PROPS | 2618 | 道具键 |
| KEYCODE\_UNDO | 2619 | 撤消键 |
| KEYCODE\_COPY | 2620 | 复制键 |
| KEYCODE\_OPEN | 2621 | 打开键 |
| KEYCODE\_PASTE | 2622 | 粘贴键 |
| KEYCODE\_FIND | 2623 | 查找键 |
| KEYCODE\_CUT | 2624 | 剪切键 |
| KEYCODE\_HELP | 2625 | 帮助键 |
| KEYCODE\_CALC | 2626 | 计算器特殊功能键，用于启动计算器应用程序 |
| KEYCODE\_FILE | 2627 | 文件按键 |
| KEYCODE\_BOOKMARKS | 2628 | 书签键 |
| KEYCODE\_NEXT | 2629 | 下一个按键 |
| KEYCODE\_PLAYPAUSE | 2630 | 播放/暂停键 |
| KEYCODE\_PREVIOUS | 2631 | 上一个按键 |
| KEYCODE\_STOPCD | 2632 | CD停止键 |
| KEYCODE\_CONFIG | 2634 | 配置键 |
| KEYCODE\_REFRESH | 2635 | 刷新键 |
| KEYCODE\_EXIT | 2636 | 退出键 |
| KEYCODE\_EDIT | 2637 | 编辑键 |
| KEYCODE\_SCROLLUP | 2638 | 向上滚动键 |
| KEYCODE\_SCROLLDOWN | 2639 | 向下滚动键 |
| KEYCODE\_NEW | 2640 | 新建键 |
| KEYCODE\_REDO | 2641 | 恢复键 |
| KEYCODE\_CLOSE | 2642 | 关闭键 |
| KEYCODE\_PLAY | 2643 | 播放键 |
| KEYCODE\_BASSBOOST | 2644 | 低音增强键 |
| KEYCODE\_PRINT | 2645 | 打印键 |
| KEYCODE\_CHAT | 2646 | 聊天键 |
| KEYCODE\_FINANCE | 2647 | 金融键 |
| KEYCODE\_CANCEL | 2648 | 取消键 |
| KEYCODE\_KBDILLUM\_TOGGLE | 2649 | 键盘灯光切换键 |
| KEYCODE\_KBDILLUM\_DOWN | 2650 | 键盘灯光调暗键 |
| KEYCODE\_KBDILLUM\_UP | 2651 | 键盘灯光调亮键 |
| KEYCODE\_SEND | 2652 | 发送键 |
| KEYCODE\_REPLY | 2653 | 答复键 |
| KEYCODE\_FORWARDMAIL | 2654 | 邮件转发键 |
| KEYCODE\_SAVE | 2655 | 保存键 |
| KEYCODE\_DOCUMENTS | 2656 | 文件键 |
| KEYCODE\_VIDEO\_NEXT | 2657 | 下一个视频键 |
| KEYCODE\_VIDEO\_PREV | 2658 | 上一个视频键 |
| KEYCODE\_BRIGHTNESS\_CYCLE | 2659 | 背光渐变键 |
| KEYCODE\_BRIGHTNESS\_ZERO | 2660 | 亮度调节为0键 |
| KEYCODE\_DISPLAY\_OFF | 2661 | 显示关闭键 |
| KEYCODE\_BTN\_MISC | 2662 | 游戏手柄上的各种按键 |
| KEYCODE\_GOTO | 2663 | 进入键 |
| KEYCODE\_INFO | 2664 | 信息查看键 |
| KEYCODE\_PROGRAM | 2665 | 程序键 |
| KEYCODE\_PVR | 2666 | 个人录像机(PVR)键 |
| KEYCODE\_SUBTITLE | 2667 | 字幕键 |
| KEYCODE\_FULL\_SCREEN | 2668 | 全屏键 |
| KEYCODE\_KEYBOARD | 2669 | 键盘 |
| KEYCODE\_ASPECT\_RATIO | 2670 | 屏幕纵横比调节键 |
| KEYCODE\_PC | 2671 | 端口控制键 |
| KEYCODE\_TV | 2672 | TV键 |
| KEYCODE\_TV2 | 2673 | TV键2 |
| KEYCODE\_VCR | 2674 | 录像机开启键 |
| KEYCODE\_VCR2 | 2675 | 录像机开启键2 |
| KEYCODE\_SAT | 2676 | SIM卡应用工具包（SAT）键 |
| KEYCODE\_CD | 2677 | CD键 |
| KEYCODE\_TAPE | 2678 | 磁带键 |
| KEYCODE\_TUNER | 2679 | 调谐器键 |
| KEYCODE\_PLAYER | 2680 | 播放器键 |
| KEYCODE\_DVD | 2681 | DVD键 |
| KEYCODE\_AUDIO | 2682 | 音频键 |
| KEYCODE\_VIDEO | 2683 | 视频键 |
| KEYCODE\_MEMO | 2684 | 备忘录键 |
| KEYCODE\_CALENDAR | 2685 | 日历键 |
| KEYCODE\_RED | 2686 | 红色指示器 |
| KEYCODE\_GREEN | 2687 | 绿色指示器 |
| KEYCODE\_YELLOW | 2688 | 黄色指示器 |
| KEYCODE\_BLUE | 2689 | 蓝色指示器 |
| KEYCODE\_CHANNELUP | 2690 | 频道向上键 |
| KEYCODE\_CHANNELDOWN | 2691 | 频道向下键 |
| KEYCODE\_LAST | 2692 | 末尾键 |
| KEYCODE\_RESTART | 2693 | 重启键 |
| KEYCODE\_SLOW | 2694 | 慢速键 |
| KEYCODE\_SHUFFLE | 2695 | 随机播放键 |
| KEYCODE\_VIDEOPHONE | 2696 | 可视电话键 |
| KEYCODE\_GAMES | 2697 | 游戏键 |
| KEYCODE\_ZOOMIN | 2698 | 放大键 |
| KEYCODE\_ZOOMOUT | 2699 | 缩小键 |
| KEYCODE\_ZOOMRESET | 2700 | 缩放重置键 |
| KEYCODE\_WORDPROCESSOR | 2701 | 文字处理键 |
| KEYCODE\_EDITOR | 2702 | 编辑器键 |
| KEYCODE\_SPREADSHEET | 2703 | 电子表格键 |
| KEYCODE\_GRAPHICSEDITOR | 2704 | 图形编辑器键 |
| KEYCODE\_PRESENTATION | 2705 | 演示文稿键 |
| KEYCODE\_DATABASE | 2706 | 数据库键标 |
| KEYCODE\_NEWS | 2707 | 新闻键 |
| KEYCODE\_VOICEMAIL | 2708 | 语音信箱 |
| KEYCODE\_ADDRESSBOOK | 2709 | 通讯簿 |
| KEYCODE\_MESSENGER | 2710 | 通信键 |
| KEYCODE\_BRIGHTNESS\_TOGGLE | 2711 | 亮度切换键 |
| KEYCODE\_SPELLCHECK | 2712 | AL拼写检查 |
| KEYCODE\_COFFEE | 2713 | 终端锁/屏幕保护程序 |
| KEYCODE\_MEDIA\_REPEAT | 2714 | 媒体循环键 |
| KEYCODE\_IMAGES | 2715 | 图像键 |
| KEYCODE\_BUTTONCONFIG | 2716 | 按键配置键 |
| KEYCODE\_TASKMANAGER | 2717 | 任务管理器 |
| KEYCODE\_JOURNAL | 2718 | 日志按键 |
| KEYCODE\_CONTROLPANEL | 2719 | 控制面板键 |
| KEYCODE\_APPSELECT | 2720 | 应用程序选择键 |
| KEYCODE\_SCREENSAVER | 2721 | 屏幕保护程序键 |
| KEYCODE\_ASSISTANT | 2722 | 智慧键 |
| KEYCODE\_KBD\_LAYOUT\_NEXT | 2723 | 下一个键盘布局键 |
| KEYCODE\_BRIGHTNESS\_MIN | 2724 | 最小亮度键 |
| KEYCODE\_BRIGHTNESS\_MAX | 2725 | 最大亮度键 |
| KEYCODE\_KBDINPUTASSIST\_PREV | 2726 | 键盘输入Assist\_Previous，查看输入法输入记录 |
| KEYCODE\_KBDINPUTASSIST\_NEXT | 2727 | 键盘输入Assist\_Next，查看输入法输入拓展 |
| KEYCODE\_KBDINPUTASSIST\_PREVGROUP | 2728 | 键盘输入Assist\_Previous，切换输入组中上一个输入法 |
| KEYCODE\_KBDINPUTASSIST\_NEXTGROUP | 2729 | 键盘输入Assist\_Next，切换输入组中下一个输入法 |
| KEYCODE\_KBDINPUTASSIST\_ACCEPT | 2730 | 键盘输入Assist\_Accept |
| KEYCODE\_KBDINPUTASSIST\_CANCEL | 2731 | 键盘输入Assist\_Cancel |
| KEYCODE\_FRONT | 2800 | 挡风玻璃除雾器开关 |
| KEYCODE\_SETUP | 2801 | 设置键 |
| KEYCODE\_WAKEUP | 2802 | 唤醒键 |
| KEYCODE\_SENDFILE | 2803 | 发送文件按键 |
| KEYCODE\_DELETEFILE | 2804 | 删除文件按键 |
| KEYCODE\_XFER | 2805 | 文件传输(XFER)按键 |
| KEYCODE\_PROG1 | 2806 | 程序键1 |
| KEYCODE\_PROG2 | 2807 | 程序键2 |
| KEYCODE\_MSDOS | 2808 | MS-DOS键（微软磁盘操作系统 |
| KEYCODE\_SCREENLOCK | 2809 | 屏幕锁定键 |
| KEYCODE\_DIRECTION\_ROTATE\_DISPLAY | 2810 | 方向旋转显示键 |
| KEYCODE\_CYCLEWINDOWS | 2811 | Windows循环键 |
| KEYCODE\_COMPUTER | 2812 | 按键 |
| KEYCODE\_EJECTCLOSECD | 2813 | 弹出CD键 |
| KEYCODE\_ISO | 2814 | ISO键 |
| KEYCODE\_MOVE | 2815 | 移动键 |
| KEYCODE\_F13 | 2816 | 按键'F13' |
| KEYCODE\_F14 | 2817 | 按键'F14' |
| KEYCODE\_F15 | 2818 | 按键'F15' |
| KEYCODE\_F16 | 2819 | 按键'F16' |
| KEYCODE\_F17 | 2820 | 按键'F17' |
| KEYCODE\_F18 | 2821 | 按键'F18' |
| KEYCODE\_F19 | 2822 | 按键'F19' |
| KEYCODE\_F20 | 2823 | 按键'F20' |
| KEYCODE\_F21 | 2824 | 按键'F21' |
| KEYCODE\_F22 | 2825 | 按键'F22' |
| KEYCODE\_F23 | 2826 | 按键'F23' |
| KEYCODE\_F24 | 2827 | 按键'F24' |
| KEYCODE\_PROG3 | 2828 | 程序键3 |
| KEYCODE\_PROG4 | 2829 | 程序键4 |
| KEYCODE\_DASHBOARD | 2830 | 仪表板 |
| KEYCODE\_SUSPEND | 2831 | 挂起键 |
| KEYCODE\_HP | 2832 | 高阶路径键 |
| KEYCODE\_SOUND | 2833 | 音量键 |
| KEYCODE\_QUESTION | 2834 | 疑问按键 |
| KEYCODE\_CONNECT | 2836 | 连接键 |
| KEYCODE\_SPORT | 2837 | 运动按键 |
| KEYCODE\_SHOP | 2838 | 商城键 |
| KEYCODE\_ALTERASE | 2839 | 交替键 |
| KEYCODE\_SWITCHVIDEOMODE | 2841 | 在可用视频之间循环输出（监视器/LCD/TV输出/等） |
| KEYCODE\_BATTERY | 2842 | 电池按键 |
| KEYCODE\_BLUETOOTH | 2843 | 蓝牙按键 |
| KEYCODE\_WLAN | 2844 | 无线局域网 |
| KEYCODE\_UWB | 2845 | 超宽带（UWB） |
| KEYCODE\_WWAN\_WIMAX | 2846 | WWAN WiMAX按键 |
| KEYCODE\_RFKILL | 2847 | 控制所有收音机的键 |
| KEYCODE\_CHANNEL | 3001 | 向上频道键 |
| KEYCODE\_BTN\_0 | 3100 | 按键0 |
| KEYCODE\_BTN\_1 | 3101 | 按键1 |
| KEYCODE\_BTN\_2 | 3102 | 按键2 |
| KEYCODE\_BTN\_3 | 3103 | 按键3 |
| KEYCODE\_BTN\_4 | 3104 | 按键4 |
| KEYCODE\_BTN\_5 | 3105 | 按键5 |
| KEYCODE\_BTN\_6 | 3106 | 按键6 |
| KEYCODE\_BTN\_7 | 3107 | 按键7 |
| KEYCODE\_BTN\_8 | 3108 | 按键8 |
| KEYCODE\_BTN\_9 | 3109 | 按键9 |

## 实战练习

结合 DevEco\_Testing\_for\_App 中的 UIViewer 工具，通过 Shell 命令实现登录输入及按钮点击。在首页滑动轮播图及滚动页面

# shell aa test 命令

根据所携带的参数启动测试框架。

**启动测试框架命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h/--help | 帮助信息。 |
| -b | 必选参数，bundleName。 |
| -s unittest | 必选参数，testRunner。 |
| -p | 可选参数，testRunner的packageName。  **说明**：该可选参数仅可在FA模型下使用。 |
| -m | 可选参数，testRunner的moduleName。  **说明**：该可选参数仅可在Stage模型下使用。 |
| -s class | 可选参数，指定要执行的测试套或测试用例。 |
| -s level | 可选参数，指定要执行用例的用例级别。 |
| -s size | 可选参数，指定要执行用例的用例规模。 |
| -s testType | 可选参数，指定要执行用例的用例类型。 |
| -s timeout | 可选参数，测试用例执行的超时时间（单位ms），默认为5000。 |
| -s <any-key> | 可选参数，任意键值对。 |
| -w | 可选参数，指定测试运行时间（单位ms）。 |
| -D | 可选参数，调试模式。 |

**返回值**：

当成功启动测试框架时，返回"user test started."；当启动失败时，返回"error: failed to start user test."和对应的错误信息。

**示例**：

示例代码1：执行所有测试用例。

示例代码2：执行指定的describe测试套用例，指定多个需用逗号隔开。

示例代码3：执行指定测试套中指定的用例，指定多个需用逗号隔开。

示例代码4：执行指定除配置以外的所有的用例，设置不执行多个测试套需用逗号隔开。

示例代码5：执行指定it名称的所有用例，指定多个需用逗号隔开。

示例代码6：用例执行超时时长配置。

示例代码7：用例以breakOnError模式执行用例。

示例代码8：执行测试类型匹配的测试用例?。官网意思不明确

示例代码9：执行测试级别匹配的测试用例?。官网意思不明确

示例代码10：执行测试规模匹配的测试用例?。官网意思不明确

示例代码11：执行测试用例指定次数。

**查看测试结果**

- cmd模式执行过程,会打印如下相关日志信息。

|  |  |
| --- | --- |
| 日志输出字段 | 日志输出字段含义 |
| OHOS\_REPORT\_SUM | 当前测试套用例总数。 |
| OHOS\_REPORT\_STATUS: class | 当前执行用例测试套名称。 |
| OHOS\_REPORT\_STATUS: id | 用例执行语言,默认JS。 |
| OHOS\_REPORT\_STATUS: numtests | 测试包中测试用例总数 。 |
| OHOS\_REPORT\_STATUS: stream | 当前用例发生错误时，记录错误信息。 |
| OHOS\_REPORT\_STATUS: test | 当前用例执行的it name。 |
| OHOS\_REPORT\_STATUS\_CODE | 当前用例执行结果状态。0表示通过，1表示错误，2表示失败。 |
| OHOS\_REPORT\_STATUS: consuming | 当前用例执行消耗的时长（ms）。 |

- cmd执行完成后,会打印如下相关日志信息。

|  |  |
| --- | --- |
| 日志输出字段 | 日志输出字段含义 |
| run | 当前测试包用例总数。 |
| Failure | 当前测试失败用例个数。 |
| Error | 当前执行用例发生错误用例个数。 |
| Pass | 当前执行用例通过用例个数 。 |
| Ignore | 当前未执行用例个数。 |
| taskconsuming | 执行当前测试用例总耗时（ms）。 |
