# 🏗️ Arquitectura de SinaptrixTwo

## 📁 Estructura del Proyecto

```
src/
├── config/               # Configuración y variables de entorno
│   ├── __init__.py
│   └── settings.py       # Configuración centralizada
│
├── models/              # Modelos de base de datos (Entidades)
│   ├── __init__.py
│   ├── base.py         # Clase base y mixins
│   ├── enums.py        # Enumeraciones
│   ├── user.py         # Modelo Usuario
│   └── lead.py         # Modelo Lead
│
├── repositories/        # Capa de acceso a datos
│   ├── __init__.py
│   ├── base.py         # Repositorio base con CRUD
│   ├── user_repository.py
│   └── lead_repository.py
│
├── services/           # Lógica de negocio
│   ├── __init__.py
│   ├── user_service.py
│   └── lead_service.py
│
├── schemas/            # DTOs y validación (Pydantic)
│   ├── __init__.py
│   ├── user.py
│   └── lead.py
│
├── ui/                 # Capa de presentación (NiceGUI)
│   ├── layouts.py      # Layouts compartidos
│   └── pages/          # Páginas de la aplicación
│       ├── home.py
│       ├── users.py
│       └── leads.py
│
├── utils/              # Utilidades y helpers
│   ├── __init__.py
│   └── validators.py
│
├── database.py         # Configuración de base de datos
└── main.py            # Punto de entrada de la aplicación
```

## 🔄 Flujo de Datos

```
UI (NiceGUI) 
    ↓↑
Services (Lógica de Negocio)
    ↓↑
Repositories (Acceso a Datos)
    ↓↑
Database (PostgreSQL)
```

## 📋 Capas de la Arquitectura

### 1. **Capa de Presentación (UI)**
- **Ubicación**: `src/ui/`
- **Responsabilidad**: Interfaz de usuario, manejo de eventos
- **Tecnología**: NiceGUI
- **Principio**: No contiene lógica de negocio

### 2. **Capa de Servicios**
- **Ubicación**: `src/services/`
- **Responsabilidad**: Lógica de negocio, validaciones, orquestación
- **Principio**: Independiente de la UI y la base de datos
- **Ejemplo**:
```python
class UserService:
    async def create_user(self, data):
        # Validación
        # Lógica de negocio
        # Llamada al repositorio
        return user
```

### 3. **Capa de Repositorios**
- **Ubicación**: `src/repositories/`
- **Responsabilidad**: Acceso a datos, queries SQL
- **Principio**: Abstrae la base de datos
- **Patrón**: Repository Pattern
- **Ejemplo**:
```python
class UserRepository(BaseRepository):
    async def get_by_email(self, email):
        # Query específico
        return user
```

### 4. **Capa de Modelos**
- **Ubicación**: `src/models/`
- **Responsabilidad**: Definición de entidades
- **Tecnología**: SQLAlchemy ORM
- **Principio**: POCO (Plain Old Class Objects)

### 5. **Capa de Configuración**
- **Ubicación**: `src/config/`
- **Responsabilidad**: Gestión de configuración y variables de entorno
- **Principio**: Configuración centralizada

## 🎯 Patrones de Diseño

### Repository Pattern
```python
# Base repository con operaciones CRUD genéricas
class BaseRepository(Generic[T]):
    async def get(self, id: int) -> Optional[T]
    async def get_all(self) -> List[T]
    async def create(self, **kwargs) -> T
    async def update(self, id: int, **kwargs) -> T
    async def delete(self, id: int) -> bool
```

### Service Layer Pattern
```python
# Servicios con lógica de negocio
class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
    
    async def business_operation(self):
        # Lógica compleja aquí
```

### Dependency Injection
```python
# Inyección de dependencias mediante constructores
async with AsyncSessionLocal() as session:
    service = UserService(session)
    result = await service.operation()
```

## 🔧 Ventajas de esta Arquitectura

1. **Separación de Responsabilidades**: Cada capa tiene una función específica
2. **Testabilidad**: Fácil de crear tests unitarios por capa
3. **Escalabilidad**: Agregar nuevas funcionalidades es sencillo
4. **Mantenibilidad**: Código organizado y fácil de mantener
5. **Reutilización**: Componentes reutilizables entre módulos
6. **Flexibilidad**: Cambiar tecnologías sin afectar otras capas

## 🚀 Cómo Extender

### Agregar un Nuevo Modelo
1. Crear archivo en `src/models/nuevo_modelo.py`
2. Heredar de `Base`
3. Exportar en `src/models/__init__.py`
4. Crear migración con Alembic

### Agregar un Nuevo Servicio
1. Crear archivo en `src/services/nuevo_service.py`
2. Crear repositorio correspondiente
3. Implementar lógica de negocio
4. Usar en las páginas UI

### Agregar una Nueva Página
1. Crear archivo en `src/ui/pages/nueva_pagina.py`
2. Usar `theme_layout` para consistencia
3. Consumir servicios necesarios
4. Registrar en `main.py`

## 📊 Diagrama de Componentes

```
┌─────────────────────────────────────────────────┐
│                   UI Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   Home   │  │  Users   │  │  Leads   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│                Service Layer                     │
│  ┌──────────────┐        ┌──────────────┐      │
│  │ UserService  │        │ LeadService  │      │
│  └──────────────┘        └──────────────┘      │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│              Repository Layer                    │
│  ┌──────────────┐        ┌──────────────┐      │
│  │UserRepository│        │LeadRepository│      │
│  └──────────────┘        └──────────────┘      │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│                  Database                        │
│                 PostgreSQL                       │
└─────────────────────────────────────────────────┘
```

## 🔒 Mejores Prácticas

1. **No mezclar capas**: La UI no debe acceder directamente a repositorios
2. **Validación en servicios**: Toda validación de negocio en la capa de servicios
3. **DTOs para transferencia**: Usar schemas/DTOs entre capas
4. **Transacciones en servicios**: Manejar transacciones en la capa de servicios
5. **Logs por capa**: Implementar logging específico por capa
6. **Manejo de errores**: Excepciones personalizadas por capa

---

Esta arquitectura permite un crecimiento ordenado y mantenible del sistema.