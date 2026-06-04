# CSS Кастомизация для Jobly Allauth шаблонов

Здесь приведены примеры, как изменять дизайн страниц авторизации.

## 📝 Способ 1: Прямое редактирование в base.html

Откройте [templates/allauth/base.html](templates/allauth/base.html) и найдите блок `<style>`.

### Изменить цвета градиента

```css
/* ДО */
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* ПОСЛЕ - сине-зеленый градиент */
body {
    background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
}

/* ИЛИ - оранжево-красный */
body {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
}
```

### Изменить размер и форму карточки

```css
.auth-card {
    border-radius: 16px;  /* Скругление углов */
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);  /* Тень */
}

/* Сделать более скругленной */
.auth-card {
    border-radius: 24px;
    box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4);
}

/* Сделать плоской */
.auth-card {
    border-radius: 8px;
    box-shadow: none;
    border: 1px solid #ddd;
}
```

### Изменить шрифты и размеры текста

```css
/* Заголовок */
.auth-header h1 {
    font-size: 32px;  /* Измените здесь */
    font-weight: 700;
}

/* Кнопки */
.btn-primary-auth {
    font-size: 15px;
    font-weight: 600;
    text-transform: uppercase;  /* Прописные буквы */
}

/* Убрать text-transform для кнопок */
.btn-primary-auth {
    text-transform: none;
}
```

### Изменить цвета кнопок

```css
/* Текущие цвета кнопки */
.btn-primary-auth {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

/* Зеленая кнопка */
.btn-primary-auth {
    background: linear-gradient(135deg, #00d084 0%, #00b050 100%);
}

/* Синяя кнопка */
.btn-primary-auth {
    background: linear-gradient(135deg, #0066ff 0%, #0052cc 100%);
}

/* Черная кнопка */
.btn-primary-auth {
    background: linear-gradient(135deg, #333 0%, #000 100%);
}
```

## 📝 Способ 2: Создать отдельный CSS файл

1. Создайте файл `static/css/jobly_allauth.css`:

```css
/* static/css/jobly_allauth.css */

/* Основные цвета Jobly */
:root {
    --jobly-primary: #667eea;
    --jobly-secondary: #764ba2;
    --jobly-success: #00d084;
    --jobly-danger: #ff6b6b;
    --jobly-text: #333;
    --jobly-text-light: #666;
    --jobly-border: #e0e0e0;
}

/* Переопределить стили */
body {
    background: linear-gradient(135deg, var(--jobly-primary) 0%, var(--jobly-secondary) 100%);
}

.auth-card {
    border-radius: 20px;
    box-shadow: 0 25px 70px rgba(0, 0, 0, 0.35);
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.auth-header {
    background: linear-gradient(135deg, var(--jobly-primary) 0%, var(--jobly-secondary) 100%);
    padding: 50px 20px;
    text-align: center;
}

.btn-primary-auth {
    background: linear-gradient(135deg, var(--jobly-primary) 0%, var(--jobly-secondary) 100%);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary-auth:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
}

/* Темная тема */
@media (prefers-color-scheme: dark) {
    body {
        background: linear-gradient(135deg, #3a4575 0%, #4a3a5a 100%);
    }
    
    .auth-card {
        background: #2a2a3e;
        color: #e0e0e0;
    }
    
    .form-control {
        background: #1a1a2e;
        border-color: #404060;
        color: #e0e0e0;
    }
}
```

2. Добавьте линк в `templates/allauth/base.html`:

```html
{% load static %}
<!-- ... в блок <head> ... -->
<link rel="stylesheet" href="{% static 'css/jobly_allauth.css' %}">
```

## 🎨 Готовые цветовые схемы

### Минималистичная (серая)

```css
body {
    background: #f5f5f5;
}

.auth-card {
    background: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-radius: 12px;
}

.btn-primary-auth {
    background: #333;
    color: white;
}
```

### Яркая (оранжево-желтая)

```css
body {
    background: linear-gradient(135deg, #ff9a56 0%, #ff6b6b 100%);
}

.auth-header {
    background: linear-gradient(135deg, #ff9a56 0%, #ff6b6b 100%);
}

.btn-primary-auth {
    background: linear-gradient(135deg, #ff9a56 0%, #ff6b6b 100%);
}
```

### Благородная (темная синяя)

```css
body {
    background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
}

.auth-header {
    background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
}

.btn-primary-auth {
    background: #1a237e;
}

.auth-card {
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
}
```

### Природная (зелено-голубая)

```css
body {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.auth-header {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.btn-primary-auth {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}
```

## 📱 Адаптивный дизайн для мобильных

```css
/* Экраны меньше 480px */
@media (max-width: 480px) {
    .auth-container {
        padding: 10px;
    }
    
    .auth-card {
        border-radius: 12px;
    }
    
    .auth-header {
        padding: 30px 15px;
    }
    
    .auth-header h1 {
        font-size: 24px;
    }
    
    .auth-content {
        padding: 25px;
    }
    
    .btn-primary-auth {
        padding: 11px 14px;
        font-size: 14px;
    }
}
```

## 🌙 Темная тема

```css
/* Добавить в base.html */
@media (prefers-color-scheme: dark) {
    body {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .auth-card {
        background: #0f3460;
        color: #eee;
    }
    
    .auth-header {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    }
    
    .form-control {
        background: #1a1a2e;
        border-color: #2d3f5f;
        color: #eee;
    }
    
    .form-label {
        color: #ccc;
    }
    
    .auth-footer {
        border-top-color: #2d3f5f;
        color: #999;
    }
    
    .auth-footer a {
        color: #66b3ff;
    }
}
```

## 🎯 Кастомные стили для элементов

### Переопределить стиль Google кнопки

```css
.btn-google {
    background: white;
    border: 2px solid #ddd;
    color: #333;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.btn-google:hover {
    border-color: #4285f4;
    background: #f8f9fa;
}
```

### Кастомный стиль инпутов формы

```css
.form-control {
    border: 2px solid transparent;
    border-radius: 10px;
    padding: 13px 16px;
    font-size: 15px;
    transition: all 0.3s ease;
}

.form-control:focus {
    border-color: var(--jobly-primary);
    box-shadow: 0 0 0 0.3rem rgba(102, 126, 234, 0.2);
}

.form-control::placeholder {
    color: #ccc;
}
```

### Стиль ошибок

```css
.errorlist {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 12px;
    color: #856404;
}

.errorlist li {
    margin: 5px 0;
}
```

## 🎬 Анимации и переходы

```css
/* Плавное появление */
@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.auth-container {
    animation: fadeIn 0.5s ease-in;
}

/* Масштабирование при наведении */
.btn-primary-auth {
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.btn-primary-auth:hover {
    transform: scale(1.02);
}

/* Шейк эффект для ошибок */
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-10px); }
    75% { transform: translateX(10px); }
}

.errorlist {
    animation: shake 0.5s ease-in-out;
}
```

## 📚 Дополнительные ресурсы

- [Bootstrap 5 Docs](https://getbootstrap.com/docs/5.0/)
- [CSS Gradients](https://cssgradient.io/)
- [Font Awesome Icons](https://fontawesome.com/)
- [Cubic Bezier Animations](https://cubic-bezier.com/)
