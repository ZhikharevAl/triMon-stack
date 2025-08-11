# Monitoring Stack

Комплексная система мониторинга на базе Prometheus, Grafana, InfluxDB и Telegraf для мониторинга Java-приложений и системных метрик.

## Архитектура

Система состоит из трех основных компонентов, развернутых в разных директориях:

### 1. Базовый мониторинг (`/1/`)
- **Prometheus** - сбор и хранение метрик
- **Telegraf** - системные метрики хоста
- **JMX Agent** - мониторинг Java-приложений через JMX

### 2. Полный стек мониторинга (`/2/`)
- **InfluxDB** - временная база данных для метрик
- **Prometheus** - сбор метрик
- **Grafana** - визуализация и дашборды
- **Telegraf** - системные метрики
- **NewMock App** - тестовое Java-приложение
- **PostgreSQL Exporter** - метрики базы данных

### 3. Дополнительный Telegraf (`/3/`)
- Отдельный экземпляр Telegraf для расширенного мониторинга

## Быстрый старт

### Запуск базового мониторинга
```bash
cd 1/
docker-compose up -d
```

### Запуск полного стека
```bash
cd 2/
# Сборка образа приложения
docker build -t newmock-app .
# Запуск всех сервисов
docker-compose up -d
```

### Запуск дополнительного Telegraf
```bash
cd 3/
docker-compose up -d
```

## Доступные сервисы

### Веб-интерфейсы
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **InfluxDB**: http://localhost:8086
- **NewMock App**: http://localhost:8081

### Метрики и экспортеры
- **JMX Metrics**: http://localhost:8888/metrics
- **Telegraf Metrics**: http://localhost:9273/metrics
- **PostgreSQL Exporter**: http://localhost:9190/metrics
- **Application Actuator**: http://localhost:8081/actuator

## Конфигурация

### Prometheus
Основная конфигурация находится в файлах:
- `/1/prometheus/prometheus.yml` - базовая конфигурация
- `/2/prometheus/prometheus.yml` - расширенная конфигурация

Настроенные job'ы:
- `prometheus` - самомониторинг Prometheus
- `telegraf` - системные метрики
- `hello-jmx-gr01` - JMX метрики Java-приложений
- `newmock-app-actuator` - Spring Boot Actuator метрики
- `postgres-exporter` - метрики PostgreSQL
- `backend-jmx-centos` - JMX метрики backend-приложения
- `backend-actuator-centos` - Actuator метрики backend-приложения

### Telegraf
Конфигурационные файлы:
- `/1/telegraf_srv2.conf`
- `/2/telegraf.conf`
- `/3/telegraf_srv3.conf`

### PostgreSQL Exporter
Кастомные запросы для мониторинга PostgreSQL находятся в `/2/postgres_queries.yaml`, включая:
- `pg_stat_statements` - статистика выполнения запросов

## Java-приложения

### NewMock Application
Тестовое Spring Boot приложение с настроенным мониторингом:
- **Порт приложения**: 8081
- **JMX порт**: 9999
- **Actuator endpoints**: `/actuator/*`
- **Health check**: `/actuator/health`

### JMX Мониторинг
Для Java-приложений используется JMX Prometheus Agent:
- Конфигурация: `/1/jmx-config.yml`
- Экспорт метрик на порту 8888

### Actuator Exporter
Кастомный Python-скрипт (`/1/actuator_exporter.py`) для конвертации Spring Boot Actuator метрик в формат Prometheus:
- Порт: 7778
- Endpoint: `/metrics`
- Health check: `/health`

## Сеть и ресурсы

### Docker Networks
- `monitor-net` - основная сеть мониторинга (172.27.0.0/16)

### Ограничения ресурсов
Настроены лимиты для всех сервисов:
- **InfluxDB**: 6GB RAM, 1 CPU
- **Prometheus**: 2GB RAM, 0.3 CPU
- **Grafana**: 512MB RAM, 0.1 CPU
- **Telegraf**: 512MB RAM, 0.1 CPU
- **NewMock App**: 768MB RAM, 0.2 CPU
- **PostgreSQL Exporter**: 128MB RAM, 0.05 CPU

## Безопасность и доступы

### Grafana
- **Логин**: admin
- **Пароль**: admin
- Данные хранятся в `/home/user01/grafana/data`

### InfluxDB
- Данные хранятся в `/home/user01/influxdb`
- Скрипты инициализации в `/home/user01/influxdb/scripts`

### Prometheus
- Данные хранятся в Docker volume `prometheus_data`
- Конфигурация в `/home/user01/prometheus`

## Health Checks

Настроены проверки здоровья для критических сервисов:
- **InfluxDB**: `curl -f http://localhost:8086/ping`
- **Prometheus**: `wget -q --spider http://localhost:9090/-/ready`
- **NewMock App**: `curl -f http://localhost:8080/actuator/health`

## Мониторинг внешних сервисов

Система настроена для мониторинга внешних сервисов на хосте `192.168.14.80`:
- PostgreSQL (порт 5432)
- Backend JMX (порт 7777)
- Backend Actuator (порт 7778)
- Hello JMX (порт 8888)
- Telegraf (порт 9273)

## Troubleshooting

### Проверка статуса сервисов
```bash
docker-compose ps
docker-compose logs [service_name]
```

### Проверка метрик
```bash
# Prometheus targets
curl http://localhost:9090/api/v1/targets

# Telegraf metrics
curl http://localhost:9273/metrics

# JMX metrics
curl http://localhost:8888/metrics
```

### Перезапуск сервисов
```bash
docker-compose restart [service_name]
```

## Расширение системы

Для добавления новых сервисов мониторинга:
1. Добавьте новый job в `prometheus.yml`
2. Настройте экспортер метрик в целевом сервисе
3. Обновите конфигурацию Docker Compose
4. Создайте дашборды в Grafana

## Backup и восстановление

### Важные директории для backup:
- `/home/user01/grafana/data` - данные Grafana
- `/home/user01/influxdb` - данные InfluxDB
- `/home/user01/prometheus` - конфигурация Prometheus
- Docker volumes: `prometheus_data`

### Создание backup:
```bash
docker-compose down
tar -czf monitoring-backup-$(date +%Y%m%d).tar.gz \
  /home/user01/grafana/data \
  /home/user01/influxdb \
  /home/user01/prometheus
```