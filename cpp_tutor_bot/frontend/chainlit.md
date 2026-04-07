# Chainlit 配置文件

[project]
name = "C++小老师"
version = "2.0.0"
description = "你的编程学习好伙伴！🌟"

[UI]
theme = "light"
title = "C++小老师 🎓"
show_avatars = true
show_return_to_chat_button = false
default_collapse_content = false
hide_cot_without_projects = true

[features]
file_upload = true
allowed_file_types = ["text/x-c++src", "text/x-c", "text/x-c++hdr", "text/plain", "application/octet-stream"]
max_file_size_mb = 10
speech_to_text = false

[custom]
custom_css = "./public/custom.css"
