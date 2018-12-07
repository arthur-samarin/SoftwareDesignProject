# Проект по курсу "Проектирование программного обеспечения"

[![Build Status](https://travis-ci.com/arthur-samarin/SoftwareDesignProject.svg?branch=master)](https://travis-ci.com/arthur-samarin/SoftwareDesignProject) [![codecov](https://codecov.io/gh/arthur-samarin/SoftwareDesignProject/branch/master/graph/badge.svg)](https://codecov.io/gh/arthur-samarin/SoftwareDesignProject)

## Запуск
src - корень исходников<br>
src/app/main.py - запускать это

В рабочей директории должен быть файл config.json:
```
{
  "bot_token": "токен бота",
  "proxy_url": "socks5://прокся:порт"
}
```
Если прокси не используется, то `"proxy_url": null`.