#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# 前置
[ -f .env ] || [ -n "$ANDROID_AI_API_KEY" ] || { echo "需要 .env 或 ANDROID_AI_* 环境变量"; exit 1; }
shenle-android-cli devices > /dev/null

# 中文输入方式（默认 clipboard）。模拟器没 cmd clipboard 时设 adbkeyboard：
#   INPUT_METHOD=adbkeyboard bash test-order-flow.sh
# 前提：装好 ADBKeyboard 并切换（见 README）。
INPUT_METHOD="${INPUT_METHOD:-clipboard}"
INPUT_METHOD_FLAG="--input-method $INPUT_METHOD"

# Step 1: 启动 APP
shenle-android-cli launch com.kenny.logistics
sleep 2

# Step 2: 点击首页「一键下单」
shenle-android-cli --debug click "一键下单按钮"
sleep 1.5

# Step 3: 点击「发货人」选项
shenle-android-cli --debug click "发货人选项"
sleep 1.5

# Step 4: 点击发货人文本框 → 输入哈米
shenle-android-cli --debug click "发货人输入框"
sleep 0.5
shenle-android-cli --debug $INPUT_METHOD_FLAG input "发货人输入框" "哈米"
sleep 0.8

# Step 5: 点击手机号文本框 → 输入手机号
shenle-android-cli --debug click "手机号输入框"
sleep 0.5
shenle-android-cli --debug $INPUT_METHOD_FLAG input "手机号输入框" "15096268001"
sleep 0.8

# Step 6: 点击地址文本框
shenle-android-cli --debug click "地址输入框"
sleep 1.5

# Step 7: 滑动地址区域 → 点击确定
shenle-android-cli --debug swipe up --region "地址列表区域" --distance 0.6 -c 2
sleep 1
shenle-android-cli --debug click "确定"
sleep 1.5

# Step 8: 输入详细地址
shenle-android-cli --debug $INPUT_METHOD_FLAG input "详细地址输入框" "长沙"
sleep 0.8

# Step 9: 点击底部【确定】按钮
shenle-android-cli --debug click "底部确定按钮"
sleep 1.5

# 验证
shenle-android-cli screenshot result.png
shenle-android-cli get "发货人信息区域"
