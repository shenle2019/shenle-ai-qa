---
title: "阶段七. 鸿蒙官方指定语言ArkTS进阶实操"
doc_id: 256210626
slug: mf1bxlvgpmkiayt6
book_id: 73651885
words: 2528
updated_at: 2026-02-06T06:51:04.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/mf1bxlvgpmkiayt6
---
# 鸿蒙自定义组件详解

## 新建组件文件

### ArkTS 模块

## 组件定义

## 组件参数

- 普通参数
- 必传参数
- 响应式参数，单向传递
- 响应式参数，双向传递
- 响应式参数，对象类型

# 一个示例讲透鸿蒙组件生命周期

## 页面组件

- aboutToAppear：挂载
- onDidBuild：页面成功渲染
- onPageShow：页面显示
- onPageHide：页面隐藏
- aboutToDisappear：卸载
- onBackPress：返回

## 普通组件

- aboutToAppear：挂载
- onDidBuild：组件成功渲染
- aboutToDisappear：卸载

## 示例代码

# 应用状态管理

- `LocalStorage`：页面级 UI 状态管理，一个`@Entry`装饰的页面组件，绑定一个`LocalStorage`对象`ls`，然后该页面组件中所有子组件都可以从该对象`ls`中获取数据或者修改数据，比`@Provide`和`@Consume`更方便
- `AppStorage`：整个应用的状态管理，在整个应用，不管是哪个模块或者页面都可以实现数据共享
- `PersistentStorage`：持久化 UI 数据存储，即永久保存。需要在模拟器中测试，在预览器无法使用

## LocalStorage

- 创建实例：`let ls = new LocalStorage({属性名: 属性值})`
- 通过`@Entry(ls)`进行页面与`ls`对象的绑定
- 在组件中如何操作`ls`对象数据

- 通过装饰器，该数据需要在页面进行显示，就使用装饰取出保存到指定的属性中

- `@LocalStorageProp("属性名")`：单向绑定
- `@LocalStorageLink("属性名")`：双向绑定

- 也可以通过相应 api 来操作，一般在事件中使用，或者不能使用 UI 操作的地方，比`Ability`页面中

- <https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-state-management-V5#localstorage9>

## AppStorage

整个应用共享一份数据，当`Stage`应用在启动时，会创建一个`AppStorage`的实例，该实例在整个应用中都可以直接使用，可以很方便的共享数据

注意：`AppStorage`是一单例模式的类，单例模式即一个类永远只能创建一个实例。

使用方式与`LocalStorage`类似

- `@StorageProp`：单向绑定
- `@StorageLink`：双向绑定

## PersistentStorage

可以实现数据持久化。如果遇到嵌套对象或对象数组，可以通过 `JSON.stringify()`转换成字符串保存，然后再通过`JSON.parse()`将字符串转换成对象

## Environment

# 其它状态管理使用场景分析与总结

## `@Watch`

@Watch应用于对状态变量的监听。如果开发者需要关注某个状态变量的值是否改变，可以使用@Watch为状态变量设置回调函数。

## `@Track`

@Track应用于class对象的属性级更新。@Track装饰的属性变化时，只会触发该属性关联的UI更新。

## $$语法

$$运算符为系统内置组件提供TS变量的引用，使得TS变量和系统内置组件的内部状态保持同步。

# 性能优化之组件复用

## @Reusable装饰的自定义组件具备可复用能力

# 鸿蒙开发动态界面详解

## wrapBuilder

测试人员只需要了解
