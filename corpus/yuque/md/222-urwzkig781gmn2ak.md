---
title: "阶段九. 鸿蒙自动化测试之单元测试"
doc_id: 256210661
slug: urwzkig781gmn2ak
book_id: 73651885
words: 9621
updated_at: 2026-02-06T06:51:16.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/urwzkig781gmn2ak
---
# 单元测试

主要是检查代码测试，程序员开发好一个功能，会自己测试一下。可以批量去测试

- 白盒测试：程序员自己写的。很清楚代码，所以用例比较简单，不全面
- 黑盒测试：测试人员写的，不了解代码，用例全面，各情况下都要测试一遍

# 创建与执行测试脚本

- **Testing library**：测试类型，默认为DECC-ArkTSUnit，JS语言默认为DECC-JSUnit。
- **ArkTS name**：创建的测试套件名称。测试套件为包含了测试用例的文件。测试套件名称要求在工程目录范围内具有唯一性，且不能使用逗号、横线、空格以及\ / : \* ? “”< > | （）&等特殊字符。
- **Destination package**：测试套件存放的位置，建议存放在待测试模块的test目录下。

> - 这种方式创建的测试套件比较方便，会自动注册到`List.test.ets`文件中。如果是手动创建的测试套件也需要手动注册，否则报错如下
>
> - 所有测试文件的命名为`XXX.test.ets`，否则报错

## Instrument Test

测试用例存放在ohosTest测试目录下，需要运行在设备或模拟器上，支持单元测试和UI测试。 日志需要在 Log 窗口中去查看

> 如果测试代码中有输出日志，需要到 Log 窗口去查看

## Local Test

测试用例存放在test测试目录下，不需要运行在设备或模拟器上，支持单元测试。日志打印在 Run 窗口

> 如果测试代码中有输出日志，日志就在 Run 窗口中查看

## 运行

### 运行单个用例

### 运行测试套件

# 测试用例和测试套

|  |  |  |
| --- | --- | --- |
| No. | API | 功能说明 |
| 1 | describe | 定义一个测试套，支持两个参数：测试套名称和测试套函数。 |
| 2 | beforeAll | 在测试套内定义一个预置条件，在所有测试用例开始前执行且仅执行一次，支持一个参数：预置动作函数。 |
| 3 | beforeEach | 在测试套内定义一个单元预置条件，在每条测试用例开始前执行，执行次数与it定义的测试用例数一致，支持一个参数：预置动作函数。 |
| 4 | afterEach | 在测试套内定义一个单元清理条件，在每条测试用例结束后执行，执行次数与it定义的测试用例数一致，支持一个参数：清理动作函数。 |
| 5 | afterAll | 在测试套内定义一个清理条件，在所有测试用例结束后执行且仅执行一次，支持一个参数：清理动作函数。 |
| 6 | beforeItSpecified | @since1.0.15在测试套内定义一个单元预置条件，仅在指定测试用例开始前执行，支持两个参数：单个用例名称或用例名称数组、预置动作函数。 |
| 7 | afterItSpecified | @since1.0.15在测试套内定义一个单元清理条件，仅在指定测试用例结束后执行，支持两个参数：单个用例名称或用例名称数组、清理动作函数 |
| 8 | it | 定义一条测试用例，支持三个参数：用例名称，过滤参数和用例函数。 |
| 9 | expect | 支持bool类型判断等多种断言方法。 |
| 10 | xdescribe | @since1.0.17定义一个跳过的测试套，支持两个参数：测试套名称和测试套函数。 |
| 11 | xit | @since1.0.17定义一条跳过的测试用例，支持三个参数：用例名称，过滤参数和用例函数。 |

# 断言库

|  |  |  |
| --- | --- | --- |
| No. | API | 功能说明 |
| 1 | assertClose | 检验actualvalue和expectvalue(0)的接近程度是否是expectValue(1)。 |
| 2 | assertContain | 检验actualvalue中是否包含expectvalue。 |
| 3 | assertEqual | 检验actualvalue是否等于expectvalue[0]。 |
| 4 | assertFail | 抛出一个错误。 |
| 5 | assertFalse | 检验actualvalue是否是false。 |
| 6 | assertTrue | 检验actualvalue是否是true。 |
| 7 | assertInstanceOf | 检验actualvalue是否是expectvalue类型，支持基础类型。 |
| 8 | assertLarger | 检验actualvalue是否大于expectvalue。 |
| 9 | assertLess | 检验actualvalue是否小于expectvalue。 |
| 10 | assertNull | 检验actualvalue是否是null。 |
| 11 | assertThrowError | 检验actualvalue抛出Error内容是否是expectValue。 |
| 12 | assertUndefined | 检验actualvalue是否是undefined。 |
| 13 | assertNaN | @since1.0.4 检验actualvalue是否是一个NAN |
| 14 | assertNegUnlimited | @since1.0.4 检验actualvalue是否等于Number.NEGATIVE\_INFINITY |
| 15 | assertPosUnlimited | @since1.0.4 检验actualvalue是否等于Number.POSITIVE\_INFINITY |
| 16 | assertDeepEquals | @since1.0.4 检验actualvalue和expectvalue是否完全相等 |
| 17 | assertPromiseIsPending | @since1.0.4 判断promise是否处于Pending状态。 |
| 18 | assertPromiseIsRejected | @since1.0.4 判断promise是否处于Rejected状态。 |
| 19 | assertPromiseIsRejectedWith | @since1.0.4 判断promise是否处于Rejected状态，并且比较执行的结果值。 |
| 20 | assertPromiseIsRejectedWithError | @since1.0.4 判断promise是否处于Rejected状态并有异常，同时比较异常的类型和message值。 |
| 21 | assertPromiseIsResolved | @since1.0.4 判断promise是否处于Resolved状态。 |
| 22 | assertPromiseIsResolvedWith | @since1.0.4 判断promise是否处于Resolved状态，并且比较执行的结果值。 |
| 23 | not | @since1.0.4 断言取反,支持上面所有的断言功能 |
| 24 | message | @since1.0.17自定义断言异常信息 |

## Promise

Promise：是 ArkTS 中的语法，翻译过来就是期待。

对一段代码有一个期待，期待有三种情况

- Promise 中的代码正在执行
- 期待的内容成功了，成功了通过`.then()` 函数来处理
- 期待的内容失败了，失败了通过`.catch()`函数来处理

在后面还会学习，使用`async`和`await`来处理`Promise`

当一个函数的返回值是 Promise 对象的时候需要知道如何去断言

## 自定义断言

# 异步代码测试

## 异步和同步代码

- 同步代码：大部分是同步代码，同步代码是从上往下按顺序去执行，编译器先执行同步代码，同步由主线程解释器去执行
- 异步代码：是一些比较耗时的代码，结果不会立马就会有，此时采用异步执行的方式，等到有结果了，再返回相应的结果。异步任务会有一个事件循环机制去处理

流程：进门->取号->排队处理业务-离开，

进门因为耗时短，就可以使用同步代码来完，大家都进去

取号：是需要等取号机器给出响应，之后才算完成。异步

处理业务：非常耗时间，异步，3 号窗口去处理

离开银行

异步代码，Promise 的 then 和 catch 中的代码都是异步代码

更好的处理方式，`async`和 `await`来处理，它是一个语法糖，就是一种简写方式

- async：修饰函数的，放在函数定义那一行的
- await：只能出现在 async 修饰的函数中

​

- 使用 `async`关键字定义一个异步测试函数,在测试函数中使用`await`等待测试函数完成。

## done 函数

- `done`函数是测试函数的一个可选回调参数,在测试用例中手动调用,测试框架将等待`done`回调被调用,然后才完成测试。
- 当测试函数中定义`done`函数参数时,测试用例中必须手动调用`done`函数,否则用例失败会出现超时错误。

### Promise回调示例代码

### 回调函数示例代码

# Mock能力

使用场景，比如要测试注册接口，但是接口还没有完成，此时可以使用 mock 来模拟测试。

单元测试框架Mock能力从npm包[1.0.1版本](https://gitee.com/link?target=https%3A%2F%2Fohpm.openharmony.cn%2F%23%2Fcn%2Fdetail%2F%40ohos%252Fhypium)开始支持，需修改源码工程中package.info中配置依赖npm包版本号后使用。

- 仅支持mock自定义对象,不支持mock系统API对象。
- 不支持mock对象的私有函数。

|  |  |  |
| --- | --- | --- |
| No. | API | 功能说明 |
| 1 | mockFunc(obj: object, f：function()) | mock某个类的对象obj的函数f，那么需要传两个参数：obj和f，支持使用异步函数（说明：对mock而言原函数实现是同步或异步没太多区别，因为mock并不关注原函数的实现）。 |
| 2 | when(mockedfunc：function) | 对传入后方法做检查，检查是否被mock并标记过，返回的是一个方法声明。 |
| 3 | afterReturn(x：value) | 设定预期返回一个自定义的值value，比如某个字符串或者一个promise。 |
| 4 | afterReturnNothing() | 设定预期没有返回值，即 undefined。 |
| 5 | afterAction(x：action) | 设定预期返回一个函数执行的操作。 |
| 6 | afterThrow(x：msg) | 设定预期抛出异常，并指定异常msg。 |
| 7 | clear(obj: object) | 用例执行完毕后，进行数据mocker对象的还原处理（还原之后对象恢复被mock之前的功能）。 |
| 8 | any | 设定用户传任何类型参数（undefined和null除外），执行的结果都是预期的值，使用ArgumentMatchers.any方式调用。 |
| 9 | anyString | 设定用户传任何字符串参数，执行的结果都是预期的值，使用ArgumentMatchers.anyString方式调用。 |
| 10 | anyBoolean | 设定用户传任何boolean类型参数，执行的结果都是预期的值，使用ArgumentMatchers.anyBoolean方式调用。 |
| 11 | anyFunction | 设定用户传任何function类型参数，执行的结果都是预期的值，使用ArgumentMatchers.anyFunction方式调用。 |
| 12 | anyNumber | 设定用户传任何数字类型参数，执行的结果都是预期的值，使用ArgumentMatchers.anyNumber方式调用。 |
| 13 | anyObj | 设定用户传任何对象类型参数，执行的结果都是预期的值，使用ArgumentMatchers.anyObj方式调用。 |
| 14 | matchRegexs(Regex) | 设定用户传任何正则表达式类型参数Regex，执行的结果都是预期的值，使用ArgumentMatchers.matchRegexs(Regex)方式调用。 |
| 15 | verify(methodName, argsArray) | 验证methodName（函数名字符串）所对应的函数和其参数列表argsArray的执行行为是否符合预期，返回一个VerificationMode：一个提供验证模式的类，它有times(count)、once()、atLeast(x)、atMost(x)、never()等函数可供选择。 |
| 16 | times(count) | 验证行为调用过count次。 |
| 17 | once() | 验证行为调用过一次。 |
| 18 | atLeast(count) | 验证行为至少调用过count次。 |
| 19 | atMost(count) | 验证行为至多调用过count次。 |
| 20 | never | 验证行为从未发生过。 |
| 21 | ignoreMock(obj, method) | 使用ignoreMock可以还原obj对象中被mock后的函数，对被mock后的函数有效。 |
| 22 | clearAll() | 用例执行完毕后，进行数据和内存清理,不会还原obj对象中被mock后的函数。 |

# 数据驱动

单元测试框架数据驱动能力从[框架 1.0.2版本](https://gitee.com/link?target=https%3A%2F%2Fohpm.openharmony.cn%2F%23%2Fcn%2Fdetail%2F%40ohos%252Fhypium)开始支持。

- 数据参数传递 : 为指定测试套、测试用例传递测试输入数据参数。
- 压力测试 : 为指定测试套、测试用例设置执行次数。

数据驱动可以根据配置参数来驱动测试用例的执行次数和每一次传入的参数，使用时依赖data.json配置文件，文件内容如下：

说明 : **data.json与测试用例\*.test.js|ets文件同目录**

配置参数说明：

|  |  |  |  |
| --- | --- | --- | --- |
|  | 配置项名称 | 功能 | 必填 |
| 1 | "suite" | 测试套配置 。 | 是 |
| 2 | "items" | 测试用例配置 。 | 是 |
| 3 | "describe" | 测试套名称 。 | 是 |
| 4 | "it" | 测试用例名称 。 | 是 |
| 5 | "params" | 测试套 / 测试用例 可传入使用的参数 。 | 否 |
| 6 | "stress" | 测试套 / 测试用例 指定执行次数 。 | 否 |

## 完成的测试项目

要使用数据驱动需要使用完整的测试项目结构，同时还有其它情况也需要完整的项目，例如：

- 数据库测试

- testability目录 > TestAbility.ets文件，
- ets 目录 > pages目录 > Index.ets文件：Index.ets 内容不重要
- testrunner目录 > OpenHarmonyTestRunner.ets文件
- resources目录 > base目录 > element目录 > color.json文件
- resources目录 > base目录 > element目录 > string.json文件
- resources目录 > base目录 > media目录 > icon.png文件
- resources目录 > base目录 > profile目录 > test\_pages.json文件

## pages/Index.ets

> 文件需要与 test\_pages.json 中的文件一致，一般都是大写开头

## TestAbility.ets

## OpenHarmonyTestRunner.ts

> 后缀名是`.ts`

## test\_pages.json

## module.json5

## color.json

## string.json

## media

**icon.png**

## test/data.json

## Ability.test.ets

编译正确如下，如果有步骤没有做就会出现红色的报错信息

在调试模式下可以看到已经成功读取文件了

# 实战测试场景

## 下载 Axios 依赖

`cd` 到指定模块目录下，执行`ohpm i @ohos/axios`

## 请求封装

不需要去修改，直接复制使用

## 模型层

## 接口测试

以注册接口为示例，调用服务端中的注册接口

### 分层开发

通过不同分层来开发的，隔离代码，不会让不同功能的混在一起，以后造成混乱。

代码出错时，能够更好的定位问题

### 直接测试接口

### Mock 模拟测试

## 注册到设备数据库测试

有部分功能必须到模拟器才可以使用，例如数据库。本案例演示注册数据到设备上的`sqlite`数据库中

## 数据驱动实现批量注册

### 使用 api 模块中的内容

- 在 api 模块中的 index.ts 文件中导出对应的内容

- 在需要使用的模块下面引入`api 模块`

# 服务端代码

需要会搭建 nodejs 环境

会上传到课堂派上

在终端中进入到项目根目录，输入`npm i`下载依赖，下载依赖只需要下载一次，再通过`npm run dev`运行项目

可以去测试公司其它线上项目的接口
