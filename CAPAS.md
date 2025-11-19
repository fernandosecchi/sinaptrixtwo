# 📚 Arquitectura en Capas - Explicación Completa

## ¿Por qué estas capas?

### 1. **Schemas (Pydantic) - Validación y Serialización**
```
src/schemas/
├── user.py     # Schemas para User
└── lead.py     # Schemas para Lead
```

**¿Para qué sirven?**
- **Validación automática** de datos de entrada
- **Serialización** de modelos a JSON
- **Documentación automática** para APIs
- **Type hints** para mejor IDE support

**Ejemplo de uso:**
```python
# Validación automática al recibir datos
lead_data = LeadCreate(
    first_name="Juan",
    last_name="Pérez",
    email="invalid-email"  # ❌ Pydantic lo rechaza
)

# Serialización de modelo a JSON
user = await user_service.get_user(1)
response = UserResponse.model_validate(user)  # ✅ Convierte a schema
```

### 2. **Services - Lógica de Negocio**
```
src/services/
├── user_service.py  # Lógica de usuarios
└── lead_service.py  # Lógica de leads
```

**¿Para qué sirven?**
- **Lógica de negocio** centralizada
- **Validaciones complejas** (más allá de tipos)
- **Orquestación** de múltiples operaciones
- **Transacciones** y manejo de errores

**Ejemplo de uso:**
```python
# Service coordina validación + repositorio + lógica
async def convert_to_client(self, lead_id: int):
    lead = await self.repository.get(lead_id)
    
    # Validación de negocio
    if lead.status == LeadStatus.LOST:
        raise ValueError("No se puede convertir lead perdido")
    
    # Lógica compleja
    if lead.status == LeadStatus.LEAD:
        await self.repository.convert_to_prospect(lead_id)
    
    return await self.repository.convert_to_client(lead_id)
```

### 3. **Repositories - Acceso a Datos**
```
src/repositories/
├── base.py              # CRUD genérico
├── user_repository.py   # Queries específicos User
└── lead_repository.py   # Queries específicos Lead
```

**¿Para qué sirven?**
- **Abstracción** de la base de datos
- **Queries SQL** centralizados
- **Reutilización** de código CRUD
- **Testing** más fácil (mock repositories)

### 4. **Models - Entidades de Dominio**
```
src/models/
├── base.py     # Clase base y mixins
├── user.py     # Tabla users
├── lead.py     # Tabla leads
└── enums.py    # Enumeraciones
```

**¿Para qué sirven?**
- **Mapeo ORM** a tablas de base de datos
- **Definición de estructura** de datos
- **Relaciones** entre entidades
- **Propiedades computadas** (full_name, etc.)

## 🔄 Flujo de Datos Completo

### Crear un Lead (ejemplo)

```
1. UI (leads.py)
   ↓ Recibe datos del formulario
   
2. Schema (LeadCreate)
   ↓ Valida email, teléfono, etc.
   
3. Service (LeadService)
   ↓ Valida lógica de negocio
   ↓ (email no duplicado, etc.)
   
4. Repository (LeadRepository)
   ↓ Ejecuta SQL INSERT
   
5. Model (Lead)
   ↓ ORM crea objeto
   
6. Database (PostgreSQL)
   ✓ Guarda en tabla 'leads'
```

## 🎯 Beneficios de esta Arquitectura

### 1. **Separación de Responsabilidades**
- **UI**: Solo presentación
- **Services**: Solo lógica
- **Repositories**: Solo SQL
- **Models**: Solo estructura

### 2. **Testabilidad**
```python
# Fácil de testear cada capa
def test_user_service():
    mock_repo = Mock(UserRepository)
    service = UserService(mock_repo)
    # Test lógica sin DB
```

### 3. **Mantenibilidad**
- Cambiar UI no afecta lógica
- Cambiar DB no afecta servicios
- Agregar validación es un solo lugar

### 4. **Escalabilidad**
- Agregar API REST es trivial
- Cambiar a GraphQL es posible
- Microservicios en el futuro

## 📊 Comparación: Sin vs Con Arquitectura

### Sin Arquitectura (todo en UI)
```python
# ❌ Malo: Todo mezclado en users.py
async def add_user():
    # Validación
    if not email_input.value:
        ui.notify("Email requerido")
    
    # SQL directo
    async with AsyncSessionLocal() as session:
        user = User(email=email_input.value)
        session.add(user)
        
    # Lógica de negocio
    if check_duplicate_email():
        # ...
```

### Con Arquitectura
```python
# ✅ Bueno: Cada capa su responsabilidad
async def add_user():
    try:
        # UI solo captura
        data = UserCreate(email=email_input.value)
        
        # Service maneja lógica
        user = await user_service.create_user(data)
        
        ui.notify("Usuario creado")
    except ValidationError as e:
        # Manejo limpio de errores
        ui.notify(str(e))
```

## 🚀 Cómo Usar la Arquitectura

### Para agregar una nueva funcionalidad:

1. **Define el Schema** (qué datos necesitas)
2. **Crea el Service** (qué lógica aplicar)  
3. **Extiende Repository** (si necesitas queries especiales)
4. **Actualiza la UI** (usar el service)

### Ejemplo: Agregar "Productos"

```bash
1. src/models/product.py       # Modelo
2. src/schemas/product.py      # Validación
3. src/repositories/product_repository.py  # Queries
4. src/services/product_service.py  # Lógica
5. src/ui/pages/products.py    # Interfaz
```

## ✅ Checklist de Implementación

- [x] **Models**: Separados por entidad
- [x] **Repositories**: Base + específicos
- [x] **Services**: User + Lead
- [x] **Schemas**: Validación con Pydantic
- [x] **Config**: Centralizada
- [x] **UI**: Usa servicios

## 🎓 Conclusión

Esta arquitectura es **profesional** y **escalable**:
- Usada en aplicaciones enterprise
- Facilita el trabajo en equipo
- Permite crecimiento ordenado
- Reduce bugs y duplicación

Cada capa tiene su propósito y todas trabajan juntas para crear una aplicación robusta y mantenible.