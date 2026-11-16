---
title: "App自动化框架考核题（含代码选择题）"
doc_id: 253555696
slug: vlg8oo6skfwtt691
book_id: 73651885
words: 5915
updated_at: 2026-01-19T08:02:27.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/vlg8oo6skfwtt691
---
# App自动化框架考核题

## 一、选择题

1. 在Appium中，用于标识移动设备平台（Android或iOS）的Desired Capability是哪个？  
   A. deviceName  
   B. platformName  
   C. platformVersion  
   D. appPackage

**答案：B**

**解析：**

- `platformName` 指定移动平台，值为"Android"或"iOS"

- `deviceName` 指定设备名称（如"Pixel 4"）

- `platformVersion` 指定操作系统版本（如"12.0"）

- `appPackage` 是Android应用的包名

1. 在Appium中，以下哪个Automation Name用于Android设备的最新UI自动化框架？  
   A. Appium  
   B. Selendroid  
   C. UiAutomator2  
   D. XCUITest

**答案：C**

**解析：**

`UiAutomator2` 是Android推荐的自动化框架（API 16+）

`XCUITest` 是iOS的自动化框架

`Selendroid` 是旧的Android框架（已不推荐）

`Appium` 不是有效的automationName值

1. 在Appium中，以下哪种定位策略可以同时兼容Android和iOS应用？  
    A. id  
    B. className  
    C. xpath  
    D. 以上所有

**答案：D**

**解析：**  
 Appium支持跨平台的定位策略包括：

- `id`：Android的resource-id或iOS的accessibility id

- `className`：Android的class name或iOS的class name

- `xpath`：通用的XML路径定位

- `accessibility id`：跨平台的无障碍标识

- `name`：部分兼容（iOS支持，Android有限支持）

1. 在Appium中，哪个Desired Capability用于指定Android应用的入口Activity？  
   A. app  
   B. appPackage  
   C. appActivity  
   D. mainActivity

**答案：C**

**解析：**

- `appActivity` 指定Android应用的启动Activity（如：`.MainActivity`或`com.example.MainActivity`）

- `appPackage` 指定Android应用的包名

- `app` 指定应用的安装包路径

- `mainActivity` 不是有效的Desired Capability

1. 以下哪个命令用于启动Appium服务？  
   A. appium start  
   B. start appium  
   C. appium  
   D. run appium

**答案：C**  
**解析：** 启动Appium服务的命令是`appium`。

1. 在Appium中，哪个移动手势方法可以实现长按操作？  
   A. tap()  
   B. swipe()  
   C. long\_press()  
   D. scroll()

**答案：C**

**解析：**  
Appium支持的移动手势操作：

`tap()` - 轻触/点击

`long_press()` - 长按（按住不放）

`swipe()` - 滑动

`scroll()` - 滚动

`pinch()` - 捏合缩放

`zoom()` - 放大

1. 在Appium中，哪个方法可以获取当前设备屏幕的分辨率？  
   A. get\_window\_size()  
   B. get\_screenshot\_as\_file()  
   C. get\_capabilities()  
   D. get\_device\_pixel\_ratio()

**答案：A**

**解析：**

`get_window_size()` 返回屏幕的宽度和高度（如：{'width': 1080, 'height': 1920}）

`get_screenshot_as_file()` 用于截图保存

`get_capabilities()` 返回当前会话的Desired Capabilities

`get_device_pixel_ratio()` 不是Appium标准方法

1. 在Appium中，用于指定Android应用启动Activity的参数是？  
   A. appPackage  
   B. appActivity  
   C. platformName  
   D. deviceName

**答案：B**  
**解析：** appActivity参数用于指定Android应用的启动Activity。

1. 以下哪个不是元素定位方式？  
   A. id  
   B. xpath  
   C. class\_name  
   D. name

**答案：D**  
**解析：** 在App自动化测试中，常用的元素定位方式包括id、xpath、class\_name等，name不是常用的定位方式。

1. 以下哪个定位方式在Android和iOS平台都支持？  
   A. id  
   B. xpath  
   C. class\_name  
   D. all of the above

**答案：D**  
**解析：** id、xpath、class\_name等定位方式在Android和iOS平台都支持。

1. 显示等待的作用是？  
   A. 让程序暂停执行  
   B. 等待元素可见或可点击  
   C. 等待固定时间  
   D. 等待页面加载完成

**答案：B**  
**解析：** 显示等待是等待元素可见或可点击，而不是等待固定时间。

1. 隐式等待的作用是？  
   A. 让程序暂停执行  
   B. 等待元素可见或可点击  
   C. 等待固定时间  
   D. 设置全局等待时间

**答案：D**  
**解析：** 隐式等待是设置全局等待时间，对所有元素定位操作都生效。

1. 以下哪个方法用于点击元素？  
   A. send\_keys()  
   B. click()  
   C. clear()  
   D. text

**答案：B**  
**解析：** click()方法用于点击元素，send\_keys()用于输入文本，clear()用于清除输入框内容，text用于获取元素文本。

1. 以下哪个方法用于输入文本？  
   A. send\_keys()  
   B. click()  
   C. clear()  
   D. text

**答案：A**  
**解析：** send\_keys()方法用于输入文本。

1. 以下哪个方法用于获取元素文本？  
   A. send\_keys()  
   B. click()  
   C. clear()  
   D. text

**答案：D**  
**解析：** text属性用于获取元素文本。

1. 以下哪个方法用于清除输入框内容？  
   A. send\_keys()  
   B. click()  
   C. clear()  
   D. text

**答案：C**  
**解析：** clear()方法用于清除输入框内容。

1. 以下哪个是App自动化测试的最佳实践？  
   A. 使用硬编码等待  
   B. 测试用例之间相互依赖  
   C. 使用数据驱动测试  
   D. 不做错误处理

**答案：C**  
**解析：** 使用数据驱动测试是App自动化测试的最佳实践之一，其他选项都是不好的实践。

1. 在HAT框架中，TestRunner类的主要作用是？  
   A. 解析测试用例  
   B. 执行测试用例  
   C. 生成测试报告  
   D. 管理测试数据

**答案：B**  
**解析：** TestRunner类的主要作用是执行测试用例，它负责解析测试数据、执行测试步骤、生成测试报告等。

1. 在HAT框架中，Keywords类封装了什么？  
   A. 测试用例  
   B. 页面元素  
   C. 操作方法  
   D. 测试数据

**答案：C**  
**解析：** Keywords类封装了App自动化测试的各种操作方法，如输入内容、点击元素、断言等。

1. 在HAT框架中，AppCaseContext类用于？  
   A. 管理测试用例  
   B. 初始化驱动  
   C. 解析测试数据  
   D. 生成测试报告

**答案：B**  
**解析：** AppCaseContext类用于初始化Appium驱动，管理设备会话，处理设备复用等。

1. 在HAT框架中，g\_context()的作用是？  
   A. 管理全局变量  
   B. 管理局部变量  
   C. 解析测试用例  
   D. 执行测试用例

**答案：A**  
**解析：** g\_context()是HAT框架中的全局变量管理器，用于存储和获取全局变量。

1. 在HAT框架中，VarRender类用于？  
   A. 渲染变量  
   B. 解析测试用例  
   C. 执行测试用例  
   D. 生成测试报告

**答案：A**  
**解析：** VarRender类用于渲染测试用例中的变量，将变量替换为实际值。

1. 在HAT框架中，load\_yaml\_files用于？  
   A. 加载YAML测试用例  
   B. 加载Excel测试用例  
   C. 加载JSON测试用例  
   D. 加载XML测试用例

**答案：A**  
**解析：** load\_yaml\_files用于加载YAML格式的测试用例文件。

1. 在HAT框架中，load\_excel\_files用于？  
   A. 加载YAML测试用例  
   B. 加载Excel测试用例  
   C. 加载JSON测试用例  
   D. 加载XML测试用例

**答案：B**  
**解析：** load\_excel\_files用于加载Excel格式的测试用例文件。

1. 在HAT框架中，yaml\_case\_parser用于？  
   A. 解析YAML测试用例  
   B. 解析Excel测试用例  
   C. 解析JSON测试用例  
   D. 解析XML测试用例

**答案：A**  
**解析：** yaml\_case\_parser用于解析YAML格式的测试用例文件，提取测试数据。

1. 在HAT框架中，ex\_invoke方法用于？  
   A. 执行扩展关键字  
   B. 执行内置关键字  
   C. 解析测试用例  
   D. 生成测试报告

**答案：A**  
**解析：** ex\_invoke方法用于执行扩展关键字，即用户自定义的关键字方法。

1. 在HAT框架中，session\_reuse参数用于？  
   A. 复用测试用例  
   B. 复用浏览器会话  
   C. 复用设备会话  
   D. 复用测试数据

**答案：C**  
**解析：** session\_reuse参数用于控制是否复用Appium设备会话，设置为True时可以复用设备会话，提高测试执行效率。

1. 在HAT框架中，Keywords类的\_\_init\_\_方法接收什么参数？  
   A. caseinfo  
   B. testdata  
   C. driver  
   D. keywords

**答案：C**  
**解析：** Keywords类的\_\_init\_\_方法接收driver参数，该参数是Appium驱动实例。

1. 在HAT框架中，g\_context类的set\_dict方法用于？  
   A. 设置全局变量  
   B. 设置局部变量  
   C. 获取全局变量  
   D. 获取局部变量

**答案：A**  
**解析：** set\_dict方法用于设置全局变量，将键值对存储到全局变量中。

1. 在HAT框架中，g\_context类的get\_dict方法用于？  
   A. 设置全局变量  
   B. 设置局部变量  
   C. 获取全局变量  
   D. 获取局部变量

**答案：C**  
**解析：** get\_dict方法用于获取全局变量，根据键名获取对应的值。

1. 在HAT框架中，VarRender类的refresh方法用于？  
   A. 刷新变量  
   B. 渲染变量  
   C. 重置变量  
   D. 删除变量

**答案：B**  
**解析：** refresh方法用于渲染变量，将变量替换为实际值。

1. 在HAT框架中，ExcelCaseParser类用于？  
   A. 解析Excel测试用例  
   B. 解析YAML测试用例  
   C. 解析JSON测试用例  
   D. 解析XML测试用例

**答案：A**  
**解析：** ExcelCaseParser类用于解析Excel格式的测试用例文件。

1. 在HAT框架中，YamlCaseParser类用于？  
   A. 解析Excel测试用例  
   B. 解析YAML测试用例  
   C. 解析JSON测试用例  
   D. 解析XML测试用例

**答案：B**  
**解析：** YamlCaseParser类用于解析YAML格式的测试用例文件。

1. 在HAT框架中，run\_script.exec\_script用于？  
   A. 执行Python脚本  
   B. 执行JavaScript脚本  
   C. 执行Shell脚本  
   D. 执行PowerShell脚本

**答案：A**  
**解析：** run\_script.exec\_script用于执行Python脚本，通常用于执行测试用例中的前置条件或后置条件。

## 二、判断题

1. Appium是一个跨平台的App自动化测试工具。  
   A. 对  
   B. 错

**答案：A**  
**解析：** Appium是一个跨平台的App自动化测试工具，支持Android和iOS平台。

1. Appium只能用于自动化测试Android应用。  
   A. 对  
   B. 错

**答案：B**  
**解析：** Appium不仅可以用于自动化测试Android应用，还可以用于自动化测试iOS应用。

​

1. Appium需要修改App源码才能进行自动化测试。  
   A. 对  
   B. 错

**答案：B**  
**解析：** Appium不需要修改App源码就能进行自动化测试，这是它的一个重要优势。

1. 在Appium中，deviceName参数用于指定设备名称。  
   A. 对  
   B. 错

**答案：A**  
**解析：** deviceName参数用于指定设备名称，如"emulator-5554"或"iPhone 12"。

1. 在Appium中，appPackage参数用于指定Android应用的包名。  
   A. 对  
   B. 错

**答案：A**  
**解析：** appPackage参数用于指定Android应用的包名，如"com.kenny.logistics"。

1. 在Appium中，appActivity参数用于指定Android应用的启动Activity。  
   A. 对  
   B. 错

**答案：A**  
**解析：** appActivity参数用于指定Android应用的启动Activity，如"com.kenny.logistics.ui.SplashActivity"。

1. id是App自动化测试中最常用的元素定位方式。  
   A. 对  
   B. 错

**答案：A**  
**解析：** id是App自动化测试中最常用的元素定位方式，因为它通常是唯一的且稳定的。

1. xpath定位方式在Android和iOS平台都支持。  
   A. 对  
   B. 错

**答案：A**  
**解析：** xpath定位方式在Android和iOS平台都支持，但在iOS平台上的性能可能不如Android平台。

1. 显示等待是让程序暂停固定时间。  
   A. 对  
   B. 错

**答案：B**  
**解析：** 显示等待不是让程序暂停固定时间，而是等待元素可见或可点击，超时后才会抛出异常。

1. 隐式等待是设置全局等待时间。  
   A. 对  
   B. 错

**答案：A**  
**解析：** 隐式等待是设置全局等待时间，对所有元素定位操作都生效。

1. click()方法用于点击元素。  
   A. 对  
   B. 错

**答案：A**  
**解析：** click()方法用于点击元素，这是App自动化测试中最常用的操作之一。

1. send\_keys()方法用于获取元素文本。  
   A. 对  
   B. 错

**答案：B**  
**解析：** send\_keys()方法用于输入文本，text属性用于获取元素文本。

1. text属性用于获取元素文本。  
   A. 对  
   B. 错

**答案：A**  
**解析：** text属性用于获取元素文本，这是App自动化测试中常用的操作之一。

1. clear()方法用于清除输入框内容。  
   A. 对  
   B. 错

**答案：A**  
**解析：** clear()方法用于清除输入框内容，在输入新内容之前通常需要先清除旧内容。

1. App自动化测试不需要处理异常。  
   A. 对  
   B. 错

**答案：B**  
**解析：** App自动化测试需要处理异常，否则测试程序可能会因为一个小错误而中断。

1. 在HAT框架中，TestRunner类用于执行测试用例。  
   A. 对  
   B. 错

**答案：A**  
**解析：** TestRunner类是HAT框架的核心类之一，用于执行测试用例。

1. 在HAT框架中，Keywords类封装了操作方法。  
   A. 对  
   B. 错

**答案：A**  
**解析：** Keywords类封装了App自动化测试的各种操作方法，如输入内容、点击元素、断言等。

1. 在HAT框架中，AppCaseContext类用于初始化驱动。  
   A. 对  
   B. 错

**答案：A**  
**解析：** AppCaseContext类用于初始化Appium驱动，管理设备会话。

1. 在HAT框架中，g\_context()用于管理全局变量。  
   A. 对  
   B. 错

**答案：A**  
**解析：** g\_context()是HAT框架中的全局变量管理器，用于存储和获取全局变量。

1. 在HAT框架中，VarRender类用于渲染变量。  
   A. 对  
   B. 错

**答案：A**  
**解析：** VarRender类用于渲染测试用例中的变量，将变量替换为实际值。

1. 在HAT框架中，load\_yaml\_files用于加载YAML测试用例。  
   A. 对  
   B. 错

**答案：A**  
**解析：** load\_yaml\_files用于加载YAML格式的测试用例文件。

1. 在HAT框架中，load\_excel\_files用于加载Excel测试用例。  
   A. 对  
   B. 错

**答案：A**  
**解析：** load\_excel\_files用于加载Excel格式的测试用例文件。

1. 在HAT框架中，yaml\_case\_parser用于解析YAML测试用例。  
   A. 对  
   B. 错

**答案：A**  
**解析：** yaml\_case\_parser用于解析YAML格式的测试用例文件，提取测试数据。

1. 在HAT框架中，ex\_invoke方法用于执行扩展关键字。  
   A. 对  
   B. 错

**答案：A**  
**解析：** ex\_invoke方法用于执行扩展关键字，即用户自定义的关键字方法。

1. 在HAT框架中，session\_reuse参数用于复用设备会话。  
   A. 对  
   B. 错

**答案：A**  
**解析：** session\_reuse参数用于控制是否复用Appium设备会话，设置为True时可以复用设备会话。

1. 在HAT框架中，TestRunner类的test\_case\_exceute方法接收caseinfo参数。  
   A. 对  
   B. 错

**答案：A**  
**解析：** test\_case\_exceute方法接收caseinfo参数，该参数包含了测试用例的所有信息。

1. 在HAT框架中，Keywords类的\_\_init\_\_方法接收driver参数。  
   A. 对  
   B. 错

**答案：A**  
**解析：** Keywords类的\_\_init\_\_方法接收driver参数，该参数是Appium驱动实例。

1. 在HAT框架中，g\_context类的set\_dict方法用于设置全局变量。  
   A. 对  
   B. 错

**答案：A**  
**解析：** set\_dict方法用于设置全局变量，将键值对存储到全局变量中。

1. 在HAT框架中，g\_context类的get\_dict方法用于获取全局变量。  
   A. 对  
   B. 错

**答案：A**  
**解析：** get\_dict方法用于获取全局变量，根据键名获取对应的值。

1. 在HAT框架中，VarRender类的refresh方法用于渲染变量。  
   A. 对  
   B. 错

**答案：A**  
**解析：** refresh方法用于渲染变量，将变量替换为实际值。

1. 在HAT框架中，ExcelCaseParser类用于解析Excel测试用例。  
   A. 对  
   B. 错

**答案：A**  
**解析：** ExcelCaseParser类用于解析Excel格式的测试用例文件。

1. 在HAT框架中，YamlCaseParser类用于解析YAML测试用例。  
   A. 对  
   B. 错

**答案：A**  
**解析：** YamlCaseParser类用于解析YAML格式的测试用例文件。

1. 在HAT框架中，run\_script.exec\_script用于执行Python脚本。  
   A. 对  
   B. 错

**答案：A**  
**解析：** run\_script.exec\_script用于执行Python脚本，通常用于执行测试用例中的前置条件或后置条件。

## 三、代码选择题

1. 在TestRunner类的test\_case\_exceute方法中，执行关键字方法的代码应该是？

A. `key_func(step_value)`  
 B. `key_func(**step_value)`  
 C. `keywords.key_func(step_value)`  
 D. `keywords.key_func(**step_value)`

**答案：B**  
**解析：** 这行代码用于执行关键字方法，使用\*\*step\_value将字典参数传递给关键字方法。

1. 在TestRunner类的test\_case\_exceute方法中，渲染变量的代码应该是？

A. `refresh(step_value, context)`  
 B. `context.refresh(step_value)`  
 C. `VarRender.refresh(step_value, context)`  
 D. `g_context().refresh(step_value, context)`

**答案：A**  
**解析：** 这行代码用于渲染变量，将step\_value中的变量替换为实际值。

1. 在TestRunner类的test\_case\_exceute方法中，处理前置条件的代码应该是？

A. `run_script(script,g_context().show_dict())`  
 B. `exec_script(script,g_context().show_dict())`  
 C. `run_script.exec_script(script,g_context().show_dict())`  
 D. `g_context().exec_script(script)`

**答案：C**  
**解析：** 这行代码用于执行前置条件脚本，并将结果保存到全局变量中。

1. 在Keywords类的输入内容方法中，输入文本的代码应该是？

A. `else_list.send_key(kwargs['数据A'])`  
 B. `else_list.send_keys(kwargs['数据内容'])`  
 C. `else_list.input(kwargs['数据内容'])`  
 D. `else_list.type(kwargs['数据内容'])`

**答案：B**  
**解析：** 这行代码用于向元素发送文本内容。

1. 在Keywords类的点击元素方法中，点击元素的代码应该是？

A. `else_list.click()`  
 B. `else_list.tap()`  
 C. `self.driver.click(else_list)`  
 D. `self.click(else_list)`

**答案：A**  
**解析：** 这行代码用于点击元素。

1. 在Keywords类的wait\_for\_element\_visible方法中，等待元素可见的代码应该是？

A. `time.sleep(3)`  
 B. `EC.presence_of_all_elements_located(locator)`  
 C. `EC.visibility_of_element_located(locator)`  
 D. `driver.implicitly\_wait(10)

**答案：B**  
**解析：** 这行代码用于等待元素可见，使用WebDriverWait和expected\_conditions。这里是找多个元素

1. 在Keywords类的断言文本方法中，抛出断言失败异常的代码应该是？

A. `raise Exception("断言失败")`  
 B. `raise Exception(f"断言失败---{['实际结果']}不等于{['期望结果']}")`  
 C. `raise Exception(f"断言失败---{kwargs['实际结果']}{operators}{kwargs['期望结果']}")`  
 D. `assert False, f"断言失败---{kwargs}{operators}{kwargs}"`

**答案：C**  
**解析：** 这行代码用于抛出断言失败异常，包含详细的错误信息。

1. 在Keywords类的提取数据mysql方法中，保存查询结果到全局变量的代码应该是？

A. `g_context().set_dict("result", result)`  
 B. `g_context().set_by_dict(result)`  
 C. `self.set_global_variable("result", result)`  
 D. `self.set_global_dict(result)`

**答案：B**  
**解析：** 这行代码用于将数据库查询结果保存到全局变量中。

1. 在Keywords类的click\_location方法中，执行点击动作的代码应该是？

A. `action_builder.perform()`  
 B. `self.driver.perform(action_builder)`  
 C. `action_builder.execute()`  
 D. `self.driver.execute(action_builder)`

**答案：A**  
**解析：** 这行代码用于执行ActionBuilder构建的动作。

1. 在Keywords类的input\_location方法中，向当前活动元素输入文本的代码应该是？

A. `self.driver.switch_to.active_element.send_keys(kwargs['文本'])`  
 B. `self.driver.active_element.send_keys(kwargs['文本'])`  
 C. `self.driver.find_element_by_active().send_keys(kwargs['文本'])`  
 D. `self.driver.find_active_element().send_keys(kwargs['文本'])`

**答案：A**  
**解析：** 这行代码用于向当前活动元素发送文本内容。

1. 在AppCaseContext类的initDriver方法中，初始化Appium驱动的代码应该是？

A. `appiumServer`  
 B. `appiumServer, _desiredCapabilities_config`  
 C. `appiumServer, desired_capabilities=_desiredCapabilities_config`  
 D. `command_executor=appiumServer, desired_capabilities=_desiredCapabilities_config`

**答案：B**  
**解析：** 这行代码用于初始化Appium驱动，需要传递Appium服务器URL和Desired Capabilities。

1. 在AppCaseContext类的init\_keywords方法中，当不启用会话复用时初始化驱动的代码应该是？

A. `self.driver=self.initDriver()`  
 B. `self.driver=webdriver.Remote()`  
 C. `self.driver=AppCaseContext.initDriver()`  
 D. `self.driver=_global_driver_obj`

**答案：A**  
**解析：** 这行代码用于初始化驱动，当不启用会话复用时，每次都创建新的驱动实例。

1. 在AppCaseContext类的start方法中，开始录屏的代码应该是？

A. `self.driver.start_recording()`  
 B. `self.driver.start_recording_screen()`  
 C. `self.start_recording_screen()`  
 D. `self.driver.start_screen_recording()`

**答案：B**  
**解析：** 这行代码用于开始录屏，记录测试过程。

1. 在AppCaseContext类的release方法中，设置附件类型的代码应该是？

A. `allure.attachment_type.MP4`  
 B. `type=allure.attachment_type.MP4`  
 C. `attachment_type=allure.attachment_type.MP4`  
 D. `format=allure.attachment_type.MP4`

**答案：C**  
**解析：** 这行代码用于指定附件类型为MP4，因为录屏文件是MP4格式。

1. 在g\_context类的set\_dict方法中，设置全局变量的代码应该是？

A. `self._dic[key]=value`  
 B. `self.dic[key]=value`  
 C. `g_context._dic[key]=value`  
 D. `self._dic.append({key:value})`

**答案：A**  
**解析：** 这行代码用于设置全局变量，将键值对存储到类属性\_dic中。

1. 在g\_context类的get\_dict方法中，获取全局变量的代码应该是？

A. `return self._dic`  
 B. `self._dic.get(key)`  
 C. `return self._dic.get(key, None)`  
 D. `return self.dic(key, None)`

**答案：C**  
**解析：** 这行代码用于获取全局变量，根据键名获取对应的值，如果键不存在则返回None。

1. 在g\_context类的set\_by\_dict方法中，批量设置全局变量的代码应该是？

A. `self._dic = dic`  
 B. `self._dic.update(dic)`  
 C. `self._dic.append(dic)`  
 D. `self._dic.extend(dic)`

**答案：B**  
**解析：** 这行代码用于批量设置全局变量，使用字典更新的方式。
