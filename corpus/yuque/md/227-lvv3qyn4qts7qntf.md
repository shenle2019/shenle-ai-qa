---
title: "阶段五. 鸿蒙OS的界面编辑器ArkUI"
doc_id: 256210589
slug: lvv3qyn4qts7qntf
book_id: 73651885
words: 10955
updated_at: 2026-02-06T06:50:56.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/lvv3qyn4qts7qntf
---
# ArkUI 中的组件与布局详解

官网 Api：<https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/arkui-declarative-comp-V5>

## 新建页面

## 页面区域划分

3.1 版本即 api9 和 5.0 版本，即 api12，是不一样，如下图就是在 api12 中的效果

## 两个基础概念

- 页面组件：就一个单独页面，可以被路由跳转，比如从 A 页面跳转到 B 页面，页面使用`@Entry`和`@Component`装饰器装饰，一个页面可以由一个或多个组件组成
- 普通组件：是组件页面的一个部分，只使用`@Component`装饰器装饰

## 语法习惯

## build 函数

- `@Entry`装饰的自定义组件，其build()函数下的**根节点唯一且必要**，且必须为容器组件，其中ForEach禁止作为根节点。

- `@Component`装饰的自定义组件，其build()函数下的根节点唯一且必要，可以为非容器组件，其中ForEach禁止作为根节点。

- 不允许声明本地变量，反例如下。

- 不允许在UI描述里直接使用console.info，但允许在方法或者函数里使用，反例如下。

- 不允许创建本地的作用域，反例如下。

- 不允许调用没有用@Builder装饰的方法，允许系统组件的参数是TS方法的返回值。后面讲解

- 不允许使用switch语法，如果需要使用条件判断，请使用if。示例如下。后面讲解

- 不允许使用表达式，反例如下。后面讲解

- 不允许直接改变状态变量，反例如下。详细分析见[@State常见问题：不允许在build里改状态变量](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-state-V5#不允许在build里改状态变量)，后面讲解

## 常用内置布局组件

布局组件里面可以放子组件，一般用来调整多个子组件的排列方式。

### 行列布局

主要分三个，行列布局只是在平台上排列，没有 Z 轴

- Column：列布局，主轴方向为垂直方向，子组件从上往下排列
- Row：行布局，主轴方向为水平方向，子组件从左右往排列
- Flex：弹性布局，可以设置主轴方向，包含上面两个布局的特点，但使用稍复杂一些

#### 富裕空间

`Column、Row、Flex`中的子组件没有占满其中的空间，剩下的空间就称为富裕空间

#### Column

- Column(value?: {space?: string | number })

> ?：表达可选，即参数可以不写
>
> string | number | boolean：表示联合类型，多个类型组合在一起，多个类型之间使用`|`来分隔
>
> {}：表示 value 的类型是一个对象

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| space | string | number | 否 | 纵向布局元素垂直方向间距。  从API version 9开始，space为负数或者[justifyContent](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-column-V5#justifycontent8)设置为FlexAlign.SpaceBetween、FlexAlign.SpaceAround、FlexAlign.SpaceEvenly时不生效。  默认值：0  单位：vp  **说明：**  可选值为大于等于0的数字，或者可以转换为数字的字符串。 |

- `alignItems(value: HorizontalAlign)：`设置交叉轴对齐方式

- `justifyContent(value: FlexAlign)`：设置主轴对象方式，默认居中排列

#### Row

基本与 Column 使用方式一致

- alignItems(value: VerticalAlign)：控制交叉轴的对齐方式

#### Flex

以弹性方式布局子组件的容器组件。测试人员了解即可

说明

- 该组件从API Version 7开始支持。后续版本如有新增内容，则采用上角标单独标记该内容的起始版本。
- Flex组件在渲染时存在二次布局过程，因此在对性能有严格要求的场景下建议使用[Column](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-column-V5)、[Row](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-row-V5)代替。
- Flex组件主轴默认不设置时撑满父容器，[Column](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-column-V5)、[Row](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-row-V5)组件主轴不设置时默认是跟随子节点大小。

Flex(value?: FlexOptions)

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| value | [FlexOptions](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-flex-V5#flexoptions对象说明) | 否 | 弹性布局子组件参数。 |

- FlexOptions对象说明

|  |  |  |  |
| --- | --- | --- | --- |
| 名称 | 类型 | 必填 | 说明 |
| direction | [FlexDirection](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-appendix-enums-V5#flexdirection) | 否 | 子组件在Flex容器上排列的方向，即主轴的方向。  **默认值：** FlexDirection.Row  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。 |
| wrap | [FlexWrap](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-appendix-enums-V5#flexwrap) | 否 | Flex容器是单行/列还是多行/列排列。  **默认值：** FlexWrap.NoWrap  **说明：**  在多行布局时，通过交叉轴方向，确认新行堆叠方向。  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。 |
| justifyContent | [FlexAlign](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-appendix-enums-V5#flexalign) | 否 | 所有子组件在Flex容器主轴上的对齐格式。  **默认值：** FlexAlign.Start  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。 |
| alignItems | [ItemAlign](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-appendix-enums-V5#itemalign) | 否 | 所有子组件在Flex容器交叉轴上的对齐格式。  **默认值：** ItemAlign.Start  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。 |
| alignContent | [FlexAlign](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-appendix-enums-V5#flexalign) | 否 | 交叉轴中有额外的空间时，多行内容的对齐方式。仅在wrap为Wrap或WrapReverse下生效。  **默认值：** FlexAlign.Start  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。 |
| space12+ | [FlexSpaceOptions12+](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-flex-V5#flexspaceoptions12) | 否 | 所有子组件在Flex容器主轴或交叉轴的space。  **默认值：** {main:LengthMetrics.px(0), cross:LengthMetrics.px(0)}  space为负数、百分比或者justifyContent设置为FlexAlign.SpaceBetween、FlexAlign.SpaceAround、FlexAlign.SpaceEvenly时不生效。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |

- FlexSpaceOptions12+

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| 名称 | 类型 | 只读 | 可选 | 说明 |
| main | [LengthMetrics](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/js-apis-arkui-graphics-V5#lengthmetrics12) | 否 | 是 | Flex容器主轴上的space。  space: {main: LengthMetrics.unit(value)} |
| cross | [LengthMetrics](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/js-apis-arkui-graphics-V5#lengthmetrics12) | 否 | 是 | Flex容器交叉轴上的space。  space: {cross: LengthMetrics.unit(value)} |

### 堆叠布局

堆叠布局有 Z 轴，在手机上如果需要一个元素浮在另一个元素上面的时候，就可以使用堆叠布局

- Stack：堆叠布局，简单的堆叠子组件时，可以使用
- RelativeContainer：相对布局，适合复杂布局场景

#### Stack

Stack(value?: { alignContent?: Alignment })

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| alignContent | [Alignment](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-appendix-enums-V5#alignment) | 否 | 设置子组件在容器内的对齐方式。  默认值：Alignment.Center |

- alignContent(value: Alignment)

#### RelativeContainer

相对布局，可以参照两种锚点，锚点就是参照物，参照哪个组件来做相对布局

- 父容器
- 子组件

讨论两种情况

- 子组件与父容器，父容器使用字符串`__container__`表示
- 子组件与子组件，子组件通过`id`属性来指定锚点

边线

- 控制的子组件：通过`alignRules`属性来控制子组件的相对位置

- 水平：left、middle、right
- 垂直：top、center、bottom

- 锚点：参照物

- 水平：HorizontalAlign.Start(左)、HorizontalAlign.Center、HorizontalAlign.End(右)
- 垂直：VerticalAlign.Top、VerticalAlign.Center、VerticalAlign.Bottom

官网教程：<https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-relativecontainer-V5>

- 相对布局的 Z 轴

相对布局有 Z 轴，可以使用`zIndex`属性来控制

- 同一方向设置多个边线

水平顺序：start 、center、end

同方向上两个及以上位置设置锚点但锚点位置逆序时此子组件大小为0，即不绘制。

- 练习

## 常用内置基础组件

### Blank

空白填充组件，在容器主轴方向上，空白填充组件具有自动填充容器空余部分的能力。仅当父组件为[Row](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-row-V5)/[Column](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-column-V5)/[Flex](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-flex-V5)时生效。

如果容器没有空余部分，则没有效果

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| min | number | string | 否 | 空白填充组件在容器主轴上的最小大小。  默认值：0  **说明：**  不支持设置百分比。负值使用默认值。当最小值大于容器可用空间时，使用最小值作为自身大小并超出容器。 |

### Text

显示一段文本的组件。可以包含[Span](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-span-V5)、[ImageSpan](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-imagespan-V5)、[SymbolSpan](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-symbolspan-V5)和[ContainerSpan](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-containerspan-V5)子组件。

- Text(content?: string | Resource , value?: TextOptions)

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| content | string | [Resource](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#resource) | 否 | 文本内容。包含子组件Span且未设置[属性字符串](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-universal-styled-string-V5#属性字符串)时不生效，显示Span内容，并且此时text组件的样式不生效。  默认值：' ' |
| value11+ | [TextOptions](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-text-V5#textoptions11) | 否 | 文本组件初始化选项。 |

> [Resource](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#resource)：就是资源使用，实际开发是所有的字符串都应该通过资源来使用

- 常用属性

textAlign(value: TextAlign)：文字对齐方式

letterSpacing(value: number | string)：设置文字之间的距离，正值远，负值近

### TextInput

TextInput(value?: TextInputOptions)

|  |  |  |  |
| --- | --- | --- | --- |
| 名称 | 类型 | 必填 | 说明 |
| placeholder | [ResourceStr](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#resourcestr) | 否 | 设置无输入时的提示文本。 |
| text | [ResourceStr](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#resourcestr) | 否 | 设置输入框当前的文本内容。  建议通过onChange事件将状态变量与文本实时绑定，  避免组件刷新时TextInput中的文本内容异常。  从API version 10开始，该参数支持[$$](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-two-way-sync-V5)双向绑定变量。 |
| controller8+ | [TextInputController](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-textinput-V5#textinputcontroller8) | 否 | 设置TextInput控制器。 |

type(value: InputType)：设置输入框类型。InputType 内容如下

|  |  |
| --- | --- |
| 名称 | 描述 |
| Normal | 基本输入模式，无特殊限制。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| Password | 密码输入模式。  支持输入数字、字母、下划线、空格、特殊字符。密码显示小眼睛图标，默认输入文字短暂显示后变成圆点，从API version 12开始，特定设备上输入文字直接显示为圆点。密码输入模式不支持下划线样式。在已启用密码保险箱的情况下，支持用户名、密码的自动保存和自动填充。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| Email | 邮箱地址输入模式。  支持数字、字母、下划线、小数点、!、#、$、%、&、'、\*、+、-、/、=、?、^、`、{、|、}、~，以及@字符（只能存在一个@字符）。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| Number | 纯数字输入模式。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| PhoneNumber9+ | 电话号码输入模式。  支持输入数字、空格、+ 、-、\*、#、(、)，长度不限。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| USER\_NAME11+ | 用户名输入模式。  在已启用密码保险箱的情况下，支持用户名、密码的自动保存和自动填充。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |
| NEW\_PASSWORD11+ | 新密码输入模式。  密码显示小眼睛图标，默认输入文字短暂显示后变成圆点，从API version 12开始，特定设备上输入文字直接显示为圆点。在已启用密码保险箱的情况下，支持自动生成新密码。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |
| NUMBER\_PASSWORD11+ | 纯数字密码输入模式。  密码显示小眼睛图标，默认输入文字短暂显示后变成圆点，从API version 12开始，特定设备上输入文字直接显示为圆点。密码输入模式不支持下划线样式。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |
| NUMBER\_DECIMAL11+ | 带小数点的数字输入模式。  支持数字，小数点（只能存在一个小数点）。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| URL12+ | 带URL的输入模式。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |

`textAlign(value: TextAlign)`：设置文本在输入框中的水平对齐方式。仅支持TextAlign.Start、TextAlign.Center和TextAlign.End。

`onChange(callback: EditableTextOnChangeCallback)`：输入内容发生变化时，触发该回调。

### Image

Image为图片组件，常用于在应用中显示图片。Image支持加载[PixelMap](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/js-apis-image-V5#pixelmap7)、[ResourceStr](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#resourcestr)和[DrawableDescriptor](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/js-apis-arkui-drawabledescriptor-V5#drawabledescriptor)类型的数据源，支持png、jpg、jpeg、bmp、svg、webp、gif和heif类型的图片格式。使用网络图片时，需要申请权限**ohos.permission.INTERNET**。具体申请方式请参考[声明权限](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/declare-permissions-V5)。

Image(src: PixelMap | ResourceStr | DrawableDescriptor)

#### 图片资源

图片的名称有要求：

- 不能以数字开头
- 不能有大写字母
- 不能有`-`

引用图片资源：`$r('app.media.图片名称')`，不需要后续名

### Button

- Button(options: ButtonOptions)
- Button(label: ResourceStr, options?: ButtonOptions)

|  |  |  |  |
| --- | --- | --- | --- |
| 名称 | 类型 | 必填 | 说明 |
| type | [ButtonType](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-button-V5#buttontype枚举说明) | 否 | 描述按钮显示样式。  默认值：ButtonType.Capsule  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| stateEffect | boolean | 否 | 按钮按下时是否开启按压态显示效果，当设置为false时，按压效果关闭。  默认值：true  **说明：**  当开启按压态显示效果，开发者设置状态样式时，会基于状态样式设置完成后的背景色再进行颜色叠加。  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| buttonStyle11+ | [ButtonStyleMode](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-button-V5#buttonstylemode11枚举说明) | 否 | 描述按钮的样式和重要程度。  默认值：ButtonStyleMode.EMPHASIZED  **说明：**  按钮重要程度：强调按钮>普通按钮>文字按钮。  **卡片能力：** 从API version 11开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |
| controlSize11+ | [ControlSize](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-button-V5#controlsize11枚举说明) | 否 | 描述按钮的尺寸。  默认值：ControlSize.NORMAL  **卡片能力：** 从API version 11开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |
| role12+ | [ButtonRole](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-button-V5#buttonrole12枚举说明) | 否 | 描述按钮的角色。  默认值：ButtonRole.NORMAL  **卡片能力：** 从API version 12开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |

type(value: ButtonType)：设置Button样式。

### Toggle

`Toggle(options: { type: ToggleType, isOn?: boolean })`

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| type | [ToggleType](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-toggle-V5#toggletype枚举说明) | 是 | 开关的样式。  默认值：ToggleType.Switch |
| isOn | boolean | 否 | 开关是否打开，true：打开，false：关闭。  默认值：false  从API version 10开始，该参数支持[$$](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-two-way-sync-V5)双向绑定变量。 |

ToggleType

|  |  |
| --- | --- |
| 名称 | 描述 |
| Checkbox | 提供单选框样式。  **说明：**  API version 11开始，Checkbox默认样式由圆角方形变为圆形。  [通用属性margin](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-universal-attributes-size-V5#margin)的默认值为：  {  top: '14px',  right: '14px',  bottom: '14px',  left: '14px'  }。  默认尺寸为:  {width:'20vp', height:'20vp'}。 |
| Button | 提供状态按钮样式，如果子组件有文本设置，则相应的文本内容会显示在按钮内部。  默认尺寸为:高为28vp，宽无默认值。 |
| Switch | 提供开关样式。  **说明：**  [通用属性margin](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-universal-attributes-size-V5#margin)默认值为：  {  top: '6px',  right: '14px',  bottom: '6px',  left: '14px'  }。  默认尺寸为:  {width:'36vp', height:'20vp'}。 |

onChange(callback: (isOn: boolean) => void)：开关状态切换时触发该事件。

### Checkbox

Checkbox(options?: CheckboxOptions)

|  |  |  |  |
| --- | --- | --- | --- |
| 名称 | 类型 | 必填 | 说明 |
| name | string | 否 | 用于指定多选框名称。  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| group | string | 否 | 用于指定多选框所属群组的名称（即所属CheckboxGroup的名称）。  **说明：**  未配合使用[CheckboxGroup](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-checkboxgroup-V5)组件时，此值无用。  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| indicatorBuilder12+ | [CustomBuilder](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#custombuilder8) | 否 | 配置多选框的选中样式为自定义组件。自定义组件与Checkbox组件为中心点对齐显示。indicatorBuilder设置为undefined/null时，默认为indicatorBuilder未设置状态。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |

select(value: boolean)：设置是否选中

shape(value: CheckBoxShape)：设置CheckBox组件形状, 包括圆形和圆角方形。

onChange(callback: (value: boolean) => void)：当选中状态发生变化时，触发该回调。

### Radio

Radio(options: RadioOptions)

|  |  |  |  |
| --- | --- | --- | --- |
| 名称 | 类型 | 必填 | 说明 |
| value | string | 是 | 当前单选框的值。  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| group | string | 是 | 当前单选框的所属群组名称，相同group的Radio只能有一个被选中。  **卡片能力：** 从API version 9开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| indicatorType12+ | [RadioIndicatorType](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-basic-components-radio-V5#radioindicatortype12枚举说明) | 否 | 配置单选框的选中样式。未设置时按照RadioIndicatorType.TICK进行显示。  **卡片能力：** 从API version 12开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |
| indicatorBuilder12+ | [CustomBuilder](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#custombuilder8) | 否 | 配置单选框的选中样式为自定义组件。自定义组件与Radio组件为中心点对齐显示。indicatorBuilder设置为undefined时，按照RadioIndicatorType.TICK进行显示。  **卡片能力：** 从API version 12开始，该接口支持在ArkTS卡片中使用。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |

onChange(callback: (isChecked: boolean) => void)：单选框选中状态改变时触发回调。

### Swiper

滑块视图容器，提供子组件滑动轮播显示的能力。

Swiper(controller?: SwiperController)

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| controller | [SwiperController](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-swiper-V5#swipercontroller) | 否 | 给组件绑定一个控制器，用来控制组件翻页。 |

index(value: number)：设置当前在容器中显示的子组件的索引值。设置小于0或大于等于子组件数量时，按照默认值0处理。

autoPlay(value: boolean)：设置子组件是否自动播放。

interval(value: number)：设置使用自动播放时播放的时间间隔。

indicator(value: DotIndicator | DigitIndicator | boolean)：设置可选导航点指示器样式。

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| value | [DotIndicator](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-swiper-V5#dotindicator10对象说明)10+ | [DigitIndicator](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-swiper-V5#digitindicator10对象说明)10+ | boolean | 是 | 可选导航点指示器样式。  - DotIndicator：圆点指示器样式。  - DigitIndicator：数字指示器样式。  - boolean：是否启用导航点指示器。设置为true启用，false不启用。  默认值：true  默认类型：DotIndicator |

loop(value: boolean)：设置是否开启循环。设置为true时表示开启循环

vertical(value: boolean)：设置是否为纵向滑动。

itemSpace(value: number | string)：设置子组件与子组件之间间隙。不支持设置百分比。

displayCount(value: number | string | SwiperAutoFill, swipeByGroup?: boolean)：设置Swiper视窗内元素显示个数。

onChange(event: (index: number) => void)：当前显示的子组件索引变化时触发该事件，返回值为当前显示的子组件的索引值。

### List 和 ListItem 和 ListGroup

列表包含一系列相同宽度的列表项。适合连续、多行呈现同类数据，例如图片和文本，仅支持[ListItem](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-listitem-V5)、[ListItemGroup](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-listitemgroup-V5)子组件

List(value?:{space?: number | string, initialIndex?: number, scroller?: Scroller})

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| space | number | string | 否 | 子组件主轴方向的间隔。  默认值：0  参数类型为number时单位为vp  **说明：**  设置为负数或者大于等于List内容区长度时，按默认值显示。  space参数值小于List分割线宽度时，子组件主轴方向的间隔取分割线宽度。 |
| initialIndex | number | 否 | 设置当前List初次加载时视口起始位置显示的item的索引值。  默认值：0  **说明：**  设置为负数或超过了当前List最后一个item的索引值时视为无效取值，无效取值按默认值显示。 |
| scroller | [Scroller](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-scroll-V5#scroller) | 否 | 可滚动组件的控制器。用于与可滚动组件进行绑定。  **说明：**  不允许和其他滚动类组件绑定同一个滚动控制对象。 |

divider(value: {strokeWidth: Length; color?: ResourceColor; startMargin?: Length; endMargin?: Length;} | null,)：设置ListItem分割线样式，默认无分割线。

lanes(value: number | LengthConstrain, gutter?: Dimension)：设置List组件的布局列数或行数。gutter为列间距，当列数大于1时生效。

#### ListItem

ListItem(value?: ListItemOptions)

swipeAction(value: SwipeActionOptions)

用于设置ListItem的划出组件。

|  |  |  |  |
| --- | --- | --- | --- |
| 名称 | 类型 | 必填 | 说明 |
| start | [CustomBuilder](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#custombuilder8)  | [SwipeActionItem](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-listitem-V5#swipeactionitem10对象说明) | 否 | ListItem向右划动时item左边的组件（List垂直布局时）或ListItem向下划动时item上方的组件（List水平布局时）。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| end | [CustomBuilder](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#custombuilder8)  | [SwipeActionItem](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-listitem-V5#swipeactionitem10对象说明) | 否 | ListItem向左划动时item右边的组件（List垂直布局时）或ListItem向上划动时item下方的组件（List水平布局时）。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| edgeEffect | [SwipeEdgeEffect](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-listitem-V5#swipeedgeeffect9枚举说明) | 否 | 滑动效果。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| onOffsetChange11+ | (offset: number) => void | 否 | 滑动操作偏移量更改时调用。  **说明：**  当列表项向左或向右滑动（当列表方向为“垂直”时），向上或向下滑动（当列方向为“水平”时）位置发生变化触发，以vp为单位。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |

#### ListItemGroup

ListItemGroup(options?: ListItemGroupOptions)

|  |  |  |  |
| --- | --- | --- | --- |
| 名称 | 类型 | 必填 | 说明 |
| header | [CustomBuilder](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#custombuilder8) | 否 | 设置ListItemGroup头部组件。  **说明：**  可以放单个子组件或不放子组件。 |
| footer | [CustomBuilder](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-types-V5#custombuilder8) | 否 | 设置ListItemGroup尾部组件。  **说明：**  可以放单个子组件或不放子组件。 |
| space | number | string | 否 | 列表项间距。只作用于ListItem与ListItem之间，不作用于header与ListItem、footer与ListItem之间。  默认值：0  单位：vp |
| style10+ | [ListItemGroupStyle](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-listitemgroup-V5#listitemgroupstyle10枚举说明) | 否 | 设置List组件卡片样式。  默认值: ListItemGroupStyle.NONE  设置为ListItemGroupStyle.NONE时无样式。  设置为ListItemGroupStyle.CARD时，建议配合[ListItem](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-listitem-V5)的ListItemStyle.CARD同时使用，显示默认卡片样式。  卡片样式下，ListItemGroup默认规格：左右外边距12vp，上下左右内边距4vp。  卡片样式下, 为卡片内的列表选项提供了默认的focus、hover、press、selected和disable样式。  **说明：**  当前卡片模式下，使用默认Axis.Vertical排列方向，如果listDirection属性设置为Axis.Horizontal，会导致显示混乱;List属性alignListItem默认为ListItemAlign.Center，居中对齐显示。 |

### Grid

Grid(scroller?: Scroller, layoutOptions?: GridLayoutOptions)

- columnsTemplate(value: string)：设置当前网格布局列的数量、固定列宽或最小列宽值，不设置时默认1列。例如, '1fr 1fr 2fr' 是将父组件分3列，将父组件允许的宽分为4等份，第一列占1份，第二列占1份，第三列占2份。
- rowsTemplate(value: string)

#### GridItem

GridItem(value?: GridItemOptions)

- rowStart(value: number)：设置当前元素起始行号。
- rowEnd(value: number)：设置当前元素终点行号。
- columnStart(value: number)：设置当前元素起始列号。
- columnEnd(value: number)：设置当前元素终点列号。

完成如下布局效果

# ArkUI 的通用属性与实战应用

- 通用属性：大部分组件都支持的属性
- 独有属性：部分组件支持的属性
- 还有部分属性是所有属性都支持，CommonAttribute，翻译普通属性

官网 api：<https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/5_2_u901a_u7528_u5c5e_u6027-V5>

- width(value: Length)：设置组件自身的宽度，缺省时使用元素自身内容需要的宽度。若子组件的宽大于父组件的宽，则会画出父组件的范围。

width(value: Length)：设置组件自身的宽度，缺省时使用元素自身内容需要的宽度。若子组件的宽大于父组件的宽，则会画出父组件的范围。

- height(value: Length)：设置组件自身的高度，缺省时使用元素自身内容需要的高度。若子组件的高大于父组件的高，则会画出父组件的范围。

- padding(value: Padding | Length | LocalizedPadding)：设置内边距属性。

- margin(value: Margin | Length | LocalizedMargin)：设置外边距属性。

- `layoutWeight(value: number | string)`：对子组件按比例重新布局，如果有且只有一个子组件设置了，则占满剩余空间。仅在[Row](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-row-V5)/[Column](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-column-V5)/[Flex](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-container-flex-V5)布局中生效。

- 字体相关属性：<https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-universal-attributes-text-style-V5>

- 边框线

官网 Api：<https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-universal-attributes-border-V5>

- backgroundColor(value: ResourceColor)：设置组件背景色。

字体属性：<https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-universal-attributes-text-style-V5>

- fontColor(value: ResourceColor)：设置字体颜色。
- fontSize(value: number | string | Resource)：设置字体大小。
- fontStyle(value: FontStyle)：设置字体样式。
- fontWeight(value: number | FontWeight | string)：设置文本的字体粗细，设置过大可能会在不同字体下有截断。
- fontFamily(value: string | Resource)：设置字体列表。

- 透明度：opacity(0~1)

# ArkUI 的常见函数与事件机制

官网 api：<https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/5_1_u901a_u7528_u4e8b_u4ef6-V5>

## 常用事件

- onClick(event: (event: ClickEvent) => void): T：点击动作触发该回调。
- onTouch(event: (event: TouchEvent) => void): T：手指触摸动作触发该回调。

TouchEvent对象说明

继承于[BaseEvent](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-gesture-customize-judge-V5#baseevent对象说明)。非事件注入场景下，changedTouches是按屏幕显示刷新率重采样的点，touches是按器件刷新率报上来的点，changedTouches的数据可能会和touches里面的不相同。

**系统能力：** SystemCapability.ArkUI.ArkUI.Full

|  |  |  |
| --- | --- | --- |
| 名称 | 类型 | 描述 |
| type | [TouchType](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-appendix-enums-V5#touchtype) | 触摸事件的类型。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| touches | Array<[TouchObject](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-universal-events-touch-V5#touchobject对象说明)> | 全部手指信息。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| changedTouches | Array<[TouchObject](https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-universal-events-touch-V5#touchobject对象说明)> | 当前发生变化的手指信息。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| stopPropagation | () => void | 阻塞事件冒泡。  **元服务API：** 从API version 11开始，该接口支持在元服务中使用。 |
| preventDefault12+ | () => void | 阻止默认事件，具体功能暂未实现。  **元服务API：** 从API version 12开始，该接口支持在元服务中使用。 |

TouchType

|  |  |
| --- | --- |
| 名称 | 描述 |
| Down | 手指按下时触发。 |
| Up | 手指抬起时触发。 |
| Move | 手指按压态在屏幕上移动时触发。 |
| Cancel | 触摸事件取消时触发。 |

- onAttach(callback: Callback<void>): T：组件挂载至组件树时触发此回调。
- onDetach(callback: Callback<void>): T：组件从组件树卸载时触发此回调。
- onAppear(event: () => void): T：组件挂载显示后触发此回调。
- onDisAppear(event: () => void): T：组件卸载消失时触发此回调。

# 路由跳转机制

路由就是进行页面切换的一个对象。

- 压栈：栈就是先进后出的容器
- 弹栈：从栈中弹出

一个页面能够被路由的要求有两个

- 必须是一个页面组件，即被`@Entry`和`@Component`两个装饰器装饰的组件
- 必须在`main_pages.json`中注册了路径，否则报错如下

导入 router 的代码

## 作业

参考地址:<https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/start-overview-V5>

# 多个页面在模拟器上运行

如果有多个页面时，在模拟器只能默认打开一个页面，其它页面通过路由来跳转，怎么设置第一个打开的默认页面呢

# 添加权限

在模拟器上运行时需要，在预览器可以不添加

# ArkTS 的装饰器使用与循环渲染机制

## 条件渲染

- `if(条件语句)`
- `if(条件语句) {} else {}`
- `if(条件语句) {} else if(条件语句){} else {}`

## 循环渲染机制

官网 api：<https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/ts-rendering-control-foreach-V5>

`ForEach`接口基于数组类型数据来进行循环渲染

`ForEach(arr,itemGenerator, keyGenerator)`

|  |  |  |  |
| --- | --- | --- | --- |
| 参数名 | 类型 | 必填 | 说明 |
| arr | Array<Object> | 是 | 数据源，为Array类型的数组。  **说明：**  - 可以设置为空数组，此时不会创建子组件。  - 可以设置返回值为数组类型的函数，例如arr.slice(1, 3)，但设置的函数不应改变包括数组本身在内的任何状态变量，例如不应使用Array.splice(),Array.sort()或Array.reverse()这些会改变原数组的函数。 |
| itemGenerator | (item: Object, index: number) => void | 是 | 组件生成函数。  - 为数组中的每个元素创建对应的组件。  - item参数：arr数组中的数据项。  - index参数（可选）：arr数组中的数据项索引。  **说明：**  - 组件的类型必须是ForEach的父容器所允许的。例如，ListItem组件要求ForEach的父容器组件必须为List组件。 |
| keyGenerator | (item: Object, index: number) => string | 否 | 键值生成函数。  - 为数据源arr的每个数组项生成唯一且持久的键值。函数返回值为开发者自定义的键值生成规则。  - item参数：arr数组中的数据项。  - index参数（可选）：arr数组中的数据项索引。  **说明：**  - 如果函数缺省，**框架默认的键值生成函数为(item: T, index: number) => { return index + '\_\_' + JSON.stringify(item); }**  - 键值生成函数不应改变任何组件状态。 |

### 字符串数组

### 对象数组

## UI 装饰器

- `@Styles`：公共样式提取

- 组件内定义：`@Styles 函数名(){}`
- 组件外定义：`@Styles function 函数名(){}`

- `@Extend`：扩展组件样式

- 组件外定义：`@Extend(组件) function 函数名(参数列表){}`

- `@Builder`：提取 UI 布局函数

- 组件内定义：`@Builer 函数名(参数列表){}`
- 组件外定义：`@Builer function 函数名(参数列表){}`

## 组件状态管理

- `@State`：组件状态，当一个装饰属性时，该属性的值发生变化时，会同步刷新使用该属性的 UI 组件
- `@Prop`：父子组件单身同步
- `@Link`：父子组件双向同步

- `@Observed 和@ObjectLink 装饰器`：嵌套类对象属性变化，常用用于对象数组，二维数组相对使用比较少

- `@Provide 和@Consume 装饰器`：后代组件双向同步，了解即可，不好用
