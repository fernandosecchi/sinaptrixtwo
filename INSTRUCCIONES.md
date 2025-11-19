# INSTRUCCIONES.md

## 📋 Guía de Desarrollo - SinaptrixTwo

### 🚀 Inicio Rápido

#### Ejecutar la aplicación
```bash
# Con Docker (recomendado)
./scripts/start-docker.sh
# o
docker-compose up -d

# Verificar estado
docker-compose ps
docker-compose logs -f
```

#### URLs de acceso
- **Aplicación**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **PostgreSQL**: localhost:5432

### 🏗️ Estructura del Proyecto

```
src/
├── main.py           # Punto de entrada (FastAPI + NiceGUI)
├── database.py       # Configuración async SQLAlchemy
├── models.py         # Modelos de base de datos
└── ui/              
    ├── layouts.py    # Layout compartido para todas las páginas
    └── pages/        # Páginas de la aplicación
        ├── home.py   # Página de inicio
        └── users.py  # Gestión de usuarios
```

### 📝 Cómo Agregar una Nueva Página

#### 1. Crear el archivo de la página
```python
# src/ui/pages/mi_pagina.py
from nicegui import ui
from src.ui.layouts import theme_layout

def create_mi_pagina():
    """Register the new page route."""
    
    @ui.page("/mi-ruta")
    def mi_pagina():
        with theme_layout('Título de Mi Página'):
            # Contenido de tu página
            ui.label('Contenido aquí')
```

#### 2. Registrar la página en main.py
```python
# src/main.py
from src.ui.pages.mi_pagina import create_mi_pagina

def init_nicegui():
    create_home_page()
    create_users_page()
    create_mi_pagina()  # Agregar aquí
```

#### 3. Actualizar la navegación
```python
# src/ui/layouts.py
# En la sección del drawer, agregar:
ui.link('Mi Página', '/mi-ruta').classes('w-full p-4 hover:bg-slate-200 text-slate-800 no-underline')
```

### 🗃️ Trabajar con la Base de Datos

#### Crear un nuevo modelo
```python
# src/models.py
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)
```

#### Crear y aplicar migraciones
```bash
# Generar migración
docker-compose exec app poetry run alembic revision --autogenerate -m "Add products table"

# Aplicar migraciones
docker-compose exec app poetry run alembic upgrade head

# Ver estado actual
docker-compose exec app poetry run alembic current
```

#### Usar el modelo en una página
```python
from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models import Product

async def load_products():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
    return products
```

### 🎨 Componentes UI Comunes

#### Formulario con validación
```python
name_input = ui.input('Nombre').props('outlined dense')
email_input = ui.input('Email').props('outlined dense')

async def submit():
    if not name_input.value:
        ui.notify('Campo requerido', type='warning')
        return
    # Procesar...
    
ui.button('Enviar', on_click=submit).props('color=primary')
```

#### Tabla interactiva
```python
columns = [
    {'name': 'id', 'label': 'ID', 'field': 'id'},
    {'name': 'name', 'label': 'Nombre', 'field': 'name'},
]

rows = [
    {'id': 1, 'name': 'Item 1'},
    {'id': 2, 'name': 'Item 2'},
]

table = ui.table(columns=columns, rows=rows, row_key='id')
```

#### Notificaciones
```python
ui.notify('Mensaje de éxito', type='positive')
ui.notify('Advertencia', type='warning')
ui.notify('Error', type='negative')
ui.notify('Información', type='info')
```

### 🛠️ Comandos Útiles

#### Docker
```bash
# Ver logs
docker-compose logs -f app

# Ejecutar comando en contenedor
docker-compose exec app bash

# Reiniciar aplicación
docker-compose restart app

# Detener todo
docker-compose down

# Limpiar y reconstruir
docker-compose down -v
docker-compose up --build -d
```

#### Base de datos
```bash
# Acceder a PostgreSQL
docker-compose exec db psql -U postgres -d sinaptrixtwo

# Ver tablas
docker-compose exec db psql -U postgres -d sinaptrixtwo -c "\dt"

# Hacer backup
docker-compose exec db pg_dump -U postgres sinaptrixtwo > backup.sql
```

### 🐛 Solución de Problemas

#### La tabla no existe
```bash
# Verificar migraciones
docker-compose exec app poetry run alembic current

# Aplicar migraciones pendientes
docker-compose exec app poetry run alembic upgrade head
```

#### Cambios no se reflejan
```bash
# Reiniciar la aplicación
docker-compose restart app

# Si es necesario, reconstruir
docker-compose up --build -d
```

#### Puerto en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

### 📚 Patrones y Mejores Prácticas

1. **Separación de responsabilidades**: Mantén la lógica de UI separada de la lógica de negocio
2. **Async/Await**: Usa funciones asíncronas para operaciones de base de datos
3. **Context Managers**: Usa `async with AsyncSessionLocal()` para manejar sesiones
4. **Validación**: Siempre valida inputs antes de procesar
5. **Feedback al usuario**: Usa `ui.notify()` para informar acciones
6. **Layout consistente**: Usa `theme_layout` en todas las páginas

### 🔒 Seguridad

⚠️ **Antes de producción:**
1. Cambiar `storage_secret` en `main.py`
2. Usar variables de entorno para credenciales
3. No commitear `.env` con datos sensibles
4. Configurar HTTPS
5. Implementar autenticación y autorización

### 📖 Referencias

- [NiceGUI Documentation](https://nicegui.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

*Última actualización: Noviembre 2024*