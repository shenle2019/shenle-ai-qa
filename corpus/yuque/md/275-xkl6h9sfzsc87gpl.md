---
title: "接口自动化测试试卷-题目答案在一起"
doc_id: 253553327
slug: xkl6h9sfzsc87gpl
book_id: 73651885
words: 5137
updated_at: 2026-01-19T07:09:04.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/xkl6h9sfzsc87gpl
---
# 接口自动化测试试卷

## 一、选择题

1. HTTP协议中，用于获取资源的请求方法是？  
   A. POST  
   B. GET  
   C. PUT  
   D. DELETE  
   **答案**：B  
   **解析**：GET方法用于从服务器获取资源，是最常用的HTTP请求方法。

1. 以下哪个HTTP状态码表示请求成功？  
   A. 200  
   B. 404  
   C. 500  
   D. 401  
   **答案**：A  
   **解析**：200状态码表示请求成功，服务器成功处理了请求。

1. RESTful API中，用于更新资源的标准请求方法是？  
   A. GET  
   B. POST  
   C. PUT  
   D. PATCH  
   **答案**：C  
   **解析**：PUT方法用于更新资源，是RESTful API中的标准方法。

1. 接口测试中，JSONPath主要用于？  
   A. 发送HTTP请求  
   B. 解析JSON响应数据  
   C. 加密数据  
   D. 数据库操作  
   **答案**：B  
   **解析**：JSONPath是一种用于解析JSON数据的查询语言，可以方便地从JSON响应中提取数据。

1. HTTP请求头中，用于指定请求体格式的字段是？  
   A. Content-Type  
   B. Accept  
   C. User-Agent  
   D. Authorization  
   **答案**：A  
   **解析**：Content-Type字段用于指定请求体的格式，如application/json、application/x-www-form-urlencoded等。

1. 以下哪个不是HTTP请求的组成部分？  
   A. 请求行  
   B. 请求头  
   C. 请求体  
   D. 响应体  
   **答案**：D  
   **解析**：HTTP请求由请求行、请求头和请求体组成，响应体是HTTP响应的组成部分。

1. 接口测试中，边界值测试主要用于？  
   A. 测试接口的性能  
   B. 测试接口的安全性  
   C. 测试接口在边界条件下的行为  
   D. 测试接口的并发能力  
   **答案**：C  
   **解析**：边界值测试是一种黑盒测试方法，主要用于测试接口在边界条件下的行为，如输入参数的最大值、最小值等。

1. 接口自动化测试中，数据驱动测试的主要优势是？  
   A. 减少代码重复  
   B. 提高测试执行速度  
   C. 降低测试维护成本  
   D. 以上都是  
   **答案**：D  
   **解析**：数据驱动测试可以减少代码重复，提高测试执行速度，降低测试维护成本，是一种高效的测试方法。

1. JSON格式中，以下哪个表示列表？  
   A. {}  
   B. []  
   C. ()  
   D. <>  
   **答案**：B  
   **解析**：在JSON格式中，列表用方括号[]表示，对象用花括号{}表示。

1. 接口测试中，Mock服务的主要用途是？  
   A. 模拟第三方接口  
   B. 提高测试效率  
   C. 隔离测试环境  
   D. 以上都是  
   **答案**：D  
   **解析**：Mock服务可以模拟依赖接口的响应，隔离测试环境，提高测试效率，方便测试各种边界情况。

1. 接口自动化框架框架中，TestRunner类的主要作用是？  
   A. 发送HTTP请求  
   B. 执行测试用例  
   C. 解析测试数据  
   D. 生成测试报告  
   **答案**：B  
   **解析**：TestRunner类是框架的核心组件，负责执行测试用例，协调各个模块的工作。

1. 框架中，全局变量的存储结构是？  
   A. 列表  
   B. 字典  
   C. 元组  
   D. 集合  
   **答案**：B  
   **解析**：框架使用字典作为全局变量的存储结构，通过g\_context类进行管理。

1. 框架中，YAML用例文件的解析顺序是基于？  
   A. 文件名中的数字前缀  
   B. 文件创建时间  
   C. 文件修改时间  
   D. 文件名字母顺序  
   **答案**：A  
   **解析**：框架按照YAML用例文件的数字前缀顺序进行解析和执行。

1. 框架中，支持的断言类型包括？  
   A. 文本断言  
   B. 数字断言  
   C. 批量断言  
   D. 以上都是  
   **答案**：D  
   **解析**：框架支持多种断言类型，包括文本断言、数字断言和批量断言等。

1. 框架中，g\_context的核心功能是？  
   A. 存储全局变量  
   B. 管理测试数据  
   C. 实现数据共享  
   D. 以上都是  
   **答案**：A  
   **解析**：g\_context的核心功能是负责存储全局变量，是框架的重要组成部分。

1. 接口自动化框架框架中，用于处理文件上传的请求类型是？  
   A. json  
   B. data  
   C. files  
   D. form-data  
   **答案**：C  
   **解析**：框架使用files参数处理文件上传请求，支持多文件上传。

## 二、判断题

1. HTTP协议是无状态的。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：HTTP协议是无状态的，服务器不会记住客户端的请求历史。

1. POST请求比GET请求更安全。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：POST请求的参数在请求体中，而GET请求的参数在URL中，因此POST请求更安全。

1. RESTful API必须使用JSON格式。  
   A. 对  
   B. 错  
   **答案**：B  
   **解析**：RESTful API可以使用多种格式，如JSON、XML等，JSON是最常用的格式但不是必须的。

1. 401状态码表示请求未授权。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：401状态码表示请求未授权，需要提供有效的身份验证信息。

1. JSONPath和XPath的语法完全相同。  
   A. 对  
   B. 错  
   **答案**：B  
   **解析**：JSONPath和XPath的语法相似但不完全相同，JSONPath用于JSON数据，XPath用于XML数据。

1. 接口自动化测试可以完全替代手工测试。  
   A. 对  
   B. 错  
   **答案**：B  
   **解析**：接口自动化测试可以提高测试效率，但不能完全替代手工测试，手工测试在某些场景下仍然是必要的。

1. 接口测试中，只需要测试正常流程即可。  
   A. 对  
   B. 错  
   **答案**：B  
   **解析**：接口测试需要测试正常流程和异常流程，以确保接口的健壮性。

1. HTTPS是HTTP的安全版本，使用SSL/TLS加密。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：HTTPS是HTTP的安全版本，通过SSL/TLS协议对通信进行加密，提高数据传输的安全性。

1. 接口测试中，Mock服务可以模拟依赖接口的行为。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：Mock服务可以模拟依赖接口的响应，方便测试在依赖接口不可用或不稳定时进行。

1. Content-Type为application/json时，请求体必须是JSON格式。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：Content-Type为application/json时，请求体必须是JSON格式，否则服务器可能无法正确解析请求。

1. 接口测试中，参数化可以提高测试覆盖率。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：参数化测试可以使用不同的测试数据执行相同的测试用例，提高测试覆盖率。

1. 500状态码表示服务器内部错误。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：500状态码表示服务器内部错误，通常是服务器端代码出现问题。

1. 接口测试中，断言是验证测试结果的关键。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：断言用于验证接口的响应是否符合预期，是接口测试的核心部分。

1. 所有的HTTP方法都是幂等的。  
   A. 对  
   B. 错  
   **答案**：B  
   **解析**：不是所有的HTTP方法都是幂等的，如POST方法就不是幂等的。

1. API文档应该包括接口的请求参数、响应格式和错误码。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：API文档应该包含接口的详细信息，包括请求参数、响应格式和错误码等。

1. 接口自动化框架框架支持Excel格式的测试用例。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架支持Excel格式的测试用例，通过ExcelCaseParser类进行解析。

1. 接口自动化框架框架中，全局变量可以在不同用例之间共享。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架中的全局变量通过g\_context类进行管理，可以在不同用例之间共享。

1. 接口自动化框架框架中，发送请求POST关键字只能发送JSON格式的数据。  
   A. 对  
   B. 错  
   **答案**：B  
   **解析**：发送请求POST关键字支持多种格式的数据，如JSON、表单数据等。

1. 接口自动化框架框架支持数据驱动测试。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架支持数据驱动测试，可以从外部文件读取测试数据。

1. 接口自动化框架框架中，提取数据JSON关键字使用的是JSONPath语法。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：提取数据JSON关键字使用JSONPath语法从JSON响应中提取数据。

1. 接口自动化框架框架中，批量断言使用的是DeepDiff库。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架使用DeepDiff库进行批量断言，比较两个JSON数据的差异。

1. 接口自动化框架框架只能用于HTTP接口测试。  
   A. 对  
   B. 错  
   **答案**：B  
   **解析**：框架不仅可以用于HTTP接口测试，还可以扩展用于其他类型的接口测试。

1. 接口自动化框架框架支持自定义关键字扩展。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架支持自定义关键字扩展，可以根据需要添加新的关键字。

1. 接口自动化框架框架支持文件上传功能。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架支持文件上传功能，可以通过files参数上传文件。

1. 接口自动化框架框架中，YAML用例文件必须按数字前缀顺序执行。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架按照YAML用例文件的数字前缀顺序进行执行。

1. 接口自动化框架框架中，测试用例的执行顺序是固定的，无法调整。  
   A. 对  
   B. 错  
   **答案**：B  
   **解析**：框架支持调整测试用例的执行顺序，可以通过修改用例文件的数字前缀或使用测试套件进行调整。

1. 接口自动化框架框架中，关键字方法支持中文命名。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架支持中文关键字命名，提高测试用例的可读性。

1. 接口自动化框架框架中，全局变量的生命周期是整个测试过程。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：全局变量的生命周期从测试开始到测试结束，贯穿整个测试过程。

1. 接口自动化框架框架中，支持多种断言比较符，如==、>=、<=等。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架支持多种断言比较符，满足不同的测试需求。

1. 接口自动化框架框架只能在Windows环境下运行。  
   A. 对  
   B. 错  
   **答案**：B  
   **解析**：框架是跨平台的，可以在Windows、Linux、Mac等环境下运行。

1. 接口自动化框架框架中，前置脚本可以用于设置测试环境。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：前置脚本可以用于设置测试环境、准备测试数据等。

1. 接口自动化框架框架支持Allure测试报告生成。  
   A. 对  
   B. 错  
   **答案**：A  
   **解析**：框架支持Allure测试报告生成，可以生成美观、详细的测试报告。

## 三、代码选择题

1. **题目**：TestRunner.py中执行关键字方法的正确代码是？

A. `key_func(step_value)`  
B. `key_func(**step_value)`  
C. `key_func(*step_value)`  
D. `key_func(key, step_value)`  
**答案**：B  
**解析**：使用反射获取的方法对象，需要使用\*\*解包步骤参数执行。

1. **题目**：TestRunner.py中初始化关键字对象的正确代码是？

A. `keywords = ApiCaseContext().init_keywords()`  
B. `keywords = Keywords()`  
C. `keywords = init_keywords()`  
D. `keywords = ApiCaseContext.init_keywords()`  
**答案**：A  
**解析**：使用ApiCaseContext类的实例方法init\_keywords初始化关键字对象。

1. **题目**：TestRunner.py中执行前置脚本的正确代码是？

A. `run_script.exec_script(script, g_context().dict())`  
B. `run_script(script, g_context().show_dict())`  
C. `run_script.exec_script(script, g_context().show_dict())`  
D. `exec_script(script, g_context().show_dict())`  
**答案**：C  
**解析**：使用run\_script模块的exec\_script方法执行脚本，并传入全局变量。

1. **题目**：TestRunner.py中渲染步骤值的正确代码是？

A. `step_value = refresh(step_value, context)`  
B. `step_value = eval(refresh(step_value, context))`  
C. `step_value = refresh(step_value)`  
D. `step_value = eval(refresh(step_value))`  
**答案**：B  
**解析**：使用VarRender模块的refresh方法渲染步骤值，并使用eval处理字符串转换。

1. **题目**：TestRunner.py中获取全局变量的正确代码是？

A. `copy.deepcopy(g_context().show_dict())`  
B. `g_context().show_dict()`  
C. `copy(g_context().show_dict())`  
D. `g_context().get_dict()`  
**答案**：A  
**解析**：使用copy.deepcopy创建全局变量的深拷贝副本。

1. **题目**：TestRunner.py中参数化装饰器的正确代码是？

A. `@pytest.mark.parametrize("caseinfo", data)`  
B. `@parametrize("caseinfo", data)`  
C. `@pytest.parametrize("caseinfo", data)`  
D. `@pytest.mark.parametrize(data, "caseinfo")`  
**答案**：A  
**解析**：使用pytest的mark.parametrize装饰器，参数顺序为参数名在前，数据在后。

1. **题目**：TestRunner.py中读取YAML用例文件的正确代码是？

A. `data = readYaml('./examples/api-cases-yaml/addcard.yaml')`  
B. `data = YamlCaseParser.readYaml('./examples/api-cases-yaml/addcard.yaml')`  
C. `data = readYaml(r'./examples/api-cases-yaml/addcard.yaml')`  
D. `data = loadYaml(r'./examples/api-cases-yaml/addcard.yaml')`  
**答案**：C  
**解析**：使用YamlCaseParser模块的readYaml函数，路径使用r前缀防止转义。

1. **题目**：TestRunner.py中设置Allure测试报告一级模块的正确代码是？

A. `allure.dynamic.feature(base_info.get("一级模块", "默认模块"))`  
B. `allure.dynamic.module(base_info.get("一级模块", "默认模块"))`  
C. `allure.feature(base_info.get("一级模块", "默认模块"))`  
D. `allure.dynamic.section(base_info.get("一级模块", "默认模块"))`  
**答案**：A  
**解析**：使用allure.dynamic.feature方法设置测试报告的一级模块。

1. **题目**：ApiCaseContext.py中session复用的正确代码是？

A. 第一处：`_global_request_obj = requests.session()`，第二处：`self.request = requests.session()`  
B. 第一处：`_global_request_obj = requests()`，第二处：`self.request = requests()`  
C. 第一处：`_global_request_obj = session()`，第二处：`self.request = session()`  
D. 第一处：`_global_request_obj = requests.Session()`，第二处：`self.request = requests.Session`  
**答案**：A  
**解析**：使用requests.session()创建session对象，小写session是函数调用，大写Session是类名。

1. **题目**：Keywords类中发送GET请求的正确代码是？

A. `response = self.request.get(**request_data)`  
B. `response = self.request.request("get", **request_data)`  
C. `response = requests.get(**request_data)`  
D. `response = self.request("get", **request_data)`  
**答案**：B  
**解析**：使用self.request.request方法发送GET请求，参数为请求方法和请求数据。

1. **题目**：Keywords类中提取JSON数据的正确代码是？

A. `result = jsonxath(response, EXPRESSION)`  
B. `result = jsonpath.jsonpath(response, EXPRESSION)`  
C. `result = jsonpath.extract(response, EXPRESSION)`  
D. `result = jsonpath.find(response, EXPRESSION)`  
**答案**：B  
**解析**：使用jsonpath.jsonpath方法从JSON响应中提取数据。

1. **题目**：Keywords类中断言文本的正确代码是？

A.

B.

C.

D.

**答案**：B  
**解析**：数字类型需要转换为float，文本类型转换为str，以支持各种比较操作。

​

1. **题目**：Keywords类中提取MySQL数据的正确代码是？

A. `connect = pymysql.connect(**config)`  
B. `connect = mysql.connect(**config)`  
C. `connect = pymysql(**config)`  
D. `connect = mysql.connector.connect(**config)`  
**答案**：A  
**解析**：使用pymysql.connect方法连接数据库，传入配置参数。

1. **题目**：TestRunner.py中执行用例步骤的正确代码是？

A. `step_value = refresh(step_value, context)`  
B. `step_value = eval(refresh(step_value, context))`  
C. `step_value = render(step_value, context)`  
D. `step_value = eval(render(step_value, context))`  
**答案**：B  
**解析**：使用refresh方法渲染步骤值，并使用eval处理字符串转换，将变量替换为实际值。

1. **题目**：VarRender.py中的refresh函数的正确代码是？

A. `return Template(target).render(context)`  
B. `return Template(str(target)).render(context)`  
C. `Template(str(target)).render(context)`  
D. `return Template(target).render()`  
**答案**：B  
**解析**：使用jinja2的Template类，需要先将目标转换为字符串，然后传入上下文渲染。
