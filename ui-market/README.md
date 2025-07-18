# External Aries - JALM Market Place UI

Веб-интерфейс маркетплейса для JALM Full Stack - современный React приложение для управления и мониторинга всей экосистемы.

## 🎯 Функциональность

### Основные возможности:
- **Dashboard** - мониторинг всех сервисов и компонентов
- **Marketplace** - каталог готовых решений и шаблонов
- **Research Analytics** - визуализация данных Research Layer
- **Service Management** - управление JALM сервисами
- **Deployment** - развертывание новых продуктов
- **Monitoring** - мониторинг производительности

### Технический стек:
- **Frontend:** React 18 + TypeScript
- **Styling:** Tailwind CSS + Headless UI
- **State Management:** Zustand
- **Charts:** Recharts
- **API Client:** Axios
- **Build Tool:** Vite
- **Package Manager:** npm

## 🚀 Быстрый старт

### Установка зависимостей:
```bash
cd ui-market
npm install
```

### Запуск в режиме разработки:
```bash
npm run dev
```

### Сборка для продакшена:
```bash
npm run build
```

### Предварительный просмотр сборки:
```bash
npm run preview
```

## 📁 Структура проекта

```
ui-market/
├── public/                 # Статические файлы
├── src/
│   ├── components/         # React компоненты
│   │   ├── common/        # Общие компоненты
│   │   ├── dashboard/     # Компоненты дашборда
│   │   ├── marketplace/   # Компоненты маркетплейса
│   │   └── monitoring/    # Компоненты мониторинга
│   ├── pages/             # Страницы приложения
│   ├── hooks/             # React хуки
│   ├── services/          # API сервисы
│   ├── stores/            # Zustand сторы
│   ├── types/             # TypeScript типы
│   ├── utils/             # Утилиты
│   └── App.tsx            # Главный компонент
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## 🔧 Конфигурация

### Переменные окружения:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_RESEARCH_API_URL=http://localhost:8080
VITE_TULA_SPEC_URL=http://localhost:8001
VITE_SHABLON_SPEC_URL=http://localhost:8002
```

### Настройка API endpoints:
- Core Runner: `http://localhost:8000`
- Research API: `http://localhost:8080`
- Tula Spec: `http://localhost:8001`
- Shablon Spec: `http://localhost:8002`

## 📊 Компоненты интерфейса

### 1. Dashboard
- Обзор всех сервисов
- Статистика использования
- Быстрые действия
- Уведомления

### 2. Marketplace
- Каталог шаблонов
- Каталог функций
- Поиск и фильтрация
- Детальная информация

### 3. Research Analytics
- Визуализация собранных данных
- Анализ паттернов
- Графики и диаграммы
- Экспорт отчетов

### 4. Service Management
- Управление сервисами
- Мониторинг состояния
- Логи и метрики
- Конфигурация

### 5. Deployment
- Создание новых продуктов
- Выбор шаблонов
- Настройка параметров
- Отслеживание процесса

## 🎨 Дизайн система

### Цветовая палитра:
- Primary: `#3B82F6` (Blue)
- Secondary: `#10B981` (Green)
- Warning: `#F59E0B` (Yellow)
- Error: `#EF4444` (Red)
- Success: `#10B981` (Green)

### Типографика:
- Font Family: Inter
- Headings: 24px, 20px, 18px, 16px
- Body: 14px, 12px

### Компоненты:
- Buttons: Primary, Secondary, Ghost
- Cards: Default, Elevated, Interactive
- Forms: Input, Select, Checkbox, Radio
- Navigation: Sidebar, Breadcrumbs, Tabs

## 🔌 Интеграция с JALM

### API интеграция:
```typescript
// Пример использования API
import { jalmApi } from '@/services/api'

// Получение статуса сервисов
const services = await jalmApi.getServices()

// Создание нового продукта
const product = await jalmApi.createProduct({
  template: 'booking_light',
  name: 'My Booking App',
  config: { /* ... */ }
})
```

### WebSocket для real-time обновлений:
```typescript
// Подписка на обновления
jalmApi.subscribeToUpdates((update) => {
  console.log('Service update:', update)
})
```

## 🧪 Тестирование

### Запуск тестов:
```bash
npm run test
```

### Тестирование компонентов:
```bash
npm run test:components
```

### E2E тестирование:
```bash
npm run test:e2e
```

## 📦 Деплой

### Docker:
```bash
docker build -t jalm-ui-market .
docker run -p 3000:3000 jalm-ui-market
```

### Docker Compose:
```bash
docker-compose up ui-market
```

## 🔒 Безопасность

- CORS настройки
- API ключи
- Аутентификация
- Авторизация
- Валидация данных

## 📈 Производительность

- Code splitting
- Lazy loading
- Memoization
- Bundle optimization
- CDN для статических файлов

## 🤝 Разработка

### Git workflow:
1. Создание feature ветки
2. Разработка функциональности
3. Тестирование
4. Code review
5. Merge в main

### Code style:
- ESLint + Prettier
- TypeScript strict mode
- Component documentation
- Unit tests для критических функций

## 📞 Поддержка

- Документация API
- Примеры использования
- Troubleshooting guide
- Community forum

---

**Версия:** 1.0.0  
**Статус:** В разработке  
**Готовность:** 0% (начальная стадия) 