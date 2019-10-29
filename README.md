# Скрипт пересылки сообщений из syslog-ng на сервер Radius
Данный скрипт используется в связке с syslong-ng сервером и служит для пересылки сообщений с Syslog-ng сервера на Radius.

## Описание файлов
- syslog_radius_router.py - скрипт для Python3 (версия 3.6)
- initial.conf - файл конфигурации, содержащий поля, которые ищутся в логе syslog и соответсвующие им атрибуты, а также дополнительные атрибуты, которые должны быть включены в пакет Radius.
- dictionary и dictionary.freeradius - словари Radius
- README.md - описание

## Настройка скрипта
1. В конфигурационном файле initial.conf прописать какие поля ищем в логе Syslog-ng и на какие атрибуты Radius их надо заменять
2. В конфигурационном файле настроить данные RADIUS сервера (IP, секретный ключ, путь к словарю) и указать путь к логу событий скрипта.
3. В файле syslog_radius_router.py указать абсолютный путь к файлу конфигурации initial.conf
4. В конфигурации syslog-ng (/etc/syslog-ng/syslog-ng.conf или другой файл, если используется) источник, фильтры и назначение: 
```
source s_net { udp(ip(0.0.0.0) port(514)); };

filter f_ise_host     {    (
                                host("10.31.34.101")
                                );
                        };

filter f_ise_auth { message("Authentication succeeded"); };

destination d_python { program("python3 -u /home/python-radius/syslog_radius_router.py"
        flags(no_multi_line)
        flush_timeout(1000)
); };

log { source(s_net);
      filter(f_ise_host);
      filter(f_ise_auth);
      destination(d_python);
};
```
5. Перезагрузить службу 
```
service syslog-ng restart
```
6. Для проверки отработки скрипта запустить 
```
tail -f /var/log/syslog-python.log
```
7. Отправить запрос автоматизации. В случае успеха в логе будет сообщение
```
Successfully sent Acct packet to server.
```
